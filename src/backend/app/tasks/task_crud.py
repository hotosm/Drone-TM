import uuid
from app.models.enums import HTTPStatus, State
from fastapi import HTTPException
from loguru import logger as log
from psycopg import Connection


async def get_tasks_by_user(user_id: str, db: Connection):
    try:
        query = """WITH task_details AS (
        SELECT
            tasks.id AS task_id,
            ST_Area(ST_Transform(tasks.outline, 4326)) / 1000000 AS task_area,
            task_events.created_at,
            task_events.state
        FROM
            task_events
        JOIN
            tasks ON task_events.task_id = tasks.id
        WHERE
            task_events.user_id = :user_id
        )
        SELECT
            task_details.task_id,
            task_details.task_area,
            task_details.created_at,
            CASE
                WHEN task_details.state = 'REQUEST_FOR_MAPPING' THEN 'ongoing'
                WHEN task_details.state = 'UNLOCKED_DONE' THEN 'completed'
                WHEN task_details.state IN ('UNLOCKED_TO_VALIDATE', 'LOCKED_FOR_VALIDATION') THEN 'mapped'
                ELSE 'unknown'
            END AS state
        FROM task_details
        """
        records = await db.fetch_all(query, values={"user_id": user_id})
        return records

    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Retrieval failed"
        ) from e


async def get_all_tasks(db: Connection, project_id: uuid.UUID):
    query = """
        SELECT id FROM tasks WHERE project_id = :project_id
    """
    values = {"project_id": str(project_id)}

    data = await db.fetch_all(query, values)

    # Extracting the list of IDs from the data
    task_ids = [task["id"] for task in data]

    return task_ids


async def all_tasks_states(db: Connection, project_id: uuid.UUID):
    query = """
        SELECT DISTINCT ON (task_id) project_id, task_id, state
        FROM task_events
        WHERE project_id = :project_id
        ORDER BY task_id, created_at DESC
    """

    r = await db.fetch_all(query, {"project_id": str(project_id)})

    # Extract task_ids and corresponding states from the query result
    existing_tasks = [dict(r) for r in r]

    # Get all task_ids from the tasks table
    task_ids = await get_all_tasks(db, project_id)

    # Create a set of existing task_ids for quick lookup
    existing_task_ids = {task["task_id"] for task in existing_tasks}

    # task ids that are not in task_events table
    remaining_task_ids = [x for x in task_ids if x not in existing_task_ids]

    # Add missing tasks with state as "UNLOCKED_FOR_MAPPING"
    remaining_tasks = [
        {
            "project_id": str(project_id),
            "task_id": task_id,
            "state": State.UNLOCKED_TO_MAP.name,
        }
        for task_id in remaining_task_ids
    ]

    # Combine both existing tasks and remaining tasks
    combined_tasks = existing_tasks + remaining_tasks

    return combined_tasks


async def request_mapping(
    db: Connection,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    user_id: str,
    comment: str,
):
    query = """
            WITH last AS (
                SELECT *
                FROM task_events
                WHERE project_id= :project_id AND task_id= :task_id
                ORDER BY created_at DESC
                LIMIT 1
            ),
            released AS (
                SELECT COUNT(*) = 0 AS no_record
                FROM task_events
                WHERE project_id= :project_id AND task_id= :task_id AND state = :unlocked_to_map_state
            )
            INSERT INTO task_events (event_id, project_id, task_id, user_id, comment, state, created_at)

            SELECT
                gen_random_uuid(),
                :project_id,
                :task_id,
                :user_id,
                :comment,
                :request_for_map_state,
                now()
            FROM last
            RIGHT JOIN released ON true
            WHERE (last.state = :unlocked_to_map_state OR released.no_record = true);
            """

    values = {
        "project_id": str(project_id),
        "task_id": str(task_id),
        "user_id": str(user_id),
        "comment": comment,
        "unlocked_to_map_state": State.UNLOCKED_TO_MAP.name,
        "request_for_map_state": State.REQUEST_FOR_MAPPING.name,
    }

    await db.fetch_one(query, values)

    return {"project_id": project_id, "task_id": task_id, "comment": comment}


async def update_task_state(
    db: Connection,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    user_id: str,
    comment: str,
    initial_state: State,
    final_state: State,
):
    # Update or insert task event
    query = """
        WITH last AS (
            SELECT *
            FROM task_events
            WHERE project_id = :project_id AND task_id = :task_id
            ORDER BY created_at DESC
            LIMIT 1
        ),
        updated AS (
            UPDATE task_events
            SET state = :final_state, comment = :comment, created_at = now()
            WHERE EXISTS (
                SELECT 1
                FROM last
                WHERE user_id = :user_id AND state = :initial_state
            )
            RETURNING project_id, task_id, user_id, state
        )
        INSERT INTO task_events (event_id, project_id, task_id, user_id, state, comment, created_at)
        SELECT gen_random_uuid(), :project_id, :task_id, :user_id, :final_state, :comment, now()
        WHERE NOT EXISTS (
            SELECT 1
            FROM updated
        )
        RETURNING project_id, task_id, user_id, state;
    """

    values = {
        "project_id": str(project_id),
        "task_id": str(task_id),
        "user_id": str(user_id),
        "comment": comment,
        "initial_state": initial_state.name,
        "final_state": final_state.name,
    }

    result = await db.fetch_one(query, values)

    return {
        "project_id": result["project_id"],
        "task_id": result["task_id"],
        "comment": comment,
    }


async def get_requested_user_id(
    db: Connection, project_id: uuid.UUID, task_id: uuid.UUID
):
    query = """
        SELECT user_id
        FROM task_events
        WHERE project_id = :project_id AND task_id = :task_id and state = :request_for_map_state
        ORDER BY created_at DESC
        LIMIT 1
        """
    values = {
        "project_id": str(project_id),
        "task_id": str(task_id),
        "request_for_map_state": State.REQUEST_FOR_MAPPING.name,
    }

    result = await db.fetch_one(query, values)
    if result is None:
        raise ValueError("No user requested for mapping")
    return result["user_id"]


async def get_project_task_by_id(db: Connection, user_id: str):
    """Get a list of pending tasks created by a specific user (project creator)."""
    _sql = """
        SELECT id FROM projects WHERE author_id = :user_id
    """
    project_ids_result = await db.fetch_all(query=_sql, values={"user_id": user_id})
    project_ids = [row["id"] for row in project_ids_result]
    raw_sql = """
        SELECT t.id AS task_id, te.event_id, te.user_id, te.project_id, te.comment, te.state, te.created_at
        FROM tasks t
        LEFT JOIN task_events te ON t.id = te.task_id
        WHERE t.project_id = ANY(:project_ids)
        AND te.state = :state
        ORDER BY t.project_task_index;
    """
    values = {"project_ids": project_ids, "state": "REQUEST_FOR_MAPPING"}
    try:
        db_tasks = await db.fetch_all(query=raw_sql, values=values)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project tasks. {e}",
        )

    return db_tasks

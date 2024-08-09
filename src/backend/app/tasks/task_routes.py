import uuid
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from app.config import settings
from app.models.enums import EventType, State, UserRole
from app.tasks import task_schemas, task_crud
from app.users.user_deps import login_required
from app.users.user_schemas import AuthUser
from app.users.user_deps import get_user_by_id
from psycopg import Connection
from app.db import database
from app.utils import send_notification_email, render_email_template
from app.projects.project_crud import get_project_by_id


router = APIRouter(
    prefix=f"{settings.API_PREFIX}/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[task_schemas.UserTasksStatsOut])
async def list_tasks(
    db: Annotated[Connection, Depends(database.get_db)],
    user_data: Annotated[AuthUser, Depends(login_required)],
):
    """Get all tasks for a drone user."""

    user_id = user_data.id
    return await task_crud.get_tasks_by_user(user_id, db)


@router.get("/states/{project_id}")
async def task_states(
    db: Annotated[Connection, Depends(database.get_db)], project_id: uuid.UUID
):
    """Get all tasks states for a project."""

    return await task_crud.all_tasks_states(db, project_id)


@router.post("/event/{project_id}/{task_id}")
async def new_event(
    db: Annotated[Connection, Depends(database.get_db)],
    background_tasks: BackgroundTasks,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    detail: task_schemas.NewEvent,
    user_data: Annotated[AuthUser, Depends(login_required)],
):
    user_id = user_data.id

    match detail.event:
        case EventType.REQUESTS:
            # TODO: Combine the logic of `update_or_create_task_state` and `request_mapping` functions into a single function if possible. Will do later.
            project = await get_project_by_id(db, project_id)
            if project["requires_approval_from_manager_for_locking"] == "true":
                data = await task_crud.update_or_create_task_state(
                    db,
                    project_id,
                    task_id,
                    user_id,
                    "Request accepted automatically",
                    State.REQUEST_FOR_MAPPING,
                    State.LOCKED_FOR_MAPPING,
                )
            else:
                data = await task_crud.request_mapping(
                    db,
                    project_id,
                    task_id,
                    user_id,
                    "Request for mapping",
                )
                # email notification
                author = await get_user_by_id(db, project.author_id)

                html_content = render_email_template(
                    template_name="mapping_requests.html",
                    context={
                        "name": author.name,
                        "drone_operator_name": user_data.name,
                        "task_id": task_id,
                        "project_name": project.name,
                        "description": project.description,
                    },
                )
                background_tasks.add_task(
                    send_notification_email,
                    user_data.email,
                    "Request for mapping",
                    html_content,
                )
            return data

        case EventType.MAP:
            project = await get_project_by_id(db, project_id)
            if user_id != project.author_id:
                raise HTTPException(
                    status_code=403,
                    detail="Only the project creator can approve the mapping.",
                )

            requested_user_id = await task_crud.get_requested_user_id(
                db, project_id, task_id
            )
            drone_operator = await get_user_by_id(db, requested_user_id)
            html_content = render_email_template(
                template_name="mapping_approved_or_rejected.html",
                context={
                    "email_subject": "Mapping Request Approved",
                    "email_body": "We are pleased to inform you that your mapping request has been approved. Your contribution is invaluable to our efforts in improving humanitarian responses worldwide.",
                    "task_status": "approved",
                    "name": user_data.name,
                    "drone_operator_name": drone_operator.name,
                    "task_id": task_id,
                    "project_name": project.name,
                    "description": project.description,
                },
            )

            background_tasks.add_task(
                send_notification_email,
                drone_operator.email_address,
                "Task is approved",
                html_content,
            )

            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                requested_user_id,
                "Request accepted for mapping",
                State.REQUEST_FOR_MAPPING,
                State.LOCKED_FOR_MAPPING,
            )

        case EventType.REJECTED:
            project = await get_project_by_id(db, project_id)
            if user_id != project.author_id:
                raise HTTPException(
                    status_code=403,
                    detail="Only the project creator can approve the mapping.",
                )

            requested_user_id = await task_crud.get_requested_user_id(
                db, project_id, task_id
            )
            drone_operator = await get_user_by_id(db, requested_user_id)
            html_content = render_email_template(
                template_name="mapping_approved_or_rejected.html",
                context={
                    "email_subject": "Mapping Request Rejected",
                    "email_body": "We are sorry to inform you that your mapping request has been rejected.",
                    "task_status": "rejected",
                    "name": user_data.name,
                    "drone_operator_name": drone_operator.name,
                    "task_id": task_id,
                    "project_name": project.name,
                    "description": project.description,
                },
            )

            background_tasks.add_task(
                send_notification_email,
                drone_operator.email_address,
                "Task is Rejected",
                html_content,
            )

            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                requested_user_id,
                "Request for mapping rejected",
                State.REQUEST_FOR_MAPPING,
                State.UNLOCKED_TO_MAP,
            )
        case EventType.FINISH:
            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                user_id,
                "Done: unlocked to validate",
                State.LOCKED_FOR_MAPPING,
                State.UNLOCKED_TO_VALIDATE,
            )
        case EventType.VALIDATE:
            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                user_id,
                "Done: locked for validation",
                State.UNLOCKED_TO_VALIDATE,
                State.LOCKED_FOR_VALIDATION,
            )
        case EventType.GOOD:
            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                user_id,
                "Done: Task is Good",
                State.LOCKED_FOR_VALIDATION,
                State.UNLOCKED_DONE,
            )

        case EventType.BAD:
            return await task_crud.update_task_state(
                db,
                project_id,
                task_id,
                user_id,
                "Done: needs to redo",
                State.LOCKED_FOR_VALIDATION,
                State.UNLOCKED_TO_MAP,
            )

    return True


@router.get("/requested_tasks/pending")
async def get_pending_tasks(
    db: Annotated[Connection, Depends(database.get_db)],
    user_data: Annotated[AuthUser, Depends(login_required)],
):
    """Get a list of pending tasks for a project creator."""
    user_id = user_data.id
    query = """SELECT role FROM user_profile WHERE user_id = :user_id"""
    records = await db.fetch_all(query, {"user_id": user_id})
    if not records:
        raise HTTPException(status_code=404, detail="User profile not found")

    roles = [record["role"] for record in records]
    if UserRole.PROJECT_CREATOR.name not in roles:
        raise HTTPException(
            status_code=403, detail="Access forbidden for non-Project Creator users"
        )
    pending_tasks = await task_crud.get_project_task_by_id(db, user_id)
    if pending_tasks is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return pending_tasks

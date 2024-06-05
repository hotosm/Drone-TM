from datetime import datetime
from typing import cast
from sqlalchemy import (
    BigInteger,
    Column,
    String,
    Integer,
    ForeignKey,
    ForeignKeyConstraint,
    DateTime,
    SmallInteger,
    Enum,
    Index,
    TIMESTAMP,
    desc,
)

from app.db.database import Base
from geoalchemy2 import Geometry, WKBElement
from app.models.enums import (
    TaskStatus,
    TaskAction,
    TaskSplitType,
    ProjectStatus,
    ProjectVisibility,
    MappingLevel,
    ProjectPriority,
)
from sqlalchemy.orm import (
    object_session,
    relationship,
)
from app.utils import timestamp


class DbUser(Base):
    __tablename__ = "users"

    id = cast(int, Column(BigInteger, primary_key=True))
    username = cast(str, Column(String, unique=True))
    profile_img = cast(str, Column(String))
    name = cast(str, Column(String))
    city = cast(str, Column(String))
    country = cast(str, Column(String))
    email_address = cast(str, Column(String))


class DbOrganisation(Base):
    """Describes an Organisation."""

    __tablename__ = "organisations"

    id = cast(int, Column(Integer, primary_key=True))
    name = cast(str, Column(String(512), nullable=False, unique=True))
    slug = cast(str, Column(String(255), nullable=False, unique=True))
    logo = cast(str, Column(String))  # URL of a logo
    description = cast(str, Column(String))
    url = cast(str, Column(String))


class DbTaskHistory(Base):
    """Describes the history associated with a task."""

    __tablename__ = "task_history"

    id = cast(int, Column(Integer, primary_key=True))
    project_id = cast(int, Column(Integer, ForeignKey("projects.id"), index=True))
    task_id = cast(int, Column(Integer, nullable=False))
    action = cast(TaskAction, Column(Enum(TaskAction), nullable=False))
    action_text = cast(str, Column(String))
    action_date = cast(datetime, Column(DateTime, nullable=False, default=timestamp))
    user_id = cast(
        int,
        Column(
            BigInteger,
            ForeignKey("users.id", name="fk_users"),
            index=True,
            nullable=False,
        ),
    )

    # Define relationships
    user = relationship(DbUser, uselist=False, backref="task_history_user")
    actioned_by = relationship(DbUser, overlaps="task_history_user,user")

    __table_args__ = (
        ForeignKeyConstraint(
            [task_id, project_id], ["tasks.id", "tasks.project_id"], name="fk_tasks"
        ),
        Index("idx_task_history_composite", "task_id", "project_id"),
        Index("idx_task_history_project_id_user_id", "user_id", "project_id"),
        {},
    )


class DbTask(Base):
    """Describes an individual mapping Task."""

    __tablename__ = "tasks"

    # Table has composite PK on (id and project_id)
    id = cast(int, Column(Integer, primary_key=True, autoincrement=True))
    project_id = cast(
        int, Column(Integer, ForeignKey("projects.id"), index=True, primary_key=True)
    )
    project_task_index = cast(int, Column(Integer))
    project_task_name = cast(str, Column(String))
    outline = cast(WKBElement, Column(Geometry("POLYGON", srid=4326)))
    task_status = cast(TaskStatus, Column(Enum(TaskStatus), default=TaskStatus.READY))
    locked_by = cast(
        int,
        Column(BigInteger, ForeignKey("users.id", name="fk_users_locked"), index=True),
    )
    mapped_by = cast(
        int,
        Column(BigInteger, ForeignKey("users.id", name="fk_users_mapper"), index=True),
    )
    validated_by = cast(
        int,
        Column(
            BigInteger, ForeignKey("users.id", name="fk_users_validator"), index=True
        ),
    )

    # Define relationships
    task_history = relationship(
        DbTaskHistory, cascade="all", order_by=desc(DbTaskHistory.action_date)
    )
    lock_holder = relationship(DbUser, foreign_keys=[locked_by])
    mapper = relationship(DbUser, foreign_keys=[mapped_by])


class DbProject(Base):
    """Describes a Mapping Project."""

    __tablename__ = "projects"

    id = cast(int, Column(Integer, primary_key=True))
    name = cast(str, Column(String))
    short_description = cast(str, Column(String))
    description = cast(str, Column(String))
    per_task_instructions = cast(str, Column(String))
    location_str = cast(str, Column(String))
    # created = cast(datetime, Column(DateTime, default=timestamp, nullable=False))
    # last_updated = cast(datetime, Column(DateTime, default=timestamp))
    created = Column(TIMESTAMP(timezone=True), default=timestamp, nullable=False)
    last_updated = Column(
        TIMESTAMP(timezone=True), default=timestamp, onupdate=timestamp
    )

    # GEOMETRY
    outline = cast(WKBElement, Column(Geometry("POLYGON", srid=4326)))
    centroid = cast(WKBElement, Column(Geometry("POINT", srid=4326)))

    organisation_id = cast(
        int,
        Column(
            Integer,
            ForeignKey("organisations.id", name="fk_organisations"),
            index=True,
        ),
    )
    organisation = relationship(DbOrganisation, backref="projects")

    # PROJECT CREATION
    author_id = cast(
        int,
        Column(
            BigInteger,
            ForeignKey("users.id", name="fk_users"),
            nullable=False,
        ),
    )
    author = relationship(DbUser, uselist=False, backref="user")

    # PROJECT STATUS
    status = cast(
        ProjectStatus,
        Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False),
    )
    visibility = cast(
        ProjectVisibility,
        Column(
            Enum(ProjectVisibility), default=ProjectVisibility.PUBLIC, nullable=False
        ),
    )

    mapper_level = cast(
        MappingLevel,
        Column(
            Enum(MappingLevel),
            default=MappingLevel.INTERMEDIATE,
            nullable=False,
            index=True,
        ),
    )

    priority = cast(
        ProjectPriority, Column(Enum(ProjectPriority), default=ProjectPriority.MEDIUM)
    )
    task_split_type = cast(TaskSplitType, Column(Enum(TaskSplitType), nullable=True))
    task_split_dimension = cast(int, Column(SmallInteger, nullable=True))

    # TASKS
    total_tasks = cast(int, Column(Integer))
    tasks = relationship(
        DbTask, backref="projects", cascade="all, delete, delete-orphan"
    )

    __table_args__ = (
        Index("idx_geometry", outline, postgresql_using="gist"),
        {},
    )

    @property
    def tasks_mapped(self):
        """Get the number of tasks mapped for a project."""
        return (
            object_session(self)
            .query(DbTask)
            .filter(DbTask.task_status == TaskStatus.MAPPED)
            .with_parent(self)
            .count()
        )

    @property
    def tasks_validated(self):
        """Get the number of tasks validated for a project."""
        return (
            object_session(self)
            .query(DbTask)
            .filter(DbTask.task_status == TaskStatus.VALIDATED)
            .with_parent(self)
            .count()
        )

    @property
    def tasks_bad(self):
        """Get the number of tasks marked bad for a project."""
        return (
            object_session(self)
            .query(DbTask)
            .filter(DbTask.task_status == TaskStatus.BAD)
            .with_parent(self)
            .count()
        )

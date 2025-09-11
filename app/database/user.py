from sqlmodel import Field, SQLModel, Column, JSON
from sqlalchemy import DateTime, func
from enum import Enum
from datetime import datetime
import uuid

from typing import List


class UserSession(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        index=True,
        primary_key=True,
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )

    xp: int = Field(default=0)
    items: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )

    class Config:
        arbitrary_types_allowed = True


class QuestStatus(str, Enum):
    DONE = "done"
    IN_PROGRESS = "in_progress"


class UserState(SQLModel, table=True):
    __tablename__ = "user_states"
    user: uuid.UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
    )
    quest: str = Field(
        foreign_key="quests.id",
        nullable=False,
    )
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        index=True,
        primary_key=True,
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )
    status: QuestStatus = Field(
        default=QuestStatus.DONE,
    )

from sqlmodel import Field, SQLModel, Column
from sqlalchemy import DateTime, func

from datetime import datetime
import uuid


class UserSession(SQLModel, table=True):
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

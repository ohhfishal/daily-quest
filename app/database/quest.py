import uuid

from dataclasses import dataclass, field

from typing import List


@dataclass
class Item:
    name: str
    description: str = ""


@dataclass
class Reward:
    gold: int = 0
    items: List[Item] = field(default_factory=list)

    def __repr__(self):
        return ",".join(
            [
                string
                for string in [f"{self.gold} gold" if self.gold > 0 else ""]
                + [
                    item.name + (f" ({item.description})" if item.description else "")
                    for item in self.items
                ]
                if string
            ],
        )


@dataclass
class Quest:
    id: uuid.UUID
    # = Field(
    #     default_factory=uuid.uuid4,
    #     index=True,
    #     primary_key=True,
    # )
    title: str
    description: str = ""
    objectives: List[str] = field(default_factory=list)
    reward: Reward = field(default_factory=Reward)


# class UserSession(SQLModel, table=True):
#     id: uuid.UUID = Field(
#         default_factory=uuid.uuid4,
#         index=True,
#         primary_key=True,
#     )
#     created_at: datetime = Field(
#         sa_column=Column(
#             DateTime(timezone=True), server_default=func.now(), nullable=False
#         ),
#     )
#     updated_at: datetime = Field(
#         sa_column=Column(
#             DateTime(timezone=True),
#             server_default=func.now(),
#             onupdate=func.now(),
#             nullable=False,
#         ),
#     )

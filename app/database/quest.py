from sqlmodel import Field, SQLModel, Column, JSON

from enum import Enum
from typing import List
import uuid


class QuestType(str, Enum):
    STORY = "story"
    DAILY = "daily"


class Quest(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        index=True,
        primary_key=True,
    )
    title: str
    objectives: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    quest_type: QuestType = Field(default=QuestType.STORY)

    rewards_gold: int = Field(default=0)
    rewards_items: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Story specific fields
    story_order: int = Field(default=-1, index=True)

    def rewards_string(self):
        return ", ".join(
            [
                string
                for string in [
                    f"{self.rewards_gold} gold" if self.rewards_gold > 0 else ""
                ]
                + self.rewards_items
                if string
            ],
        )


quests = [
    Quest(
        title="It's dangerous to go alone!",
        objectives=["Take this."],
        quest_type=QuestType.STORY,
        story_order=0,
        rewards_items=["The Master Sword"],
    ),
    Quest(
        title="Enter the dragon's lair",
        objectives=["Do something new and uncomfortable."],
        quest_type=QuestType.STORY,
        story_order=430,  # 43th mission
        rewards_gold=100,
    ),
    Quest(
        title="Defeat the dragon",
        objectives=["TODO DECIDE THIS TASK"],
        quest_type=QuestType.STORY,
        story_order=500,  # 0th mission
        rewards_items=["A mysterious orb", "Tomb of Azathoth"],
        rewards_gold=1000,
    ),
]

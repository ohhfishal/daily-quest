from sqlmodel import Field, SQLModel, Column, JSON

from typing import List

import datetime
import json
import logging

logger = logging.getLogger("uvicorn")


DATE_FORMAT = "%Y-%m-%d"


class Quest(SQLModel, table=True):
    id: str = Field(
        index=True,
        primary_key=True,
    )
    release_date: datetime.date = Field(
        index=True,
    )

    title: str
    objectives: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )

    rewards_gold: int = Field(default=0)
    rewards_items: List[str] = Field(default_factory=list, sa_column=Column(JSON))

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


def load_quests(file: str) -> List[Quest]:
    quests = []

    try:
        with open(file, "r") as file:
            # TODO: If the file ever gets big enough stream it
            data = json.load(file)
            for id, metadata in data["quests"].items():
                quest = Quest()

                # Required fields
                quest.id = id
                quest.title = metadata["title"]
                quest.objectives = metadata["objectives"]
                quest.release_date = datetime.datetime.strptime(
                    metadata["release_date"], DATE_FORMAT
                )

                # Optional Fields
                rewards = metadata.get("rewards", {})
                quest.rewards_gold = rewards.get("gold", 0)
                quest.rewards_items = rewards.get("items", [])

                quests.append(quest)
    except FileNotFoundError:
        raise ValueError(f"JSON file {file} not found")
    except ValueError as e:
        raise ValueError(f"Invalid JSON schema: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON formatting: {e}")
    except KeyError as e:
        raise ValueError(f"Missing required field for JSON quests: {e}")
    except Exception as e:
        raise ValueError(f"Unknown error: {e}")
    return quests

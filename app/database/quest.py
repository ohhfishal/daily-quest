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
    title: str
    description: str = ""
    objectives: List[str] = field(default_factory=list)
    reward: Reward = field(default_factory=Reward)

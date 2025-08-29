from dataclasses import dataclass, field
from typing import List

@dataclass
class Reward:
    gold: int = 0
    items: List[str] = field(default_factory=list)

    def __repr__(self):
        return ",".join(
            [item for item in [ 
               f"{self.gold} gold" if self.gold > 0 else "" ] + self.items if item],
        )

@dataclass
class Quest:
    title: str
    description: str = ""
    objectives: List[str] = field(default_factory=list)
    reward: Reward = field(default_factory=Reward)


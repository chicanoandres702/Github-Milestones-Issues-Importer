from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Milestone:
  title: str
  description: str = None
  due_on: str = None
  state: str = "open"
  issues: List["Issue"] = field(default_factory=list)

@dataclass
class Issue:
    title: str
    description: str = None
    overview: str = None
    tasks: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)
    milestone: int = None
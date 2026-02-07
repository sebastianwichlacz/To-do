from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


STATUSES = ["To Do", "In Progress", "Done"]
PRIORITIES = ["Niski", "Średni", "Wysoki"]
PRIORITY_COLORS = {"Niski": "#4CAF50", "Średni": "#FF9800", "Wysoki": "#F44336"}
PRIORITY_ICONS = {"Niski": "🟢", "Średni": "🟡", "Wysoki": "🔴"}


@dataclass
class Task:
    id: int = 0
    title: str = ""
    status: str = "To Do"
    priority: str = "Średni"
    description: str = ""
    deadline: Optional[date] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def is_overdue(self) -> bool:
        if self.deadline and self.status != "Done":
            return self.deadline < date.today()
        return False

    @property
    def priority_icon(self) -> str:
        return PRIORITY_ICONS.get(self.priority, "⚪")

from datetime import date
from .models import Task

LEVEL_WEIGHTS = {"alta": 3, "media": 2, "baja": 1}


def calculate_priority(task: Task, today: date | None = None) -> float:
    today = today or date.today()
    days_remaining = (task.deadline - today).days

    urgency = min(10, max(0, 10 - days_remaining))   # <-- ahora acotado entre 0 y 10
    difficulty_weight = LEVEL_WEIGHTS.get(task.difficulty, 1)
    importance_weight = LEVEL_WEIGHTS.get(task.importance, 1)
    workload_weight = min(task.estimated_hours / 2, 5)

    return round(urgency + difficulty_weight + importance_weight + workload_weight, 2)
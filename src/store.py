from .models import Task


class TaskStore:
    """In-memory storage for academic tasks"""

    def __init__(self):
        self._tasks: dict[str, Task] = {}

    def add(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        return list(self._tasks.values())

    def get_pending(self) -> list[Task]:
        return [t for t in self._tasks.values() if t.status != "completada"]

    def update_status(self, task_id: str, status: str) -> Task | None:
        task = self._tasks.get(task_id)
        if task:
            task.status = status
        return task
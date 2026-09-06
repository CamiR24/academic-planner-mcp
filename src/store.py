import sqlite3
from contextlib import closing
from datetime import date
from .models import Task


class TaskStore:
    """SQLite-backed storage for academic tasks. Same public interface
    as the in-memory version, so the MCP tools don't need to change."""

    def __init__(self, db_path: str = "academic.db"):
        self.db_path = db_path
        self._init_schema()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_schema(self):
        with closing(self._connect()) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    course TEXT NOT NULL,
                    type TEXT NOT NULL,
                    deadline TEXT NOT NULL,
                    estimated_hours REAL NOT NULL,
                    difficulty TEXT NOT NULL,
                    importance TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pendiente'
                )
            """)
            conn.commit()

    def _row_to_task(self, row) -> Task:
        return Task(
            id=row[0], name=row[1], course=row[2], type=row[3],
            deadline=date.fromisoformat(row[4]), estimated_hours=row[5],
            difficulty=row[6], importance=row[7], status=row[8],
        )

    def add(self, task: Task) -> Task:
        with closing(self._connect()) as conn:
            conn.execute(
                """INSERT INTO tasks (id, name, course, type, deadline,
                   estimated_hours, difficulty, importance, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (task.id, task.name, task.course, task.type,
                 task.deadline.isoformat(), task.estimated_hours,
                 task.difficulty, task.importance, task.status),
            )
            conn.commit()
        return task

    def get(self, task_id: str) -> Task | None:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._row_to_task(row) if row else None

    def get_all(self) -> list[Task]:
        with closing(self._connect()) as conn:
            rows = conn.execute("SELECT * FROM tasks").fetchall()
        return [self._row_to_task(r) for r in rows]

    def get_pending(self) -> list[Task]:
        with closing(self._connect()) as conn:
            rows = conn.execute("SELECT * FROM tasks WHERE status != 'completada'").fetchall()
        return [self._row_to_task(r) for r in rows]

    def update_status(self, task_id: str, status: str) -> Task | None:
        with closing(self._connect()) as conn:
            conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
            conn.commit()
        return self.get(task_id)
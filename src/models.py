from dataclasses import dataclass, field
from datetime import date
import uuid


@dataclass
class Task:
    name: str
    course: str
    type: str              # "examen" | "tarea" | "proyecto"
    deadline: date
    estimated_hours: float
    difficulty: str         # "alta" | "media" | "baja"
    importance: str         # "alta" | "media" | "baja"
    status: str = "pendiente"   # "pendiente" | "en_progreso" | "completada"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "course": self.course,
            "type": self.type,
            "deadline": self.deadline.isoformat(),
            "estimated_hours": self.estimated_hours,
            "difficulty": self.difficulty,
            "importance": self.importance,
            "status": self.status,
        }
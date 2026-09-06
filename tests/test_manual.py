from datetime import date
from src.models import Task
from src.store import TaskStore
from src.priority import calculate_priority

store = TaskStore()

t1 = store.add(Task(
    name="Parcial de Redes", course="CC3067", type="examen",
    deadline=date(2026, 9, 10), estimated_hours=4,
    difficulty="alta", importance="alta",
))

t2 = store.add(Task(
    name="Proyecto de Bases de Datos", course="CC3086", type="proyecto",
    deadline=date(2026, 9, 12), estimated_hours=6,
    difficulty="media", importance="alta",
))

for t in store.get_pending():
    score = calculate_priority(t, today=date(2026, 9, 5))
    print(f"{t.name}: priority={score}")
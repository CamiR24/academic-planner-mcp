from datetime import date, timedelta

DEFAULT_PHASES = [
    ("Investigación y planificación", 0.20),
    ("Desarrollo / implementación", 0.50),
    ("Pruebas y revisión", 0.20),
    ("Entrega final y documentación", 0.10),
]


def decompose_project(
    description: str,
    deadline: date,
    estimated_total_hours: float,
    today: date | None = None,
) -> dict:
    today = today or date.today()
    total_days = max((deadline - today).days, 1)

    subtasks = []
    elapsed_fraction = 0.0

    for phase_name, fraction in DEFAULT_PHASES:
        phase_hours = round(estimated_total_hours * fraction, 1)
        elapsed_fraction += fraction
        phase_deadline = today + timedelta(days=round(total_days * elapsed_fraction))

        subtasks.append({
            "name": f"{phase_name}: {description}",
            "estimated_hours": phase_hours,
            "suggested_deadline": phase_deadline.isoformat(),
        })

    return {
        "project": description,
        "final_deadline": deadline.isoformat(),
        "total_estimated_hours": estimated_total_hours,
        "subtasks": subtasks,
    }
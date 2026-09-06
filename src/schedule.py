from datetime import date, timedelta
from .models import Task
from .priority import calculate_priority


def generate_study_schedule(
    tasks: list[Task],
    available_hours_per_day: float,
    days_ahead: int,
    today: date | None = None,
) -> dict:
    today = today or date.today()
    remaining_hours = {t.id: t.estimated_hours for t in tasks}
    schedule = []

    for offset in range(days_ahead):
        current_day = today + timedelta(days=offset)
        budget = available_hours_per_day
        day_allocations = []

        candidates = [
            t for t in tasks
            if remaining_hours[t.id] > 0 and t.deadline >= current_day
        ]

        def sort_key(t: Task):
            days_left = (t.deadline - current_day).days
            #slack = días que le quedan menos los días que necesita para
            days_needed = remaining_hours[t.id] / available_hours_per_day if available_hours_per_day > 0 else float("inf")
            slack = days_left - days_needed
            is_at_risk = slack <= 0
            #primero las que están en riesgo de no completarse (slack <= 0)
            return (not is_at_risk, slack, -calculate_priority(t, today=current_day))

        candidates.sort(key=sort_key)

        for t in candidates:
            if budget <= 0:
                break
            alloc = min(remaining_hours[t.id], budget)
            if alloc <= 0:
                continue
            day_allocations.append({"task": t.name, "hours": round(alloc, 2)})
            remaining_hours[t.id] -= alloc
            budget -= alloc

        schedule.append({
            "date": current_day.isoformat(),
            "allocations": day_allocations,
            "hours_used": round(available_hours_per_day - budget, 2),
        })

    warnings = []
    for t in tasks:
        if remaining_hours[t.id] > 0 and t.deadline <= today + timedelta(days=days_ahead - 1):
            warnings.append(
                f"No se alcanza a completar '{t.name}' antes de su fecha límite "
                f"({t.deadline.isoformat()}); quedan {round(remaining_hours[t.id], 2)}h sin asignar."
            )

    return {"schedule": schedule, "warnings": warnings}
import asyncio
from datetime import date, datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .models import Task
from .store import TaskStore
from .priority import calculate_priority, calculate_priority_breakdown

app = Server("academic-planner")
store = TaskStore()


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add_academic_task",
            description=(
                "Registra una nueva tarea, examen o proyecto académico "
                "con su fecha límite, horas estimadas, dificultad e importancia."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "course": {"type": "string"},
                    "type": {"type": "string", "enum": ["examen", "tarea", "proyecto"]},
                    "deadline": {"type": "string", "description": "Formato YYYY-MM-DD"},
                    "estimated_hours": {"type": "number"},
                    "difficulty": {"type": "string", "enum": ["alta", "media", "baja"]},
                    "importance": {"type": "string", "enum": ["alta", "media", "baja"]},
                },
                "required": ["name", "course", "type", "deadline",
                             "estimated_hours", "difficulty", "importance"],
            },
        ),
        Tool(
            name="get_upcoming_tasks",
            description="Devuelve las tareas pendientes ordenadas por prioridad.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Filtra tareas con deadline dentro de N días (opcional).",
                    }
                },
            },
        ),
                Tool(
            name="update_task_status",
            description="Actualiza el estado de una tarea existente (pendiente, en_progreso, completada).",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["pendiente", "en_progreso", "completada"]},
                },
                "required": ["task_id", "status"],
            },
        ),
        Tool(
            name="calculate_task_priority",
            description=(
                "Calcula el score de prioridad de una tarea específica, "
                "mostrando el desglose de cada componente (urgencia, dificultad, importancia, carga)."
            ),
            inputSchema={
                "type": "object",
                "properties": {"task_id": {"type": "string"}},
                "required": ["task_id"],
            },
        ),
        Tool(
            name="analyze_workload",
            description=(
                "Analiza si hay sobrecarga académica en un período: compara las horas "
                "estimadas de las tareas pendientes en esos días contra las horas disponibles del estudiante."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ahead": {"type": "integer", "description": "Ventana de días a analizar"},
                    "available_hours_per_day": {"type": "number"},
                },
                "required": ["days_ahead", "available_hours_per_day"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "add_academic_task":
        task = Task(
            name=arguments["name"],
            course=arguments["course"],
            type=arguments["type"],
            deadline=date.fromisoformat(arguments["deadline"]),
            estimated_hours=arguments["estimated_hours"],
            difficulty=arguments["difficulty"],
            importance=arguments["importance"],
        )
        store.add(task)
        return [TextContent(type="text", text=f"Tarea creada con id={task.id}")]

    if name == "get_upcoming_tasks":
        days_ahead = arguments.get("days_ahead")
        today = date.today()
        tasks = store.get_pending()

        if days_ahead is not None:
            tasks = [t for t in tasks if (t.deadline - today).days <= days_ahead]

        scored = [(t, calculate_priority(t, today)) for t in tasks]
        scored.sort(key=lambda x: x[1], reverse=True)

        if not scored:
            return [TextContent(type="text", text="No hay tareas pendientes.")]

        lines = [
            f"- {t.name} ({t.course}) | deadline={t.deadline} | priority={score}"
            for t, score in scored
        ]
        return [TextContent(type="text", text="\n".join(lines))]

    if name == "update_task_status":
        task = store.update_status(arguments["task_id"], arguments["status"])
        if task is None:
            return [TextContent(type="text", text=f"No se encontró tarea con id={arguments['task_id']}")]
        return [TextContent(type="text", text=f"Tarea '{task.name}' actualizada a estado: {task.status}")]

    if name == "calculate_task_priority":
        task = store.get(arguments["task_id"])
        if task is None:
            return [TextContent(type="text", text=f"No se encontró tarea con id={arguments['task_id']}")]
        breakdown = calculate_priority_breakdown(task)
        lines = [f"Prioridad de '{task.name}':"]
        lines += [f"  {k}: {v}" for k, v in breakdown.items()]
        return [TextContent(type="text", text="\n".join(lines))]

    if name == "analyze_workload":
        days_ahead = arguments["days_ahead"]
        available_per_day = arguments["available_hours_per_day"]
        today = date.today()

        window_tasks = [
            t for t in store.get_pending()
            if 0 <= (t.deadline - today).days <= days_ahead
        ]
        total_needed = sum(t.estimated_hours for t in window_tasks)
        total_available = available_per_day * days_ahead
        overloaded = total_needed > total_available

        lines = [
            f"Tareas en los próximos {days_ahead} días: {len(window_tasks)}",
            f"Horas estimadas necesarias: {total_needed}",
            f"Horas disponibles en el período: {total_available}",
            f"Estado: {'SOBRECARGA' if overloaded else 'Carga manejable'}",
        ]
        if overloaded:
            lines.append(f"Déficit: {round(total_needed - total_available, 1)} horas")

        return [TextContent(type="text", text="\n".join(lines))]

    raise ValueError(f"Tool desconocida: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
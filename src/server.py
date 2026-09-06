import asyncio
from datetime import date, datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .models import Task
from .store import TaskStore
from .priority import calculate_priority

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

    raise ValueError(f"Tool desconocida: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
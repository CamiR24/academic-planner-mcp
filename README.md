# Academic Planner MCP Server

An MCP (Model Context Protocol) server that provides academic planning
tools to AI assistants and chatbots: task management, priority
calculation, workload analysis, study scheduling, study-technique
recommendations, and project decomposition.

Built for **CC3067 Redes, Project 1** (Universidad del Valle de Guatemala) —
functional requirement #5 (own local MCP server, non-trivial). Scope
approved by the professor beforehand.

This repository is independent and public so other students can install
and use this server from their own MCP host/chatbot.

## Why this isn't trivial

- Full task lifecycle management backed by a real relational schema
  (SQLite), not an in-memory placeholder.
- A custom priority formula combining urgency, difficulty, importance,
  and estimated workload into a single actionable score.
- A scheduling algorithm that distributes available study hours across
  multiple pending tasks day by day, using a **slack-time check** to
  guarantee that tasks close to their deadline are never starved of
  hours in favor of tasks that are merely "more important" but have
  more room to spare.
- Rule-based study-technique recommendation and project decomposition
  into phases with sub-deadlines, requiring the host LLM to combine
  multiple tool calls and reason over structured output to build a
  complete study plan.

## Tools exposed

| Tool | Purpose |
|---|---|
| `add_academic_task` | Register a new task, exam, or project |
| `get_upcoming_tasks` | List pending tasks ordered by priority score |
| `update_task_status` | Update a task's status |
| `calculate_task_priority` | Return the full priority score breakdown for one task |
| `analyze_workload` | Compare hours needed vs. hours available in a date window |
| `generate_study_schedule` | Build a day-by-day study plan across pending tasks |
| `recommend_study_technique` | Recommend a study technique based on content type |
| `decompose_project` | Break a large project into phases with suggested sub-deadlines |

---

### `add_academic_task`

Registers a new academic task, exam, or project.

**Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Task name |
| `course` | string | yes | Course name or code |
| `type` | string | yes | `"examen"` \| `"tarea"` \| `"proyecto"` |
| `deadline` | string | yes | Due date, `YYYY-MM-DD` |
| `estimated_hours` | number | yes | Estimated hours needed |
| `difficulty` | string | yes | `"alta"` \| `"media"` \| `"baja"` |
| `importance` | string | yes | `"alta"` \| `"media"` \| `"baja"` |

**Returns**

Text confirmation including the generated task `id` (UUID), e.g.:
```
Tarea creada con id=e5a56835-6919-4654-8c7e-95cd006121da
```

---

### `get_upcoming_tasks`

Lists pending tasks (status ≠ `completada`), ordered by priority score
(highest first).

**Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `days_ahead` | integer | no | If given, only includes tasks with deadline within N days from today |

**Returns**

A text list, one line per task:
```
- Examen de Redes (CC3067) | deadline=2026-09-10 | priority=14.0
```
Or `"No hay tareas pendientes."` if none match.

---

### `update_task_status`

Updates the status of an existing task.

**Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `task_id` | string | yes | Task UUID (returned by `add_academic_task`) |
| `status` | string | yes | `"pendiente"` \| `"en_progreso"` \| `"completada"` |

**Returns**

Text confirmation, e.g. `"Tarea 'Tarea de Compiladores' actualizada a estado: en_progreso"`,
or an error message if the `task_id` doesn't exist.

---

### `calculate_task_priority`

Returns the full breakdown of the priority score for a single task —
useful for transparency (showing *why* a task scored the way it did).

**Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `task_id` | string | yes | Task UUID |

**Priority formula**

```
priority_score = urgency + difficulty_weight + importance_weight + workload_weight

urgency           = min(10, max(0, 10 - days_remaining))
difficulty_weight = {"alta": 3, "media": 2, "baja": 1}[difficulty]
importance_weight = {"alta": 3, "media": 2, "baja": 1}[importance]
workload_weight   = min(estimated_hours / 2, 5)
```

Score range: 0–21. Higher = more urgent/important.

**Returns**

```
Prioridad de 'Tarea de Compiladores':
  days_remaining: 2
  urgency: 8
  difficulty_weight: 2
  importance_weight: 2
  workload_weight: 1.5
  priority_score: 13.5
```

---

### `analyze_workload`

Compares the hours needed by pending tasks in a date window against the
hours the student says they have available, to flag overload.

**Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `days_ahead` | integer | yes | Size of the window to analyze, in days |
| `available_hours_per_day` | number | yes | Hours the student can dedicate per day |

**Returns**

```
Tareas en los próximos 5 días: 2
Horas estimadas necesarias: 7
Horas disponibles en el período: 10
Estado: ✅ Carga manejable
```
(or `⚠️ SOBRECARGA` plus a `Déficit` line, if hours needed exceed hours available)

---

### `generate_study_schedule`

Distributes the student's available hours across pending tasks, day by
day, for the requested horizon.

**Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `available_hours_per_day` | number | yes | Hours available per day |
| `days_ahead` | integer | yes | Number of days to plan ahead |

**Algorithm**

For each day, candidate tasks (not yet finished, deadline not yet passed)
are ranked by **slack time** first — a task with `slack ≤ 0` (i.e. it
cannot be finished in time at the current pace) is always scheduled
before a task that merely has a higher priority score but more room to
spare. Only once no task is "at risk" does the algorithm fall back to
ranking by the priority formula above.

**Returns**

A day-by-day list plus warnings for any task that will not be finished
before its deadline given the available hours:
```
2026-09-06: Tarea de Compiladores (2h) [total 2h]
2026-09-07: Tarea de Compiladores (1h), Examen de Redes (1h) [total 2h]
2026-09-08: Examen de Redes (2h) [total 2h]
```

---

### `recommend_study_technique`

Recommends a study technique based on the type of content to be
learned.

**Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `content_type` | string | yes | `"memorización"` \| `"conceptual"` \| `"práctico"` |
| `time_available_hours` | number | yes | Hours available for this study session |

**Returns**

```
technique: Repetición espaciada + Active Recall
justification: ...
how_to_apply: ...
time_management_tip: ...
```

---

### `decompose_project`

Breaks a large project into standard phases (research/planning,
development, testing/review, final delivery), with suggested
sub-deadlines distributed proportionally toward the final deadline.

**Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `description` | string | yes | Short project description |
| `deadline` | string | yes | Final due date, `YYYY-MM-DD` |
| `estimated_total_hours` | number | yes | Total estimated hours for the whole project |

**Returns**

```
Proyecto: Proyecto de Compiladores (deadline final: 2026-09-30)
  - Investigación y planificación: 4.0h, sugerido antes de 2026-09-11
  - Desarrollo / implementación: 10.0h, sugerido antes de 2026-09-23
  - Pruebas y revisión: 4.0h, sugerido antes de 2026-09-28
  - Entrega final y documentación: 2.0h, sugerido antes de 2026-09-30
```

---

## Installation

Requires **Python 3.12+**.

```bash
git clone <this-repository-url>
cd academic-planner-mcp

python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration

The server uses a SQLite database (`academic.db`) created automatically
in the project's working directory the first time it runs — no manual
setup required. Data (tasks, statuses) persists across restarts.

No environment variables or API keys are required to run this server —
all logic is local and self-contained.

## Usage

### Standalone (for testing/inspection)

```bash
source venv/bin/activate
python -m src.server
```

This starts the server on stdio. You normally don't run it directly —
an MCP host does, as a subprocess.

### From an MCP host (e.g. your own chatbot, or Claude Desktop)

Point your host's MCP client config at this server. For example, using
the official `mcp` Python SDK:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(
    command="/absolute/path/to/academic-planner-mcp/venv/bin/python",
    args=["-m", "src.server"],
    cwd="/absolute/path/to/academic-planner-mcp",
)

async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool(
            "add_academic_task",
            {
                "name": "Examen de Redes",
                "course": "CC3067",
                "type": "examen",
                "deadline": "2026-09-10",
                "estimated_hours": 4,
                "difficulty": "alta",
                "importance": "alta",
            },
        )
```

For Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "academic-planner": {
      "command": "/absolute/path/to/academic-planner-mcp/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/absolute/path/to/academic-planner-mcp"
    }
  }
}
```

## Usage examples (natural language)

```
"Agrega un examen de Redes para el 10 de septiembre, dificultad alta,
importancia alta, 4 horas estimadas, curso CC3067"
  → add_academic_task

"¿Qué tareas tengo pendientes?"
  → get_upcoming_tasks

"¿Tengo sobrecarga de trabajo en los próximos 5 días con 2 horas
disponibles al día?"
  → analyze_workload

"Genera mi plan de estudio para los próximos 5 días con 2 horas al día"
  → generate_study_schedule

"Necesito estudiar fórmulas para mi examen, tengo 2 horas, ¿qué técnica
me recomiendas?"
  → recommend_study_technique

"Tengo que hacer un proyecto de Compiladores, entrega el 30 de
septiembre, estimo 20 horas totales. Descompónmelo en fases"
  → decompose_project
```

## Project Structure

```
academic-planner-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py                  # MCP server definition and tool handlers
│   ├── models.py                  # Task dataclass
│   ├── store.py                   # SQLite-backed persistence layer
│   ├── priority.py                # Priority formula
│   ├── schedule.py                # Study schedule algorithm (slack-based)
│   ├── study_techniques.py        # Study technique recommendation rules
│   └── project_decomposition.py   # Project phase breakdown logic
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Data

All task data is created by the user through the chatbot at runtime;
this server ships with no pre-seeded data.

## License

MIT.
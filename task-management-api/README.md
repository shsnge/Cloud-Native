# Task Management API

A complete RESTful API for task management built with FastAPI, Neon PostgreSQL, and SQLModel. Includes comprehensive CRUD operations, filtering, search, and statistics.

## Features

- **Full CRUD Operations** - Create, read, update, and delete tasks
- **Advanced Filtering** - Filter by status, priority, assignee
- **Search** - Search tasks by title and description
- **Pagination** - Built-in pagination for large datasets
- **Statistics** - Get task analytics and metrics
- **Tagging** - Organize tasks with tags
- **Assignee Management** - Track task assignments
- **Due Dates** - Track task deadlines
- **Comprehensive Tests** - Full pytest test coverage

## Quick Start

### Prerequisites

- Python 3.11+
- UV package manager
- (Optional) Neon PostgreSQL account

### Installation

```bash
# Navigate to project directory
cd task-management-api

# Install dependencies
uv sync
```

### Running the API

#### Using SQLite (Default - No setup required)

```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

#### Using Neon PostgreSQL

1. Create a free account at [console.neon.tech](https://console.neon.tech/)
2. Create a new project
3. Copy the connection string (use "Psycopg" format)
4. Create a `.env` file:

```env
NEON_DATABASE_URL=postgresql+psycopg://user:password@host/database
```

5. Run the API:

```bash
uv run uvicorn main:app --reload
```

## API Endpoints

### Health Check

- `GET /` - API information
- `GET /health` - Health check

### Task CRUD

- `POST /tasks/` - Create a new task
- `GET /tasks/` - List all tasks (with filtering, search, pagination)
- `GET /tasks/{task_id}` - Get a specific task
- `PATCH /tasks/{task_id}` - Update a task (partial update)
- `DELETE /tasks/{task_id}` - Delete a task
- `PATCH /tasks/{task_id}/status` - Quick status update

### Additional Endpoints

- `GET /tasks/stats` - Task statistics
- `GET /tasks/by-tag/{tag}` - Filter tasks by tag
- `GET /tasks/assignee/{email}` - Get tasks by assignee

## Task Model

```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive docs",
  "status": "todo",
  "priority": "high",
  "due_date": "2026-01-15T10:00:00",
  "tags": ["documentation", "api"],
  "assignee_email": "john@example.com",
  "created_at": "2026-01-10T10:00:00",
  "updated_at": "2026-01-10T10:00:00"
}
```

### Status Values

- `todo` - Task not started
- `in_progress` - Task is being worked on
- `review` - Task under review
- `done` - Task completed
- `cancelled` - Task cancelled

### Priority Values

- `low` - Low priority
- `medium` - Medium priority (default)
- `high` - High priority
- `urgent` - Urgent priority

## Example Usage

### Create a Task

```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete API documentation",
    "description": "Write comprehensive documentation for the task management API",
    "priority": "high",
    "tags": ["documentation", "api"],
    "assignee_email": "john@example.com"
  }'
```

### List Tasks with Filters

```bash
curl "http://localhost:8000/tasks/?status=todo&priority=high&page=1&page_size=10"
```

### Update a Task

```bash
curl -X PATCH "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "description": "Updated description"
  }'
```

### Quick Status Update

```bash
curl -X PATCH "http://localhost:8000/tasks/1/status?new_status=done"
```

### Get Statistics

```bash
curl "http://localhost:8000/tasks/stats"
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest test_tasks.py

# Run specific test
uv run pytest test_tasks.py::test_create_task_full

# Run with coverage
uv run pytest --cov=main --cov-report=html
```

## Test Coverage

The test suite includes:

- **CRUD Operations** - All create, read, update, delete operations
- **Validation Tests** - Input validation and error handling
- **Filtering Tests** - Status, priority, assignee filters
- **Search Tests** - Text search functionality
- **Pagination Tests** - Page navigation
- **Statistics Tests** - Analytics endpoints
- **Integration Tests** - Full lifecycle tests
- **Edge Cases** - Not found, invalid data, etc.

## Project Structure

```
task-management-api/
├── main.py              # FastAPI application and models
├── database.py          # Database configuration
├── pyproject.toml       # Dependencies and config
├── .env                 # Environment variables (create this)
├── .gitignore
├── README.md            # This file
├── test_conftest.py     # Pytest fixtures
└── test_tasks.py        # Comprehensive test suite
```

## Database Schema

### Table: task

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| title | String | Task title (required, max 200 chars) |
| description | String | Task description (optional, max 2000 chars) |
| status | String | Task status (enum) |
| priority | String | Task priority (enum) |
| due_date | DateTime | Due date (optional) |
| tags | Array | List of tags |
| assignee_email | String | Assignee email (optional) |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

## Development

### Adding New Dependencies

```bash
# Add runtime dependency
uv add package-name

# Add dev dependency
uv add --dev package-name
```

### Database Migrations (Optional - with Alembic)

```bash
# Initialize Alembic (first time only)
uv run alembic init alembic

# Create a migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## License

MIT

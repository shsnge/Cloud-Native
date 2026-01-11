"""
Task Management API - Complete CRUD application using FastAPI, SQLModel, and pytest.

Features:
- FastAPI with Depends dependency injection
- SQLModel with Field, Session, create_engine, select
- Single Task model for both database and API
- Complete CRUD operations (Create, Read, Update, Delete)
- Pagination, filtering, and search
- Task statistics
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlmodel import col
from typing import Optional, List
from datetime import datetime
from pydantic import EmailStr, BaseModel
from enum import Enum
from dotenv import load_dotenv

import sys
import os

# from database import get_session, init_db
from database import get_session
from database import engine
# =============================================================================
# Enums for Status and Priority
# =============================================================================

class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


# =============================================================================
# Single Model for both DB and API - SQLModel
# =============================================================================

class Task(SQLModel, table=True):
    """
    Task model - Single model for both database and API.
    SQLModel combines Pydantic (for validation) and SQLAlchemy (for database).
    """
    id: int | None = Field(default=None, primary_key=True)

    # # Title is required and indexed
    title: str = Field(default=None)

    # Optional description
    description: Optional[str] = Field(default=None, max_length=2000)

    # Status with default and index for filtering
    status: TaskStatus = Field(
        default=TaskStatus.todo,
        index=True
    )

    # Priority level
    priority: TaskPriority = Field(
        default=TaskPriority.medium,
        index=True
    )

    # Due date (optional)
    due_date: Optional[datetime] = None

    # Tags stored as comma-separated string (SQLite doesn't have native array type)
    tags: Optional[str] = Field(default=None)

    # Assignee email with validation
    assignee_email: Optional[str] = Field(default=None, index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# create_table()
# =============================================================================
# Pydantic Models for Partial Updates
# =============================================================================

class TaskUpdate(BaseModel):
    """Model for partial updates - all fields optional."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    tags: Optional[str] = None
    assignee_email: Optional[str] = None


# =============================================================================
# Response Models
# =============================================================================

class TaskListResponse(BaseModel):
    """Response model for task list with pagination."""
    tasks: List[Task]
    total: int
    page: int
    page_size: int


class TaskStatsResponse(BaseModel):
    """Response model for task statistics."""
    total: int
    by_status: dict
    by_priority: dict
    overdue: int
    completed_this_week: int


class ApiInfoResponse(BaseModel):
    """Response model for API info."""
    name: str
    version: str
    docs: str
    endpoints: List[str]


# =============================================================================
# Database Table Creation Function
# =============================================================================

def create_tables():
    """
    Database mein SQLModel ke liye table create karta hai.

    Yeh function SQLModel metadata use karke sabhi models ke liye
    tables automatically create kar deta hai. Agar tables pehle se
    exist karti hain toh unhe skip kar deta hai (safe operation).

    Returns:
        None: Tables database mein create ho jati hain
    """
    # from database import engine

    # SQLModel metadata se sabhi tables create karein
    SQLModel.metadata.create_all(engine)
    print("table has been created")

    print("Database tables successfully created!")
    print("- Task table created with all fields")
    print("- Fields: id, title, description, status, priority, due_date, tags, assignee_email, created_at, updated_at")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Task Management API",
    description="Complete CRUD API for task management using FastAPI and SQLModel",
    version="1.0.0"
)


# Initialize database on startup
@app.on_event("startup")
def on_startup():
    """Server start hone par tables create karein."""
    create_tables()


# =============================================================================
# Root & Health Endpoints
# =============================================================================

@app.get("/", response_model=ApiInfoResponse)
def root():
    """Root endpoint with API information."""
    return {
        "name": "Task Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "GET / - API information",
            "GET /health - Health check",
            "GET /tasks/ - List all tasks (with pagination & filters)",
            "POST /tasks/ - Create a new task",
            "GET /tasks/{id} - Get task by ID",
            "PATCH /tasks/{id} - Update task (partial)",
            "DELETE /tasks/{id} - Delete task",
            "GET /tasks/stats - Task statistics",
        ]
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "task-management-api"
    }


# =============================================================================
# CRUD Operations
# =============================================================================

# CREATE - Create a new task
@app.post("/tasks")
def create_task(
    task: Task,
    session: Session = Depends(get_session)
):
    """
    Create a new task.

    Uses:
    - Task model (SQLModel) for both validation and database
    - Session from Depends(get_session) for database access
    - session.add() to insert the task
    - session.commit() to persist changes
    - session.refresh() to get the generated ID
    """
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# READ - List all tasks with pagination and filtering
@app.get("/tasks/", response_model=TaskListResponse)
def list_tasks(
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of tasks per page"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    assignee_email: Optional[str] = Query(None, description="Filter by assignee email")
):
    """
    List all tasks with pagination and filtering.

    Uses:
    - select() to build queries
    - col() for case-insensitive search
    - where() for filtering
    - offset() and limit() for pagination
    - session.exec() to execute the query
    """
    # Start building the query
    statement = select(Task)

    # Apply filters
    if status:
        statement = statement.where(Task.status == status)
    if priority:
        statement = statement.where(Task.priority == priority)
    if assignee_email:
        statement = statement.where(Task.assignee_email == assignee_email)
    if search:
        statement = statement.where(
            (col(Task.title).icontains(search)) |
            (col(Task.description).icontains(search))
        )

    # Get total count before pagination
    count_statement = select(Task)
    if status:
        count_statement = count_statement.where(Task.status == status)
    if priority:
        count_statement = count_statement.where(Task.priority == priority)
    if assignee_email:
        count_statement = count_statement.where(Task.assignee_email == assignee_email)
    if search:
        count_statement = count_statement.where(
            (col(Task.title).icontains(search)) |
            (col(Task.description).icontains(search))
        )

    total = len(session.exec(count_statement).all())

    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    tasks = session.exec(statement).all()

    # Calculate page number
    page = (skip // limit) + 1

    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        page_size=limit
    )


# =============================================================================
# Additional Specific Endpoints (must come before /tasks/{task_id})
# =============================================================================

@app.get("/tasks/stats", response_model=TaskStatsResponse)
def get_task_stats(session: Session = Depends(get_session)):
    """Get task statistics."""
    all_tasks = session.exec(select(Task)).all()

    by_status = {}
    by_priority = {}

    for status in TaskStatus:
        by_status[status.value] = sum(1 for t in all_tasks if t.status == status)

    for priority in TaskPriority:
        by_priority[priority.value] = sum(1 for t in all_tasks if t.priority == priority)

    # Count overdue tasks
    now = datetime.utcnow()
    overdue = sum(1 for t in all_tasks if t.due_date and t.due_date < now and t.status != TaskStatus.done)

    # Count completed this week
    week_ago = now.replace(hour=0, minute=0, second=0, microsecond=0)
    completed_this_week = sum(1 for t in all_tasks if t.status == TaskStatus.done and t.updated_at >= week_ago)

    return TaskStatsResponse(
        total=len(all_tasks),
        by_status=by_status,
        by_priority=by_priority,
        overdue=overdue,
        completed_this_week=completed_this_week
    )


@app.get("/tasks/by-tag/{tag}", response_model=List[Task])
def get_tasks_by_tag(
    tag: str,
    session: Session = Depends(get_session)
):
    """Get all tasks with a specific tag."""
    # Note: This is a simple implementation. For production, you'd want proper JSON querying
    all_tasks = session.exec(select(Task)).all()
    return [t for t in all_tasks if tag in (t.tags or "")]


@app.get("/tasks/assignee/{email}", response_model=List[Task])
def get_tasks_by_assignee(
    email: str,
    session: Session = Depends(get_session)
):
    """Get all tasks assigned to a specific email."""
    statement = select(Task).where(Task.assignee_email == email)
    return session.exec(statement).all()


# =============================================================================
# CRUD Operations (continued)
# =============================================================================

# READ - Get a single task by ID (must come after specific routes)
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID.

    Uses:
    - session.get() to fetch by primary key
    - HTTPException for error handling (404 not found)
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# UPDATE - Partial update of a task
@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """
    Update a task (partial update).

    Uses:
    - session.get() to fetch existing task
    - model_dump() to get update data
    - setattr() to update fields dynamically
    - exclude_unset=True to only update provided fields
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get update data (only fields that were set)
    update_data = task_update.model_dump(exclude_unset=True)

    # Update fields
    for field, value in update_data.items():
        setattr(task, field, value)

    # Update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# Quick status update endpoint
@app.patch("/tasks/{task_id}/status", response_model=Task)
def update_task_status(
    task_id: int,
    new_status: TaskStatus = Query(..., description="New status"),
    session: Session = Depends(get_session)
):
    """Quick endpoint to update only the task status."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = new_status
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# DELETE - Delete a task
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """
    Delete a task.

    Uses:
    - session.get() to fetch the task
    - session.delete() to remove it
    - Returns 204 No Content on success
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return None

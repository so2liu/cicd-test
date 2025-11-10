from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")


class CreateTask(TaskBase):
    pass


class UpdateTask(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None


class Task(TaskBase):
    id: UUID = Field(default_factory=uuid4, description="Task unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Complete FastAPI tutorial",
                "description": "Learn FastAPI basics and best practices",
                "status": "in_progress",
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }


# In-memory storage
tasks_db: dict[UUID, Task] = {}

app = FastAPI(
    title="Task Management API",
    description="A simple task management system built with FastAPI",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Task Management API",
        "version": "1.0.1",
        "docs": "/docs",
        "status": "ok"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "tasks_count": len(tasks_db)
    }


@app.post("/tasks", response_model=Task, status_code=201)
async def create_task(task: CreateTask):
    """Create a new task"""
    new_task = Task(**task.model_dump())
    tasks_db[new_task.id] = new_task
    return new_task


@app.get("/tasks", response_model=list[Task])
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip")
):
    """List all tasks with optional filtering and pagination"""
    all_tasks = list(tasks_db.values())

    # Filter by status if provided
    if status:
        all_tasks = [task for task in all_tasks if task.status == status]

    # Sort by creation time (newest first)
    all_tasks.sort(key=lambda x: x.created_at, reverse=True)

    # Apply pagination
    return all_tasks[offset:offset + limit]


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: UUID):
    """Get a specific task by ID"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return tasks_db[task_id]


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: UUID, task_update: UpdateTask):
    """Update a task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    stored_task = tasks_db[task_id]
    update_data = task_update.model_dump(exclude_unset=True)

    # Update only provided fields
    for field, value in update_data.items():
        setattr(stored_task, field, value)

    stored_task.updated_at = datetime.now()
    tasks_db[task_id] = stored_task
    return stored_task


@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: UUID):
    """Delete a task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    del tasks_db[task_id]
    return None


@app.get("/tasks/stats/summary")
async def get_stats():
    """Get task statistics"""
    total = len(tasks_db)
    if total == 0:
        return {
            "total": 0,
            "by_status": {},
            "message": "No tasks yet"
        }

    stats = {
        "total": total,
        "by_status": {
            TaskStatus.PENDING: 0,
            TaskStatus.IN_PROGRESS: 0,
            TaskStatus.COMPLETED: 0
        }
    }

    for task in tasks_db.values():
        stats["by_status"][task.status] += 1

    return stats


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

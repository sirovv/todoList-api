from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class Task(BaseModel):
    title: str
    description: str
    done: bool
    priority: str

def get_db():
    conn = sqlite3.connect("todos.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def startup():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            done BOOLEAN,
            priority TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.get("/tasks")
def get_tasks(done: bool = None, priority: str = None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if done is not None:
        query += " AND done = ?"
        params.append(int(done))

    if priority:
        query += " AND priority = ?"
        params.append(priority)

    tasks = cursor.execute(query, params).fetchall()
    return [dict(task) for task in tasks]

@app.post("/tasks")
def create_task(task: Task):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, done, priority) VALUES (?, ?, ?, ?)",
        (task.title, task.description, task.done, task.priority)
    )
    conn.commit()
    return {"id": cursor.lastrowid}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET title = ?, description = ?, done = ?, priority = ? WHERE id = ?",
        (task.title, task.description, task.done, task.priority, task_id)
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit()
    return {"message": "Task updated"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    conn.commit()
    return {"message": "Task deleted"}

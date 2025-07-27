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

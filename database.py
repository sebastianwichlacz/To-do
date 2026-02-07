import sqlite3
from pathlib import Path
from models import Task

DB_PATH = Path(__file__).parent / "kanban.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'To Do',
            priority TEXT NOT NULL DEFAULT 'Średni',
            description TEXT DEFAULT '',
            deadline TEXT,
            created_at TEXT NOT NULL
        )
    """)
    # Migracja: category -> description (dla istniejących baz)
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    if "category" in columns and "description" not in columns:
        conn.execute("ALTER TABLE tasks RENAME COLUMN category TO description")
    conn.commit()
    conn.close()


def _row_to_task(row: sqlite3.Row) -> Task:
    from datetime import date as d
    deadline = None
    if row["deadline"]:
        deadline = d.fromisoformat(row["deadline"])
    return Task(
        id=row["id"],
        title=row["title"],
        status=row["status"],
        priority=row["priority"],
        description=row["description"] or "",
        deadline=deadline,
        created_at=row["created_at"],
    )


def get_all_tasks() -> list[Task]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    conn.close()
    return [_row_to_task(r) for r in rows]


def get_tasks_by_status(status: str) -> list[Task]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE status = ? ORDER BY id", (status,)
    ).fetchall()
    conn.close()
    return [_row_to_task(r) for r in rows]


def add_task(task: Task) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO tasks (title, status, priority, description, deadline, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            task.title,
            task.status,
            task.priority,
            task.description,
            task.deadline.isoformat() if task.deadline else None,
            task.created_at,
        ),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id


def update_task_status(task_id: int, new_status: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()


def update_task(task: Task) -> None:
    conn = get_connection()
    conn.execute(
        """UPDATE tasks SET title=?, status=?, priority=?, description=?, deadline=?
           WHERE id=?""",
        (
            task.title,
            task.status,
            task.priority,
            task.description,
            task.deadline.isoformat() if task.deadline else None,
            task.id,
        ),
    )
    conn.commit()
    conn.close()


def delete_task(task_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

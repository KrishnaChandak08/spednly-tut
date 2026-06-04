import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "spendly.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            email    TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title       TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        DATE    NOT NULL,
            notes       TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()

    # Skip seeding if data already exists
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        conn.close()
        return

    conn.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.in", "hashed_password_placeholder"),
    )
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    sample_expenses = [
        (user_id, "Groceries",       1250.00, "Food",          "2026-05-28", "Weekly grocery run"),
        (user_id, "Metro card",       500.00, "Transport",     "2026-05-27", None),
        (user_id, "Netflix",          649.00, "Entertainment", "2026-05-25", "Monthly subscription"),
        (user_id, "Electricity bill", 980.00, "Utilities",     "2026-05-20", "May bill"),
        (user_id, "Lunch",            320.00, "Food",          "2026-05-30", "Office cafeteria"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, title, amount, category, date, notes) VALUES (?,?,?,?,?,?)",
        sample_expenses,
    )

    conn.commit()
    conn.close()

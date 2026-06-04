from database.db import get_db, init_db, seed_db


def test_get_db_returns_row_factory():
    conn = get_db()
    conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                 ("Alice", "alice@test.com", "pw"))
    conn.commit()
    row = conn.execute("SELECT name FROM users").fetchone()
    conn.close()
    assert row["name"] == "Alice"


def test_foreign_keys_enabled():
    conn = get_db()
    result = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    conn.close()
    assert result == 1


def test_init_db_creates_tables():
    conn = get_db()
    tables = {r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    conn.close()
    assert "users" in tables
    assert "expenses" in tables


def test_init_db_idempotent():
    init_db()  # second call — must not raise


def test_seed_db_inserts_data():
    seed_db()
    conn = get_db()
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    expense_count = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    conn.close()
    assert user_count >= 1
    assert expense_count >= 5


def test_seed_db_idempotent():
    seed_db()
    seed_db()  # second call — must not duplicate
    conn = get_db()
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    assert user_count == 1

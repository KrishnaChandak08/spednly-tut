import pytest
import database.db as db_module


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_spendly.db"
    monkeypatch.setattr(db_module, "DB_PATH", str(db_file))
    db_module.init_db()
    yield
    if db_file.exists():
        db_file.unlink()

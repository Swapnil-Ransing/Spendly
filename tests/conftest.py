import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database.db as db

db.DB_PATH = os.path.join(tempfile.mkdtemp(), "test_expense_tracker.db")

import app as flask_app_module


@pytest.fixture
def client():
    flask_app_module.app.config["TESTING"] = True
    with flask_app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_db():
    conn = db.get_db()
    conn.execute("DELETE FROM expenses")
    conn.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    db.seed_db()
    yield

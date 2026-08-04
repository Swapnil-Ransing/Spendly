from werkzeug.security import check_password_hash

import database.db as db


def test_get_register_renders_form(client):
    response = client.get("/register")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert 'name="name"' in body
    assert 'name="email"' in body
    assert 'name="password"' in body
    assert 'name="confirm_password"' in body


def test_post_register_valid_creates_user_and_redirects(client):
    response = client.post(
        "/register",
        data={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "supersecret",
            "confirm_password": "supersecret",
        },
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    conn = db.get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", ("jane@example.com",)
    ).fetchone()
    conn.close()

    assert row is not None
    assert row["name"] == "Jane Doe"
    assert row["password_hash"] != "supersecret"
    assert check_password_hash(row["password_hash"], "supersecret")


def test_post_register_password_mismatch(client):
    response = client.post(
        "/register",
        data={
            "name": "Jane Doe",
            "email": "mismatch@example.com",
            "password": "supersecret",
            "confirm_password": "different",
        },
    )
    assert response.status_code == 200
    assert b"Passwords do not match." in response.data

    conn = db.get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", ("mismatch@example.com",)
    ).fetchone()
    conn.close()
    assert row is None


def test_post_register_duplicate_email(client):
    response = client.post(
        "/register",
        data={
            "name": "Demo Two",
            "email": "demo@spendly.com",
            "password": "supersecret",
            "confirm_password": "supersecret",
        },
    )
    assert response.status_code == 200
    assert b"Email already registered." in response.data

    conn = db.get_db()
    count = conn.execute(
        "SELECT COUNT(*) as c FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()["c"]
    conn.close()
    assert count == 1


def test_post_register_missing_field(client):
    response = client.post(
        "/register",
        data={
            "name": "",
            "email": "missing@example.com",
            "password": "supersecret",
            "confirm_password": "supersecret",
        },
    )
    assert response.status_code == 200
    assert b"All fields are required." in response.data

    conn = db.get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", ("missing@example.com",)
    ).fetchone()
    conn.close()
    assert row is None

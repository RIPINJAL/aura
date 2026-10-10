from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.main import app

client = TestClient(app)


def test_register_login_and_authenticate():
    email = f"{uuid4().hex}@example.com"
    password = "a-strong-test-password"
    registration = client.post("/api/auth/register", json={"email": email, "password": password})

    assert registration.status_code == 201
    body = registration.json()
    assert body["user"]["email"] == email
    assert "hashed_password" not in body["user"]
    assert client.get("/api/tasks").status_code == 401

    token = body["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/auth/me", headers=headers).json()["id"] == body["user"]["id"]
    assert client.get("/api/tasks", headers=headers).status_code == 200

    login = client.post("/api/auth/login", json={"email": email.upper(), "password": password})
    assert login.status_code == 200
    assert login.json()["user"]["id"] == body["user"]["id"]


def test_duplicate_registration_and_invalid_login_are_rejected():
    email = f"{uuid4().hex}@example.com"
    credentials = {"email": email, "password": "another-strong-password"}
    assert client.post("/api/auth/register", json=credentials).status_code == 201
    assert client.post("/api/auth/register", json=credentials).status_code == 409
    assert client.post("/api/auth/login", json={"email": email, "password": "wrong-password"}).status_code == 401


def test_bad_bearer_token_is_rejected():
    response = client.get("/api/tasks", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401


def test_users_cannot_access_each_others_records():
    first_registration = client.post(
        "/api/auth/register",
        json={"email": f"{uuid4().hex}@example.com", "password": "first-user-password"},
    ).json()
    second_registration = client.post(
        "/api/auth/register",
        json={"email": f"{uuid4().hex}@example.com", "password": "second-user-password"},
    ).json()
    first_headers = {"Authorization": f"Bearer {first_registration['access_token']}"}
    second_headers = {"Authorization": f"Bearer {second_registration['access_token']}"}

    task = client.post("/api/tasks", headers=first_headers, json={"title": "Private task"}).json()
    memory = client.post(
        "/api/memory",
        headers=first_headers,
        json={"type": "semantic", "content": "Private memory"},
    ).json()
    document = client.post(
        "/api/documents",
        headers=first_headers,
        json={"title": "Private document", "content": "Private content"},
    ).json()
    approval = client.post(
        "/api/approvals",
        headers=first_headers,
        json={"action": "private_action", "risk_level": 2},
    ).json()

    assert client.get("/api/tasks", headers=second_headers).json() == []
    assert client.get("/api/memory", headers=second_headers).json() == []
    assert client.get("/api/documents", headers=second_headers).json() == []
    assert client.get("/api/approvals", headers=second_headers).json() == []
    assert client.get(f"/api/tasks/{task['id']}", headers=second_headers).status_code == 404
    assert client.get(f"/api/memory/{memory['id']}", headers=second_headers).status_code == 404
    assert client.get(f"/api/documents/{document['id']}", headers=second_headers).status_code == 404
    assert client.post(f"/api/approvals/{approval['id']}/approve", headers=second_headers).status_code == 404


def test_production_settings_reject_placeholder_signing_secret():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="production", secret_key="change-me-in-production")
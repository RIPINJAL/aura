from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        registration = test_client.post(
            "/api/auth/register",
            json={"email": f"{uuid4().hex}@example.com", "password": "test-user-password"},
        )
        assert registration.status_code == 201
        user = registration.json()["user"]
        test_client.headers.update({"Authorization": f"Bearer {registration.json()['access_token']}"})
        test_client.user_id = user["id"]
        yield test_client
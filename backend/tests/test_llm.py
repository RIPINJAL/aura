import json
from unittest.mock import Mock, patch

import httpx
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.memory import Memory


def test_configured_provider_generates_workflow(client, monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.example/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    get_settings.cache_clear()
    provider_response = Mock()
    provider_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "summary": "Prepare for the interview.",
                            "plan": ["Review the role", "Practice examples"],
                            "research": {"summary": "Identify role context.", "findings": ["Confirm the interview format"]},
                            "career": {"summary": "Prepare evidence.", "matched_skills": ["Python"], "gaps": ["Project examples"]},
                            "task_manager": {"summary": "Created focused tasks.", "tasks": ["Prepare two project stories"]},
                        }
                    )
                }
            }
        ]
    }

    try:
        with patch("app.agents.llm.httpx.post", return_value=provider_response) as post:
            response = client.post("/api/agents/run", json={"task": "Prepare for a Python interview"})
    finally:
        get_settings.cache_clear()

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "llm"
    assert body["workflow"]["task_manager"]["tasks"] == ["Prepare two project stories"]
    assert post.call_args.args[0] == "https://llm.example/v1/chat/completions"
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer test-key"


def test_configured_provider_failure_returns_safe_error(client, monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.example/v1")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    get_settings.cache_clear()

    try:
        with patch("app.agents.llm.httpx.post", side_effect=httpx.TimeoutException("private provider detail")):
            response = client.post("/api/agents/run", json={"task": "Prepare for an interview"})
    finally:
        get_settings.cache_clear()

    assert response.status_code == 502
    assert "private provider detail" not in response.text


def test_agent_run_sends_relevant_saved_context_to_provider(client, monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.example/v1")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    get_settings.cache_clear()
    db = SessionLocal()
    relevant_document = Document(
        user_id=client.user_id,
        title="Zircon portfolio notes",
        content="A zircon project used Python for data pipelines.",
        source="portfolio.txt",
    )
    relevant_memory = Memory(
        user_id=client.user_id,
        type="preference",
        content="Zircon is the user's preferred project example.",
    )
    unrelated_document = Document(
        user_id=client.user_id,
        title="Garden journal",
        content="Tomatoes need regular watering.",
        source="garden.txt",
    )
    db.add_all([relevant_document, relevant_memory, unrelated_document])
    db.commit()
    provider_response = Mock()
    provider_response.json.return_value = {
        "choices": [{"message": {"content": json.dumps({
            "summary": "Prepare the portfolio story.",
            "plan": ["Review the zircon project"],
            "research": {"summary": "Review known details.", "findings": ["Project uses Python"]},
            "career": {"summary": "Connect the project to the role.", "matched_skills": ["Python"], "gaps": []},
            "task_manager": {"summary": "Created one task.", "tasks": ["Prepare a project story"]},
        })}}]}

    try:
        with patch("app.agents.llm.httpx.post", return_value=provider_response) as post:
            response = client.post("/api/agents/run", json={"task": "Prepare my zircon Python interview"})
        sent_context = json.loads(post.call_args.kwargs["json"]["messages"][1]["content"])
    finally:
        db.delete(relevant_document)
        db.delete(relevant_memory)
        db.delete(unrelated_document)
        db.commit()
        db.close()
        get_settings.cache_clear()

    assert response.status_code == 200
    assert "Zircon portfolio notes" in sent_context["saved_context"][0]["title"]
    assert any(item["kind"] == "memory" for item in sent_context["saved_context"])
    assert all(item["title"] != "Garden journal" for item in sent_context["saved_context"])
    assert "document: Zircon portfolio notes" in response.json()["context_used"]
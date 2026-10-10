def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_agent_run(client):
    response = client.post("/api/agents/run", json={"task": "Prepare me for tomorrow's interview"})
    assert response.status_code == 200
    body = response.json()
    assert body["agent"] == "supervisor"
    assert "plan" in body
    assert body["mode"] == "demo"


def test_multi_agent_workflow(client):
    response = client.post("/api/agents/run", json={"task": "Prepare me for an AI/ML internship application"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert "workflow" in body
    assert "research" in body["workflow"]
    assert "career" in body["workflow"]
    assert "task_manager" in body["workflow"]
    assert "evaluation" in body
    assert body["evaluation"]["status"] in {"pass", "needs_review"}


def test_memory_and_tool_registry_endpoints(client):
    memory_response = client.post(
        "/api/memory",
        json={"type": "semantic", "content": "User prefers remote AI internships and Python-first roles."},
    )
    assert memory_response.status_code == 201
    assert memory_response.json()["content"]

    memory_list = client.get("/api/memory")
    assert memory_list.status_code == 200
    assert len(memory_list.json()) >= 1

    tool_response = client.get("/api/tools")
    assert tool_response.status_code == 200
    tools = tool_response.json()["tools"]
    assert any(tool["name"] == "search" for tool in tools)
    assert any(tool["name"] == "calendar" for tool in tools)


def test_approval_workflow(client):
    approval_response = client.post(
        "/api/approvals",
        json={
            "action": "submit_application",
            "risk_level": 3,
            "reason": "Submit internship application to company portal.",
        },
    )
    assert approval_response.status_code == 201
    body = approval_response.json()
    assert body["status"] == "pending"
    assert body["requires_approval"] is True

    approval_id = body["id"]
    approve_response = client.post(f"/api/approvals/{approval_id}/approve")
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    approval_list = client.get("/api/approvals")
    assert approval_list.status_code == 200
    assert len(approval_list.json()) >= 1

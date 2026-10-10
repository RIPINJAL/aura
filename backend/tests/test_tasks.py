def test_task_can_be_created_and_marked_complete(client):
    create_response = client.post(
        "/api/tasks",
        json={"title": "Prepare interview notes", "priority": "high"},
    )
    assert create_response.status_code == 201
    task = create_response.json()
    assert task["status"] == "pending"

    update_response = client.patch(
        f"/api/tasks/{task['id']}",
        json={"status": "completed"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "completed"

    list_response = client.get("/api/tasks")
    assert list_response.status_code == 200
    saved_task = next(item for item in list_response.json() if item["id"] == task["id"])
    assert saved_task["status"] == "completed"


def test_task_status_update_rejects_unknown_status(client):
    create_response = client.post("/api/tasks", json={"title": "Validate task status"})
    task_id = create_response.json()["id"]

    response = client.patch(f"/api/tasks/{task_id}", json={"status": "archived"})

    assert response.status_code == 422
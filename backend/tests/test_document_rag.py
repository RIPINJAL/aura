def test_document_creation_and_search(client):
    document_payload = {
        "title": "Resume",
        "content": "Python, machine learning, and remote internship experience in computer vision.",
        "source": "resume.pdf",
    }

    create_response = client.post("/api/documents", json=document_payload)
    assert create_response.status_code == 201
    assert create_response.json()["title"] == "Resume"

    search_response = client.post("/api/documents/search", json={"query": "python"})
    assert search_response.status_code == 200
    results = search_response.json()["results"]
    assert len(results) >= 1
    assert results[0]["title"] == "Resume"

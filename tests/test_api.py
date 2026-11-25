import pytest
from fastapi.testclient import TestClient
from ai_engineer_project.main import app

# Create the test client bound to your FastAPI app
client = TestClient(app)

# 1. Test /health
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# 2. Test valid document data
def test_create_valid_document():
    payload = {
        "filename": "annual_report.pdf",
        "file_type": "pdf",
        "size_bytes": 10240,
        "description": "Financial summary for Q4",
    }
    response = client.post("/documents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == payload["filename"]
    assert data["file_type"] == "pdf"
    assert data["size_bytes"] == 10240
    assert data["description"] == payload["description"]

# 3. Test invalid document data (e.g., negative/zero size, invalid file type)
@pytest.mark.parametrize(
    "invalid_payload",
    [
        # size_bytes must be > 0
        {"filename": "test.pdf", "file_type": "pdf", "size_bytes": 0},
        # file_type must be in the allowed list
        {"filename": "malware.exe", "file_type": "exe", "size_bytes": 500},
        # filename cannot be empty
        {"filename": "", "file_type": "txt", "size_bytes": 500},
    ],
)
def test_create_invalid_document(invalid_payload):
    response = client.post("/documents", json=invalid_payload)
    # FastAPI returns HTTP 422 Unprocessable Entity when Pydantic validation fails
    assert response.status_code == 422

# 4. Test missing required fields
def test_create_document_missing_fields():
    # Missing required 'size_bytes' and 'file_type'
    payload = {"filename": "notes.txt"}
    response = client.post("/documents", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    # Check that FastAPI reports which fields are missing
    missing_fields = [
        err["loc"][-1] for err in errors if err["type"] == "missing"
    ]
    assert "file_type" in missing_fields
    assert "size_bytes" in missing_fields


# 5. Test GET /documents (list all)
def test_list_documents():
    create_resp = client.post(
        "/documents",
        json={"filename": "list_test.txt", "file_type": "txt", "size_bytes": 128},
    )
    assert create_resp.status_code == 200
    created_id = create_resp.json()["id"]

    response = client.get("/documents")
    assert response.status_code == 200
    docs = response.json()
    assert isinstance(docs, list)
    assert any(doc["id"] == created_id for doc in docs)


# 6. Test GET /documents/{id} (get one & 404)
def test_get_document():
    create_resp = client.post(
        "/documents",
        json={"filename": "single.md", "file_type": "md", "size_bytes": 256},
    )
    doc_id = create_resp.json()["id"]

    response = client.get(f"/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["filename"] == "single.md"

    missing_resp = client.get("/documents/999999")
    assert missing_resp.status_code == 404


# 7. Test PUT /documents/{id} (update & 404)
def test_update_document():
    create_resp = client.post(
        "/documents",
        json={"filename": "old.csv", "file_type": "csv", "size_bytes": 512},
    )
    doc_id = create_resp.json()["id"]

    update_payload = {
        "filename": "updated.json",
        "file_type": "json",
        "size_bytes": 1024,
        "description": "Updated metadata",
    }
    response = client.put(f"/documents/{doc_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
    assert data["filename"] == "updated.json"
    assert data["file_type"] == "json"
    assert data["size_bytes"] == 1024
    assert data["description"] == "Updated metadata"

    missing_resp = client.put("/documents/999999", json=update_payload)
    assert missing_resp.status_code == 404


# 8. Test DELETE /documents/{id} (delete & 404)
def test_delete_document():
    create_resp = client.post(
        "/documents",
        json={"filename": "to_delete.pdf", "file_type": "pdf", "size_bytes": 2048},
    )
    doc_id = create_resp.json()["id"]

    del_resp = client.delete(f"/documents/{doc_id}")
    assert del_resp.status_code == 200
    assert del_resp.json() == {"status": "deleted", "id": doc_id}

    # Confirm it no longer exists
    get_resp = client.get(f"/documents/{doc_id}")
    assert get_resp.status_code == 404

    missing_resp = client.delete(f"/documents/{doc_id}")
    assert missing_resp.status_code == 404
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
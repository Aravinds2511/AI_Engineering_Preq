from fastapi import FastAPI
from ai_engineer_project.models import Document

app = FastAPI(title="AI Engineer Project")

@app.get("/health")
def health_check():
    return {"status":"healthy"}

@app.post("/documents", response_model=Document)
def create_document(doc: Document):
    return doc
from fastapi import Depends, FastAPI
from sqlmodel import Session, select, text

from ai_engineer_project.database import get_session
from ai_engineer_project.models import Document, DocumentCreate, DocumentRead

app = FastAPI(title="AI Engineer Project")


@app.get("/health")
def health_check(session: Session = Depends(get_session)):
    # Executes a lightweight query to verify PostgreSQL connectivity
    session.exec(text("SELECT 1"))
    return {"status": "healthy"}


@app.post("/documents", response_model=DocumentRead)
def create_document(
    doc: DocumentCreate,
    session: Session = Depends(get_session),
):
    db_doc = Document.model_validate(doc)
    session.add(db_doc)
    session.commit()
    session.refresh(db_doc)
    return db_doc


@app.get("/documents", response_model=list[DocumentRead])
def list_documents(session: Session = Depends(get_session)):
    return session.exec(select(Document)).all()
from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Session, select, text

from ai_engineer_project.database import get_session
from ai_engineer_project.models import Document, DocumentCreate, DocumentRead

app = FastAPI(title="AI Engineer Project")


def _get_document_or_404(document_id: int, session: Session) -> Document:
    """Fetch a document by ID or raise a 404 HTTPException."""
    db_doc = session.get(Document, document_id)
    if not db_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return db_doc


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


@app.get("/documents/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: int,
    session: Session = Depends(get_session),
):
    return _get_document_or_404(document_id, session)


@app.put("/documents/{document_id}", response_model=DocumentRead)
def update_document(
    document_id: int,
    doc: DocumentCreate,
    session: Session = Depends(get_session),
):
    db_doc = _get_document_or_404(document_id, session)
    db_doc.sqlmodel_update(doc.model_dump())
    session.add(db_doc)
    session.commit()
    session.refresh(db_doc)
    return db_doc


@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    session: Session = Depends(get_session),
):
    db_doc = _get_document_or_404(document_id, session)
    session.delete(db_doc)
    session.commit()
    return {"status": "deleted", "id": document_id}
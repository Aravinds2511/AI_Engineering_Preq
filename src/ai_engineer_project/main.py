from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from ai_engineer_project.database import get_session
from ai_engineer_project.models import (
    Document,
    DocumentCreate,
    DocumentRead,
    Token,
    User,
    UserCreate,
    UserRead,
)
from ai_engineer_project.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

app = FastAPI(title="AI Engineer Project")

security_scheme = HTTPBearer()
SessionDep = Annotated[Session, Depends(get_session)]
CredentialsDep = Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)]


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
def health_check(session: SessionDep):
    # Executes a lightweight query to verify PostgreSQL connectivity
    session.exec(select(1))
    return {"status": "healthy"}


@app.post("/documents", response_model=DocumentRead)
def create_document(
    doc: DocumentCreate,
    session: SessionDep,
):
    db_doc = Document.model_validate(doc)
    session.add(db_doc)
    session.commit()
    session.refresh(db_doc)
    return db_doc


@app.get("/documents", response_model=list[DocumentRead])
def list_documents(session: SessionDep):
    return session.exec(select(Document)).all()


@app.get("/documents/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: int,
    session: SessionDep,
):
    return _get_document_or_404(document_id, session)


@app.put("/documents/{document_id}", response_model=DocumentRead)
def update_document(
    document_id: int,
    doc: DocumentCreate,
    session: SessionDep,
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
    session: SessionDep,
):
    db_doc = _get_document_or_404(document_id, session)
    session.delete(db_doc)
    session.commit()
    return {"status": "deleted", "id": document_id}


@app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate,
    session: SessionDep,
):
    existing = session.exec(
        select(User).where(User.username == user_in.username)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    db_user = User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.post("/auth/login", response_model=Token)
def login_user(
    credentials: UserCreate,
    session: SessionDep,
):
    db_user = session.exec(
        select(User).where(User.username == credentials.username)
    ).first()

    if not db_user or not verify_password(credentials.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(db_user.id)})
    return Token(access_token=access_token)


def get_current_user(
    credentials: CredentialsDep,
    session: SessionDep,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id_int = int(user_id)
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise credentials_exception from exc

    db_user = session.get(User, user_id_int)
    if db_user is None:
        raise credentials_exception
    return db_user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


@app.get("/users/me", response_model=UserRead)
def read_current_user(current_user: CurrentUserDep):
    return current_user
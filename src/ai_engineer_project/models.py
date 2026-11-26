from datetime import datetime, timezone
from pydantic import field_validator, EmailStr
from sqlmodel import Field, SQLModel


class DocumentBase(SQLModel):
    filename: str = Field(
        min_length=1,
        max_length=255,
        description="Name of the file including extension",
    )
    file_type: str = Field(
        description="File format or extension (e.g. pdf, txt, md, docx)",
    )
    size_bytes: int = Field(
        gt=0,
        le=50 * 1024 * 1024,
        description="File size in bytes",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional summary or note about the document",
    )

    @field_validator("file_type")
    @classmethod
    def validate_file_type(cls, value: str) -> str:
        allowed = {"pdf", "txt", "md", "docx", "csv", "json"}
        normalized = value.lower().lstrip(".")
        if normalized not in allowed:
            raise ValueError(
                f"Unsupported file_type '{value}'. Allowed: {', '.join(allowed)}"
            )
        return normalized


class Document(DocumentBase, table=True):
    __tablename__ = "documents"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    id: int
    created_at: datetime

class UserBase(SQLModel):
    username: str = Field(min_length=3, max_length=50, unique=True, index=True)

class User(UserBase, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserRead(UserBase):
    id: int
    created_at: datetime

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
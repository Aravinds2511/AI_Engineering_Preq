from pydantic import BaseModel, Field, field_validator

class Document(BaseModel):
    # Required: must not be empty, max 255 chars
    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the file including extension"
    )

    # Required: restricted to common file extensions
    file_type: str = Field(
        ...,
        description="File format or extension (e.g. pdf, txt, md, docx)",
    )

    # Required: size must be strictly positive (> 0 bytes) and under 50 MB
    size_bytes: int = Field(
        ...,
        gt=0,
        le=50 * 1024 * 1024, # 50 MB limit
        description="File size in bytes",
    )

    # Optional field: defaults to None if not provided
    description: str | None = Field (
        default=None,
        max_length=500,
        description="Optional summary or note about the document",
    )
    
    # Normalizes extension and rejects unsupported types
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
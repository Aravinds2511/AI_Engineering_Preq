# 1. Base Python image matching pyproject.toml (>=3.14)
FROM python:3.14-slim

# 2. Copy uv binary from the official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Set working directory
WORKDIR /app

# 4. Install dependencies first (cached unless pyproject.toml or uv.lock changes)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 5. Copy application source code & README (referenced in pyproject.toml)
COPY README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev

# 6. Expose FastAPI port
EXPOSE 8000

# 7. Start Uvicorn bound to 0.0.0.0 so it is reachable outside the container
CMD ["uv", "run", "--no-sync", "uvicorn", "ai_engineer_project.main:app", "--host", "0.0.0.0", "--port", "8000"]

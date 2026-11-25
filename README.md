# AI Engineer Project

## Setup & Running

### 1. Prerequisites
- Python `>= 3.14`
- [`uv`](https://docs.astral.sh/uv/) package manager
- Docker & Docker Compose

### 2. Install Dependencies
```bash
uv sync
```

### 3. Database Setup (PostgreSQL)

1. **Configure environment variables** (copy `.env.example` to `.env` and set values):
   ```bash
   cp .env.example .env
   ```

2. **Start PostgreSQL container:**
   ```bash
   docker compose up -d
   ```

3. **Apply database migrations:**
   ```bash
   uv run alembic upgrade head
   ```

4. **Check database records (optional):**
   ```bash
   docker compose exec postgres psql -U postgres -d ai_engineer_db -c "SELECT * FROM documents;"
   ```

### 4. Start the Development Server
```bash
uv run uvicorn ai_engineer_project.main:app --reload
```
Alternatively, use the package CLI entrypoint:
```bash
uv run ai-engineer-project
```

- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`

### 5. Run Tests
```bash
uv run pytest -v
```

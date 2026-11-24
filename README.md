# AI Engineer Project

## Setup & Running

### 1. Prerequisites
- Python `>= 3.14`
- [`uv`](https://docs.astral.sh/uv/) package manager

### 2. Install Dependencies
```bash
uv sync
```

### 3. Start the Development Server
```bash
uv run uvicorn ai_engineer_project.main:app --reload
```
Alternatively, use the package CLI entrypoint:
```bash
uv run ai-engineer-project
```

- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`

### 4. Run Tests
```bash
uv run pytest -v
```

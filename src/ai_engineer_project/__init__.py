import uvicorn
from ai_engineer_project.main import app

def main() -> None:
    uvicorn.run("ai_engineer_project.main:app", host="0.0.0.0", port=8000, reload=True)

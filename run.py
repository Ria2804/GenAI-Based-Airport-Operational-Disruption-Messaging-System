"""
Run from the project root:
    python run.py
Or with uvicorn directly:
    uvicorn backend.main:app --reload --port 8000
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
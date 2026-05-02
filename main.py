from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

from backend.schemas import DisruptionInput
from backend.ai_engine import generate_disruption_messages
from backend.database import init_db, save_disruption

app = FastAPI(title="Airport Disruption AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (frontend JS/CSS)
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/disruptions")
async def get_disruptions():
    from backend.database import get_all_disruptions
    rows = get_all_disruptions()
    return JSONResponse(content=rows)

@app.post("/generate")
async def generate(payload: DisruptionInput):
    try:
        messages = generate_disruption_messages(payload)
        save_disruption(payload, messages)
        return JSONResponse(content=messages)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
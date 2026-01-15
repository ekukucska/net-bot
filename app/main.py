from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from netbot.api.api import router as api_router
from netbot.db import init_db
import os

# Initialize database on startup
init_db()

app = FastAPI(
    title="NetBot",
    description="Rule-based network diagnostics chatbot",
    version="0.1.0",
)

# Include all API routes under /v1
app.include_router(api_router)

# Get the directory where main.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    """Serve the main UI"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "app": "NetBot", "version": "0.1.0"}

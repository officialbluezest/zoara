import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db
from routers import brand, inspo, research, content, meta

app = FastAPI(title="Zoara Content Creation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(brand.router)
app.include_router(inspo.router)
app.include_router(research.router)
app.include_router(content.router)
app.include_router(meta.router)

@app.get("/api/health")
def health():
    return {"status": "ok", "anthropic_key_configured": bool(os.environ.get("ANTHROPIC_API_KEY"))}


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{path:path}")
    def serve_frontend_files(path: str):
        full_path = os.path.join(FRONTEND_DIR, path)
        if os.path.isfile(full_path):
            return FileResponse(full_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

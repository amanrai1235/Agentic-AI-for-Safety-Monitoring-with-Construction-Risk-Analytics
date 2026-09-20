import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import Base, engine
from .routers import agents, dashboards, governance, projects, reporting, site

logging.basicConfig(level=logging.INFO)
settings = get_settings()

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="BuildSure AI",
    description="Agentic Construction Risk Intelligence Platform — agent network, risk engine and dashboards.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(site.router)
app.include_router(governance.router)
app.include_router(agents.router)
app.include_router(dashboards.router)
app.include_router(reporting.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": app.version}


# Single-server deployment: if the React app has been built, serve it from here.
DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        candidate = DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(DIST / "index.html")

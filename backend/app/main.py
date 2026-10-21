from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.core.config import Settings
from backend.app.db import make_engine


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    engine = make_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(app):
        yield
        engine.dispose()

    app = FastAPI(title="LabTrack", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "labtrack"}

    return app

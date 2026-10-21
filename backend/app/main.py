from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from backend.app.api import auth
from backend.app.core.config import Settings
from backend.app.db import make_engine
from backend.app.errors import install_error_handlers


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
    install_error_handlers(app)
    app.include_router(auth.router)

    @app.middleware("http")
    async def response_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        )
        if request.url.path.startswith("/api/auth"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "labtrack"}

    return app

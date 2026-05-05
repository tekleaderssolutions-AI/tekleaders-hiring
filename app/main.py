from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.jd.jobs import router as jobs_router
from app.api.v1.resume.candidates import router as candidates_router
from app.api.v1.matching import router as matching_router
from app.api.v1.feedback import router as feedback_router

def create_app() -> FastAPI:
    # ... (existing setup)
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-Driven Recruitment Platform — Hexagonal + DDD + Event-Driven",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ─── Startup Events ───────────────────────────────────────────────────────
    @app.on_event("startup")
    async def on_startup():
        from app.scripts.sync_schema import sync_schema
        try:
            print("Running database schema synchronization...")
            await sync_schema()
            print("Database schema synchronization complete.")
        except Exception as e:
            print(f"Error during database sync: {e}")

    # ─── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─── Routers ──────────────────────────────────────────────────────────────
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(jobs_router, prefix="/api/v1")
    app.include_router(candidates_router, prefix="/api/v1")
    app.include_router(matching_router, prefix="/api/v1")
    app.include_router(feedback_router, prefix="/api/v1")

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "app": settings.APP_NAME}

    return app

app = create_app()

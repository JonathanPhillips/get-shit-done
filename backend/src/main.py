"""Focus Agent Backend - Main Application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.database import init_db, close_db
from src.api import health

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Intelligent focus management with Claude AI, GitHub, and Obsidian integrations",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(health.router)

# API routers
from src.api.tasks import router as tasks_router
from src.api.pomodoro import router as pomodoro_router

app.include_router(tasks_router, prefix="/api")
app.include_router(pomodoro_router, prefix="/api")

# Future routers will be added here:
# app.include_router(github.router, prefix=f"{settings.api_prefix}/github")
# app.include_router(obsidian.router, prefix=f"{settings.api_prefix}/obsidian")
# app.include_router(claude.router, prefix=f"{settings.api_prefix}/claude")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )

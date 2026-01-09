"""Health check endpoints."""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis

from src.core.config import settings
from src.core.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check with dependency checks.

    Args:
        db: Database session

    Returns:
        dict: Detailed health status
    """
    health_status = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "up",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["database"] = {
            "status": "down",
            "message": f"Database error: {str(e)}"
        }

    # Check Redis
    if settings.redis_enabled:
        try:
            redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            await redis_client.ping()
            await redis_client.close()
            health_status["checks"]["redis"] = {
                "status": "up",
                "message": "Redis connection successful"
            }
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["checks"]["redis"] = {
                "status": "down",
                "message": f"Redis error: {str(e)}"
            }
    else:
        health_status["checks"]["redis"] = {
            "status": "disabled",
            "message": "Redis is disabled"
        }

    # Check Obsidian vault (if configured)
    if settings.obsidian_vault_path and settings.obsidian_sync_enabled:
        import os
        if os.path.exists(settings.obsidian_vault_path):
            health_status["checks"]["obsidian"] = {
                "status": "up",
                "message": "Obsidian vault accessible"
            }
        else:
            health_status["status"] = "degraded"
            health_status["checks"]["obsidian"] = {
                "status": "down",
                "message": "Obsidian vault not found"
            }
    else:
        health_status["checks"]["obsidian"] = {
            "status": "disabled",
            "message": "Obsidian sync is disabled"
        }

    return health_status


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    """
    Kubernetes readiness probe endpoint.

    Args:
        db: Database session

    Returns:
        dict: Readiness status
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not ready"}


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """
    Kubernetes liveness probe endpoint.

    Returns:
        dict: Liveness status
    """
    return {"status": "alive"}

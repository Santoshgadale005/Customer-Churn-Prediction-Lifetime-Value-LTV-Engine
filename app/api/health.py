"""
Health check API routes.

Provides a simple endpoint to verify the API is running
and the model is loaded — essential for production monitoring.
"""

from fastapi import APIRouter
from app.api.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="API health check",
)
def health_check():
    """
    Returns the current status of the API and model.
    Used by monitoring tools, load balancers, and CI/CD pipelines.
    """
    # Import here to avoid circular imports and get live status
    from app.api.predict import MODEL_LOADED

    return HealthResponse(
        status="healthy" if MODEL_LOADED else "degraded",
        model_loaded=MODEL_LOADED,
        api_version="1.0.0",
        model_type="XGBoost",
    )

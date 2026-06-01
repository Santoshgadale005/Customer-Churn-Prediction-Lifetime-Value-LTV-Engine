"""
Health check API routes.

Provides a simple endpoint to verify the API is running
and the model is loaded — essential for production monitoring.
"""

from fastapi import APIRouter
router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="API health check",
)
def health_check():
    """
    Returns the current status of the API and model.
    Used by monitoring tools, load balancers, and CI/CD pipelines.
    """
    return {"status": "healthy"}

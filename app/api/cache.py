from fastapi import APIRouter, Depends

from app.database.user_model import User
from app.services.auth_service import require_admin
from app.utils.cache import clear_prediction_cache, get_cache_status

router = APIRouter(prefix="/api/v1/cache", tags=["Cache"])


@router.get("/status")
def cache_status(current_admin: User = Depends(require_admin)):
    return get_cache_status()


@router.delete("")
def invalidate_cache(current_admin: User = Depends(require_admin)):
    deleted_keys = clear_prediction_cache()
    return {
        "message": "Prediction cache invalidated",
        "deleted_keys": deleted_keys,
    }

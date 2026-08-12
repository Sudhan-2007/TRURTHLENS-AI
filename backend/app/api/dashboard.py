from fastapi import APIRouter, Depends

from ..middleware.auth import get_current_user, require_admin
from ..middleware.rate_limit import rate_limit_analytics
from ..services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/user", response_model=dict)
async def user_dashboard(user: dict = Depends(get_current_user)):
    return await dashboard_service.user_dashboard(user)


@router.get("/user/statistics", response_model=dict)
async def user_statistics(user: dict = Depends(rate_limit_analytics)):
    return await dashboard_service.user_statistics(user)


@router.get("/admin", response_model=dict)
async def admin_dashboard(admin: dict = Depends(require_admin)):
    return await dashboard_service.admin_dashboard()


@router.get("/admin/statistics", response_model=dict)
async def admin_statistics(
    admin: dict = Depends(require_admin),
    _: dict = Depends(rate_limit_analytics),
):
    return await dashboard_service.admin_statistics()

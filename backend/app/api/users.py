from fastapi import APIRouter, Depends, HTTPException, status

from ..db import get_users_collection
from ..middleware.auth import get_current_user, require_admin
from ..models.user import serialize_user
from ..schemas.user import Role, UserOut, UserUpdate
from ..services import auth_service

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_profile(user: dict = Depends(get_current_user)):
    return serialize_user(dict(user))


@router.put("/me", response_model=UserOut)
async def update_profile(
    payload: UserUpdate,
    user: dict = Depends(get_current_user),
):
    updated = await auth_service.update_user(str(user["_id"]), payload)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return serialize_user(dict(updated))


@router.get("", response_model=list[UserOut])
async def list_users(admin: dict = Depends(require_admin)):
    users = []
    async for doc in get_users_collection().find({}):
        users.append(serialize_user(dict(doc)))
    return users


@router.put("/{user_id}/role", response_model=UserOut)
async def set_user_role(
    user_id: str,
    role: Role,
    admin: dict = Depends(require_admin),
):
    user = await auth_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await get_users_collection().update_one(
        {"_id": user["_id"]}, {"$set": {"role": role.value}}
    )
    updated = await auth_service.get_user_by_id(user_id)
    return serialize_user(dict(updated))

from datetime import UTC, datetime

from fastapi import HTTPException, status

from ..db import get_blacklist_collection, get_users_collection
from ..models.user import utcnow
from ..schemas.user import Role, UserRegister, UserUpdate
from ..utils.security import hash_password, verify_password


async def get_user_by_email(email: str) -> dict | None:
    return await get_users_collection().find_one({"email": email.lower()})


async def get_user_by_id(user_id: str) -> dict | None:
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        oid = ObjectId(user_id)
    except InvalidId:
        return None
    return await get_users_collection().find_one({"_id": oid})


async def register_user(payload: UserRegister) -> dict:
    users = get_users_collection()
    email = payload.email.lower()

    if await users.find_one({"email": email}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    now = utcnow()
    user_doc = {
        "name": payload.name.strip(),
        "email": email,
        "password_hash": hash_password(payload.password),
        "role": Role.USER.value,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    result = await users.insert_one(user_doc)
    return {"id": str(result.inserted_id)}


async def authenticate_user(email: str, password: str) -> dict | None:
    user = await get_user_by_email(email)
    if user is None:
        return None
    if not user.get("is_active", True):
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


async def blacklist_token(jti: str, expires_at: datetime) -> None:
    await get_blacklist_collection().insert_one(
        {"jti": jti, "exp": expires_at.replace(tzinfo=UTC)}
    )


async def is_token_blacklisted(jti: str) -> bool:
    return await get_blacklist_collection().find_one({"jti": jti}) is not None


async def update_user(user_id: str, payload: UserUpdate) -> dict | None:
    users = get_users_collection()
    user = await get_user_by_id(user_id)
    if user is None:
        return None

    updates: dict = {"updated_at": utcnow()}

    if payload.name is not None:
        updates["name"] = payload.name.strip()
    if payload.email is not None:
        new_email = payload.email.lower()
        if new_email != user["email"]:
            existing = await users.find_one({"email": new_email})
            if existing and str(existing["_id"]) != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this email already exists",
                )
        updates["email"] = new_email
    if payload.password is not None:
        updates["password_hash"] = hash_password(payload.password)

    await users.update_one({"_id": user["_id"]}, {"$set": updates})
    return await get_user_by_id(user_id)


async def generate_password_reset_token(email: str) -> str | None:
    import secrets
    from datetime import timedelta

    user = await get_user_by_email(email)
    if user is None:
        return None

    token = secrets.token_urlsafe(32)
    expires_at = utcnow() + timedelta(hours=1)

    await get_users_collection().update_one(
        {"_id": user["_id"]},
        {"$set": {"reset_token": token, "reset_token_exp": expires_at}},
    )

    # In a real app, this is where you would send the email.
    # For now, we simulate by logging to the console.
    print("--- PASSWORD RESET SIMULATION ---")
    print(f"To reset password for {email}, use token: {token}")
    print(f"Or visit: http://localhost:5173/reset-password/{token}")
    print("---------------------------------")

    return token


async def reset_password_with_token(token: str, new_password: str) -> bool:
    users = get_users_collection()
    user = await users.find_one({"reset_token": token})

    if not user:
        return False

    # Check if token is expired
    exp = user.get("reset_token_exp")
    if not exp or exp.replace(tzinfo=UTC) < utcnow().replace(tzinfo=UTC):
        return False

    # Update password and clear token
    await users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "password_hash": hash_password(new_password),
                "updated_at": utcnow(),
            },
            "$unset": {"reset_token": "", "reset_token_exp": ""},
        },
    )
    return True

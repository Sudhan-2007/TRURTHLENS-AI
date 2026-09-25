from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from ..middleware.auth import bearer_scheme, get_current_user
from ..schemas.auth import LoginRequest, Token
from ..schemas.user import UserRegister
from ..services import auth_service
from ..utils.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
)
async def register(payload: UserRegister):
    result = await auth_service.register_user(payload)
    return {"message": "User registered successfully", "user_id": result["id"]}


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest):
    user = await auth_service.authenticate_user(payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token, expires_in = create_access_token(str(user["_id"]), user["role"])
    return Token(access_token=token, expires_in=expires_in)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    _: dict = Depends(get_current_user),
):
    from ..utils.security import decode_access_token

    payload = decode_access_token(credentials.credentials)
    exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
    await auth_service.blacklist_token(payload["jti"], exp)


from ..schemas.auth import ForgotPasswordRequest, ResetPasswordRequest


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(payload: ForgotPasswordRequest):
    token = await auth_service.generate_password_reset_token(payload.email)
    if not token:
        # Avoid user enumeration by returning success even if email not found
        return {
            "message": "If that email is registered, a reset link has been logged (simulated)."
        }
    return {
        "message": "If that email is registered, a reset link has been logged (simulated)."
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(payload: ResetPasswordRequest):
    success = await auth_service.reset_password_with_token(
        payload.token, payload.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )
    return {"message": "Password has been reset successfully."}

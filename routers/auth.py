from fastapi import APIRouter, Depends, HTTPException, status

from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_admin,
)
from database import get_db
from schemas.auth import LoginRequest, Token


auth_router = APIRouter()


@auth_router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db=Depends(get_db)
):
    user = authenticate_user(
        db,
        login_data.username,
        login_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(user)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@auth_router.get("/me")
def get_me(
    current_user=Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role
    }


@auth_router.get("/admin")
def admin_only(
    current_user=Depends(require_admin)
):
    return {
        "message": "Hello admin",
        "username": current_user.username,
        "role": current_user.role
    }
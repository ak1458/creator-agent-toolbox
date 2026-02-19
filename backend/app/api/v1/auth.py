from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_password_hash,
    get_user_by_id,
    get_user_id_from_token,
)
from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Get current user ID from JWT token."""
    if token is None:
        # For development/demo, return a default user
        # In production, this should raise an exception
        return "demo_user_001"
    
    user_id = get_user_id_from_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


@router.post("/register")
async def register(email: str, password: str) -> dict[str, Any]:
    """Register a new user."""
    # In production, validate email format and password strength
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters",
        )
    
    user_id = create_user(email, password)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user_id, "email": email},
        expires_delta=access_token_expires,
    )
    
    logger.info("user_registered", user_id=user_id, email=email)
    
    return {
        "user_id": user_id,
        "email": email,
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, Any]:
    """Login and get access token."""
    user_id = authenticate_user(form_data.username, form_data.password)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(user_id)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user_id, "email": user["email"]},
        expires_delta=access_token_expires,
    )
    
    logger.info("user_login", user_id=user_id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id,
        "email": user["email"],
    }


@router.get("/me")
async def get_me(current_user: str = Depends(get_current_user)) -> dict[str, Any]:
    """Get current user info."""
    user = get_user_by_id(current_user)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return {
        "user_id": current_user,
        "email": user["email"],
        "created_at": user["created_at"],
    }

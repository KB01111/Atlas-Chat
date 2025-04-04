from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
from datetime import timedelta
from loguru import logger

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    validate_password_strength,
    get_current_user,
    rate_limiter
)
from app.core.config import settings
from app.models.models import User, UserCreate, UserLogin, Token
from app.core.database import get_db_session

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session = Depends(get_db_session)
):
    """
    Authenticate user and return JWT token
    """
    # Check rate limiting
    client_ip = request.client.host
    if rate_limiter.is_rate_limited(f"login:{client_ip}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Get user from database
    user = await db_session.query(User).filter(User.email == form_data.username).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserCreate,
    db_session = Depends(get_db_session)
):
    """
    Register a new user
    """
    # Check rate limiting
    client_ip = request.client.host
    if rate_limiter.is_rate_limited(f"register:{client_ip}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    # Check if user already exists
    existing_user = await db_session.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet security requirements. It must be at least 8 characters long and contain uppercase, lowercase, number, and special character."
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    # Save to database
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.email}")
    return {"message": "User registered successfully"}

@router.get("/me", response_model=Dict[str, Any])
async def get_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session = Depends(get_db_session)
):
    """
    Get current user information
    """
    user = await db_session.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at
    }

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: Request,
    password_data: Dict[str, str],
    current_user: Dict[str, Any] = Depends(get_current_user),
    db_session = Depends(get_db_session)
):
    """
    Change user password
    """
    # Check rate limiting
    if rate_limiter.is_rate_limited(f"change_password:{current_user['user_id']}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password change attempts. Please try again later."
        )
    
    # Get user from database
    user = await db_session.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data["current_password"], user.hashed_password):
        logger.warning(f"Failed password change attempt for user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength
    if not validate_password_strength(password_data["new_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password does not meet security requirements. It must be at least 8 characters long and contain uppercase, lowercase, number, and special character."
        )
    
    # Update password
    user.hashed_password = get_password_hash(password_data["new_password"])
    await db_session.commit()
    
    logger.info(f"Password changed for user: {user.email}")
    return {"message": "Password changed successfully"}

@router.post("/logout")
async def logout():
    """
    Logout user (client-side only, invalidate token on client)
    """
    return {"message": "Logged out successfully"}

"""
Pydantic v2 models for authentication requests and responses.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Public-facing user representation (no password)."""

    id: str
    name: str
    email: str
    bio: str = ""
    avatar: str = ""
    followers_count: int = 0
    following_count: int = 0
    created_at: datetime


class TokenResponse(BaseModel):
    """Returned after successful signup / login."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse

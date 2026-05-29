"""
Pydantic v2 models for user profile and social features.
"""

from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    """Schema for updating a user's profile. All fields are optional."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    avatar: str | None = None


class UserStats(BaseModel):
    """Aggregated statistics for a user's content and social presence."""

    total_stories: int = 0
    total_views: int = 0
    total_reads: int = 0
    followers_count: int = 0
    following_count: int = 0


class FollowResponse(BaseModel):
    """Response returned after a follow / unfollow action."""

    message: str
    followers_count: int

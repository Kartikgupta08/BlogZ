"""
Pydantic v2 models for the Comments module.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    """Schema for creating a new comment."""

    content: str = Field(..., min_length=1, max_length=5000, description="Comment text")


class CommentResponse(BaseModel):
    """Response schema for a single comment."""

    id: str
    story_id: str
    author_id: str
    author_name: str
    content: str
    created_at: datetime


class CommentListResponse(BaseModel):
    """Paginated response wrapper for comments."""

    comments: list[CommentResponse]
    total: int

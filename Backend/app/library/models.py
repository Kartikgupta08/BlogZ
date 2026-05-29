"""
Pydantic v2 models for the Library module (reading lists & bookmarks).
"""

from datetime import datetime
from pydantic import BaseModel, Field


class ListCreate(BaseModel):
    """Schema for creating a new reading list."""

    name: str = Field(..., min_length=1, max_length=100, description="Name of the reading list")
    description: str = Field(default="", max_length=500, description="Optional description")


class ListUpdate(BaseModel):
    """Schema for updating an existing reading list. All fields optional."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class ListResponse(BaseModel):
    """Response schema for a reading list."""

    id: str
    name: str
    description: str
    user_id: str
    story_count: int
    created_at: datetime
    updated_at: datetime


class BookmarkResponse(BaseModel):
    """Response schema for a bookmarked story."""

    id: str
    story_id: str
    story_title: str
    story_author: str
    created_at: datetime

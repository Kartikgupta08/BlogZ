"""
Pydantic v2 models for story requests and responses.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class StoryCreate(BaseModel):
    """Schema for creating a new story (defaults to draft)."""

    title: str = Field(..., min_length=1, max_length=300)
    content: str = ""
    category: str = ""
    image_url: str = ""


class StoryUpdate(BaseModel):
    """Schema for updating an existing story. All fields optional."""

    title: str | None = None
    content: str | None = None
    category: str | None = None
    image_url: str | None = None
    status: Literal["draft", "published", "unlisted"] | None = None


class StoryResponse(BaseModel):
    """Public-facing story representation."""

    id: str
    title: str
    content: str
    category: str = ""
    image_url: str = ""
    status: str = "draft"
    author_id: str
    author_name: str
    views: int = 0
    reads: int = 0
    comments_count: int = 0
    word_count: int = 0
    read_time: str = "1 min read"
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None


class StoryListResponse(BaseModel):
    """List of stories with total count."""

    stories: list[StoryResponse]
    total: int


class StoryStatsResponse(BaseModel):
    """Engagement stats for a single story."""

    views: int = 0
    reads: int = 0
    comments_count: int = 0

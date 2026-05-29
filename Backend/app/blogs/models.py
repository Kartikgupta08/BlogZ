"""
Pydantic v2 models for blog requests and responses.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class BlogCreate(BaseModel):
    """Schema for creating a new blog post."""

    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=100)
    image_url: str = ""


class BlogUpdate(BaseModel):
    """Schema for updating an existing blog post. All fields optional."""

    title: str | None = None
    description: str | None = None
    content: str | None = None
    category: str | None = None
    image_url: str | None = None


class BlogResponse(BaseModel):
    """Public-facing blog representation."""

    id: str
    title: str
    description: str
    content: str
    category: str
    image_url: str = ""
    author_id: str
    author_name: str
    views: int = 0
    reads: int = 0
    comments_count: int = 0
    created_at: datetime
    updated_at: datetime


class BlogListResponse(BaseModel):
    """Paginated list of blogs."""

    blogs: list[BlogResponse]
    total: int
    page: int
    per_page: int

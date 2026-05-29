"""
Blog routes: CRUD operations for published blog posts.
"""

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.utils import get_current_user
from app.blogs.models import (
    BlogCreate,
    BlogListResponse,
    BlogResponse,
    BlogUpdate,
)
from app.database import get_db

router = APIRouter(prefix="/api/blogs", tags=["Blogs"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_object_id(blog_id: str) -> ObjectId:
    """Convert a string to a BSON ObjectId, raising 400 on failure."""
    try:
        return ObjectId(blog_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid blog id: {blog_id}",
        )


async def _build_blog_response(blog: dict) -> BlogResponse:
    """Build a ``BlogResponse`` from a MongoDB blog document.

    Resolves the author name from the users collection.
    """
    db = get_db()

    author_name = "Unknown"
    if blog.get("author_id"):
        try:
            author = await db.users.find_one(
                {"_id": ObjectId(blog["author_id"])},
                {"name": 1},
            )
            if author:
                author_name = author["name"]
        except (InvalidId, TypeError):
            pass

    return BlogResponse(
        id=str(blog["_id"]),
        title=blog["title"],
        description=blog["description"],
        content=blog["content"],
        category=blog["category"],
        image_url=blog.get("image_url", ""),
        author_id=blog.get("author_id", ""),
        author_name=author_name,
        views=blog.get("views", 0),
        reads=blog.get("reads", 0),
        comments_count=blog.get("comments_count", 0),
        created_at=blog.get("created_at", datetime.now(timezone.utc)),
        updated_at=blog.get("updated_at", datetime.now(timezone.utc)),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/", response_model=BlogListResponse)
async def list_blogs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    category: str | None = Query(None, description="Filter by category"),
) -> BlogListResponse:
    """List published blogs with pagination and optional category filter.

    Returns a paginated list including author names resolved from the users
    collection.
    """
    db = get_db()

    query: dict = {}
    if category:
        query["category"] = category

    total = await db.blogs.count_documents(query)

    skip = (page - 1) * per_page
    cursor = db.blogs.find(query).sort("created_at", -1).skip(skip).limit(per_page)

    blogs: list[BlogResponse] = []
    async for blog_doc in cursor:
        blogs.append(await _build_blog_response(blog_doc))

    return BlogListResponse(
        blogs=blogs,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/categories", response_model=list[str])
async def list_categories() -> list[str]:
    """Return a list of distinct blog categories."""
    db = get_db()
    categories: list[str] = await db.blogs.distinct("category")
    return sorted(categories)


@router.get("/{blog_id}", response_model=BlogResponse)
async def get_blog(blog_id: str) -> BlogResponse:
    """Get a single blog by ID and increment its view count."""
    db = get_db()
    oid = _to_object_id(blog_id)

    blog = await db.blogs.find_one({"_id": oid})
    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    # Increment views
    await db.blogs.update_one({"_id": oid}, {"$inc": {"views": 1}})
    blog["views"] = blog.get("views", 0) + 1

    return await _build_blog_response(blog)


@router.post(
    "/",
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_blog(
    body: BlogCreate,
    current_user: dict = Depends(get_current_user),
) -> BlogResponse:
    """Create a new blog post.

    The ``author_id`` is automatically set from the authenticated user.
    """
    db = get_db()
    now = datetime.now(timezone.utc)

    blog_doc = {
        "title": body.title,
        "description": body.description,
        "content": body.content,
        "category": body.category,
        "image_url": body.image_url,
        "author_id": current_user["_id"],
        "views": 0,
        "reads": 0,
        "comments_count": 0,
        "created_at": now,
        "updated_at": now,
    }

    result = await db.blogs.insert_one(blog_doc)
    blog_doc["_id"] = result.inserted_id

    return await _build_blog_response(blog_doc)


@router.put("/{blog_id}", response_model=BlogResponse)
async def update_blog(
    blog_id: str,
    body: BlogUpdate,
    current_user: dict = Depends(get_current_user),
) -> BlogResponse:
    """Update an existing blog post.

    Only the original author may perform this action.
    """
    db = get_db()
    oid = _to_object_id(blog_id)

    blog = await db.blogs.find_one({"_id": oid})
    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    if blog.get("author_id") != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own blogs",
        )

    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    update_data["updated_at"] = datetime.now(timezone.utc)
    await db.blogs.update_one({"_id": oid}, {"$set": update_data})

    updated_blog = await db.blogs.find_one({"_id": oid})
    return await _build_blog_response(updated_blog)


@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(
    blog_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    """Delete a blog post.

    Only the original author may perform this action.
    """
    db = get_db()
    oid = _to_object_id(blog_id)

    blog = await db.blogs.find_one({"_id": oid})
    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    if blog.get("author_id") != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own blogs",
        )

    await db.blogs.delete_one({"_id": oid})

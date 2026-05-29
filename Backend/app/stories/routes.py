"""
Story routes: CRUD operations for user stories (drafts, published, unlisted).
"""

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.utils import get_current_user
from app.database import get_db
from app.stories.models import (
    StoryCreate,
    StoryListResponse,
    StoryResponse,
    StoryStatsResponse,
    StoryUpdate,
)

router = APIRouter(prefix="/api/stories", tags=["Stories"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_object_id(story_id: str) -> ObjectId:
    """Convert a string to a BSON ObjectId, raising 400 on failure."""
    try:
        return ObjectId(story_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid story id: {story_id}",
        )


def _calc_word_count(content: str) -> int:
    """Return the number of words in *content*."""
    return len(content.split())


def _calc_read_time(word_count: int) -> str:
    """Return a human-friendly read-time string (≈ 200 wpm)."""
    minutes = max(1, word_count // 200)
    return f"{minutes} min read"


async def _build_story_response(story: dict) -> StoryResponse:
    """Build a ``StoryResponse`` from a MongoDB story document.

    Resolves the author name from the users collection.
    """
    db = get_db()

    author_name = "Unknown"
    if story.get("author_id"):
        try:
            author = await db.users.find_one(
                {"_id": ObjectId(story["author_id"])},
                {"name": 1},
            )
            if author:
                author_name = author["name"]
        except (InvalidId, TypeError):
            pass

    return StoryResponse(
        id=str(story["_id"]),
        title=story["title"],
        content=story.get("content", ""),
        category=story.get("category", ""),
        image_url=story.get("image_url", ""),
        status=story.get("status", "draft"),
        author_id=story.get("author_id", ""),
        author_name=author_name,
        views=story.get("views", 0),
        reads=story.get("reads", 0),
        comments_count=story.get("comments_count", 0),
        word_count=story.get("word_count", 0),
        read_time=story.get("read_time", "1 min read"),
        created_at=story.get("created_at", datetime.now(timezone.utc)),
        updated_at=story.get("updated_at", datetime.now(timezone.utc)),
        published_at=story.get("published_at"),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/", response_model=StoryListResponse)
async def list_my_stories(
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by status: draft, published, or unlisted",
    ),
    current_user: dict = Depends(get_current_user),
) -> StoryListResponse:
    """Get the current user's stories, optionally filtered by status."""
    db = get_db()

    query: dict = {"author_id": current_user["_id"]}
    if status_filter:
        if status_filter not in {"draft", "published", "unlisted"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="status must be one of: draft, published, unlisted",
            )
        query["status"] = status_filter

    total = await db.stories.count_documents(query)
    cursor = db.stories.find(query).sort("updated_at", -1)

    stories: list[StoryResponse] = []
    async for story_doc in cursor:
        stories.append(await _build_story_response(story_doc))

    return StoryListResponse(stories=stories, total=total)


@router.post(
    "/",
    response_model=StoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_story(
    body: StoryCreate,
    current_user: dict = Depends(get_current_user),
) -> StoryResponse:
    """Create a new story (defaults to draft status).

    Automatically calculates ``word_count`` and ``read_time``.
    """
    db = get_db()
    now = datetime.now(timezone.utc)

    word_count = _calc_word_count(body.content)
    read_time = _calc_read_time(word_count)

    story_doc = {
        "title": body.title,
        "content": body.content,
        "category": body.category,
        "image_url": body.image_url,
        "status": "draft",
        "author_id": current_user["_id"],
        "views": 0,
        "reads": 0,
        "comments_count": 0,
        "word_count": word_count,
        "read_time": read_time,
        "created_at": now,
        "updated_at": now,
        "published_at": None,
    }

    result = await db.stories.insert_one(story_doc)
    story_doc["_id"] = result.inserted_id

    return await _build_story_response(story_doc)


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: str,
    current_user: dict | None = Depends(get_current_user),
) -> StoryResponse:
    """Get a single story by ID.

    If the requester is **not** the author the view count is incremented.
    """
    db = get_db()
    oid = _to_object_id(story_id)

    story = await db.stories.find_one({"_id": oid})
    if story is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )

    # Increment views only when a different user reads the story
    is_author = current_user and story.get("author_id") == current_user["_id"]
    if not is_author:
        await db.stories.update_one({"_id": oid}, {"$inc": {"views": 1}})
        story["views"] = story.get("views", 0) + 1

    return await _build_story_response(story)


@router.put("/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: str,
    body: StoryUpdate,
    current_user: dict = Depends(get_current_user),
) -> StoryResponse:
    """Update an existing story.

    Recalculates ``word_count`` and ``read_time`` when content changes.
    Only the original author may perform this action.
    """
    db = get_db()
    oid = _to_object_id(story_id)

    story = await db.stories.find_one({"_id": oid})
    if story is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )

    if story.get("author_id") != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own stories",
        )

    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    # Recalculate reading metrics when content changes
    if "content" in update_data:
        update_data["word_count"] = _calc_word_count(update_data["content"])
        update_data["read_time"] = _calc_read_time(update_data["word_count"])

    update_data["updated_at"] = datetime.now(timezone.utc)
    await db.stories.update_one({"_id": oid}, {"$set": update_data})

    updated_story = await db.stories.find_one({"_id": oid})
    return await _build_story_response(updated_story)


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
    story_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    """Delete a story.

    Only the original author may perform this action.
    """
    db = get_db()
    oid = _to_object_id(story_id)

    story = await db.stories.find_one({"_id": oid})
    if story is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )

    if story.get("author_id") != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own stories",
        )

    await db.stories.delete_one({"_id": oid})


@router.patch("/{story_id}/publish", response_model=StoryResponse)
async def publish_story(
    story_id: str,
    current_user: dict = Depends(get_current_user),
) -> StoryResponse:
    """Publish a story by setting status to 'published' and recording the timestamp.

    Only the original author may perform this action.
    """
    db = get_db()
    oid = _to_object_id(story_id)

    story = await db.stories.find_one({"_id": oid})
    if story is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )

    if story.get("author_id") != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only publish your own stories",
        )

    now = datetime.now(timezone.utc)
    await db.stories.update_one(
        {"_id": oid},
        {"$set": {"status": "published", "published_at": now, "updated_at": now}},
    )

    updated_story = await db.stories.find_one({"_id": oid})
    return await _build_story_response(updated_story)


@router.get("/{story_id}/stats", response_model=StoryStatsResponse)
async def get_story_stats(
    story_id: str,
    current_user: dict = Depends(get_current_user),
) -> StoryStatsResponse:
    """Get engagement stats for a story.

    Only the original author may view stats.
    """
    db = get_db()
    oid = _to_object_id(story_id)

    story = await db.stories.find_one({"_id": oid})
    if story is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )

    if story.get("author_id") != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view stats for your own stories",
        )

    return StoryStatsResponse(
        views=story.get("views", 0),
        reads=story.get("reads", 0),
        comments_count=story.get("comments_count", 0),
    )

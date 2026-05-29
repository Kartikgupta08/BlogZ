"""
Comments routes — create, list, and delete comments on stories.

All write endpoints are protected. The GET endpoint is public.
"""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.utils import get_current_user
from app.database import get_db
from app.comments.models import CommentCreate, CommentListResponse, CommentResponse

router = APIRouter(prefix="/api/comments", tags=["Comments"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _object_id_or_404(id_str: str, label: str = "Resource") -> ObjectId:
    """Convert a string to ObjectId, raising 400 on invalid format."""
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {label} ID format",
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/{story_id}", response_model=CommentListResponse)
async def get_story_comments(story_id: str) -> CommentListResponse:
    """Get all comments for a story, sorted newest first.

    Includes the author's display name resolved from the users collection.
    This endpoint is public (no authentication required).
    """
    db = get_db()
    story_oid = _object_id_or_404(story_id, "story")

    # Verify story exists
    story = await db.stories.find_one({"_id": story_oid})
    if story is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")

    total = await db.comments.count_documents({"story_id": story_id})
    cursor = db.comments.find({"story_id": story_id}).sort("created_at", -1)

    comments: list[CommentResponse] = []
    async for doc in cursor:
        # Resolve author name from users collection
        author = await db.users.find_one({"_id": ObjectId(doc["author_id"])})
        author_name = author.get("name", "Unknown") if author else "Unknown"

        comments.append(
            CommentResponse(
                id=str(doc["_id"]),
                story_id=doc["story_id"],
                author_id=doc["author_id"],
                author_name=author_name,
                content=doc["content"],
                created_at=doc["created_at"],
            )
        )

    return CommentListResponse(comments=comments, total=total)


@router.post("/{story_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    story_id: str,
    payload: CommentCreate,
    current_user: dict = Depends(get_current_user),
) -> CommentResponse:
    """Add a comment to a story.

    Also increments ``comments_count`` on the story document.
    """
    db = get_db()
    story_oid = _object_id_or_404(story_id, "story")

    # Verify story exists
    story = await db.stories.find_one({"_id": story_oid})
    if story is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")

    now = datetime.now(timezone.utc)
    comment_doc = {
        "story_id": story_id,
        "author_id": current_user["_id"],
        "content": payload.content,
        "created_at": now,
    }
    result = await db.comments.insert_one(comment_doc)

    # Increment comments_count on the story
    await db.stories.update_one({"_id": story_oid}, {"$inc": {"comments_count": 1}})

    return CommentResponse(
        id=str(result.inserted_id),
        story_id=story_id,
        author_id=current_user["_id"],
        author_name=current_user.get("name", "Unknown"),
        content=payload.content,
        created_at=now,
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    """Delete a comment. Only the comment author may delete it.

    Also decrements ``comments_count`` on the associated story.
    """
    db = get_db()
    oid = _object_id_or_404(comment_id, "comment")

    comment = await db.comments.find_one({"_id": oid})
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment["author_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not the comment author"
        )

    await db.comments.delete_one({"_id": oid})

    # Decrement comments_count on the story
    story_oid = _object_id_or_404(comment["story_id"], "story")
    await db.stories.update_one(
        {"_id": story_oid, "comments_count": {"$gt": 0}},
        {"$inc": {"comments_count": -1}},
    )

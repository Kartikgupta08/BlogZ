"""
Library routes — reading lists and bookmarks.

All endpoints are protected and scoped to the authenticated user.
"""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.utils import get_current_user
from app.database import get_db
from app.library.models import (
    BookmarkResponse,
    ListCreate,
    ListResponse,
    ListUpdate,
)

router = APIRouter(prefix="/api/library", tags=["Library"])


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
# Reading Lists
# ---------------------------------------------------------------------------


@router.get("/lists", response_model=list[ListResponse])
async def get_user_lists(
    current_user: dict = Depends(get_current_user),
) -> list[ListResponse]:
    """Get all reading lists belonging to the authenticated user.

    Each list includes a ``story_count`` indicating how many stories it contains.
    """
    db = get_db()
    user_id = current_user["_id"]

    cursor = db.lists.find({"user_id": user_id}).sort("created_at", -1)
    lists: list[ListResponse] = []
    async for doc in cursor:
        lists.append(
            ListResponse(
                id=str(doc["_id"]),
                name=doc["name"],
                description=doc.get("description", ""),
                user_id=doc["user_id"],
                story_count=len(doc.get("story_ids", [])),
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
            )
        )
    return lists


@router.post("/lists", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    payload: ListCreate,
    current_user: dict = Depends(get_current_user),
) -> ListResponse:
    """Create a new reading list for the authenticated user."""
    db = get_db()
    now = datetime.now(timezone.utc)

    doc = {
        "name": payload.name,
        "description": payload.description,
        "user_id": current_user["_id"],
        "story_ids": [],
        "created_at": now,
        "updated_at": now,
    }
    result = await db.lists.insert_one(doc)

    return ListResponse(
        id=str(result.inserted_id),
        name=doc["name"],
        description=doc["description"],
        user_id=doc["user_id"],
        story_count=0,
        created_at=now,
        updated_at=now,
    )


@router.put("/lists/{list_id}", response_model=ListResponse)
async def update_list(
    list_id: str,
    payload: ListUpdate,
    current_user: dict = Depends(get_current_user),
) -> ListResponse:
    """Update the name and/or description of a reading list.

    Only the list owner may perform this action.
    """
    db = get_db()
    oid = _object_id_or_404(list_id, "list")

    existing = await db.lists.find_one({"_id": oid})
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    if existing["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the list owner")

    update_fields: dict = {"updated_at": datetime.now(timezone.utc)}
    if payload.name is not None:
        update_fields["name"] = payload.name
    if payload.description is not None:
        update_fields["description"] = payload.description

    await db.lists.update_one({"_id": oid}, {"$set": update_fields})
    updated = await db.lists.find_one({"_id": oid})

    return ListResponse(
        id=str(updated["_id"]),
        name=updated["name"],
        description=updated.get("description", ""),
        user_id=updated["user_id"],
        story_count=len(updated.get("story_ids", [])),
        created_at=updated["created_at"],
        updated_at=updated["updated_at"],
    )


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
    list_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    """Delete a reading list. Only the list owner may perform this action."""
    db = get_db()
    oid = _object_id_or_404(list_id, "list")

    existing = await db.lists.find_one({"_id": oid})
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    if existing["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the list owner")

    await db.lists.delete_one({"_id": oid})


# ---------------------------------------------------------------------------
# List ↔ Story membership
# ---------------------------------------------------------------------------


@router.post(
    "/lists/{list_id}/stories",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
)
async def add_story_to_list(
    list_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Add a story to a reading list.

    Request body must contain ``{ "story_id": "<id>" }``.
    """
    db = get_db()
    oid = _object_id_or_404(list_id, "list")
    story_id = body.get("story_id")
    if not story_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="story_id is required"
        )

    # Verify list exists and belongs to user
    existing = await db.lists.find_one({"_id": oid})
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    if existing["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the list owner")

    # Verify story exists
    story_oid = _object_id_or_404(story_id, "story")
    story = await db.stories.find_one({"_id": story_oid})
    if story is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")

    # Add story (idempotent — $addToSet prevents duplicates)
    await db.lists.update_one(
        {"_id": oid},
        {
            "$addToSet": {"story_ids": story_id},
            "$set": {"updated_at": datetime.now(timezone.utc)},
        },
    )
    return {"message": "Story added to list"}


@router.delete("/lists/{list_id}/stories/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_story_from_list(
    list_id: str,
    story_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    """Remove a story from a reading list."""
    db = get_db()
    oid = _object_id_or_404(list_id, "list")

    existing = await db.lists.find_one({"_id": oid})
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    if existing["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the list owner")

    await db.lists.update_one(
        {"_id": oid},
        {
            "$pull": {"story_ids": story_id},
            "$set": {"updated_at": datetime.now(timezone.utc)},
        },
    )


# ---------------------------------------------------------------------------
# Bookmarks
# ---------------------------------------------------------------------------


@router.get("/bookmarks", response_model=list[BookmarkResponse])
async def get_bookmarks(
    current_user: dict = Depends(get_current_user),
) -> list[BookmarkResponse]:
    """Get all bookmarks for the authenticated user, including story details."""
    db = get_db()
    user_id = current_user["_id"]

    cursor = db.bookmarks.find({"user_id": user_id}).sort("created_at", -1)
    bookmarks: list[BookmarkResponse] = []
    async for doc in cursor:
        # Fetch associated story for title and author info
        story = await db.stories.find_one({"_id": ObjectId(doc["story_id"])})
        if story is None:
            continue  # skip dangling bookmarks

        # Resolve author name
        author = await db.users.find_one({"_id": ObjectId(story["author_id"])})
        author_name = author.get("name", "Unknown") if author else "Unknown"

        bookmarks.append(
            BookmarkResponse(
                id=str(doc["_id"]),
                story_id=doc["story_id"],
                story_title=story.get("title", ""),
                story_author=author_name,
                created_at=doc["created_at"],
            )
        )
    return bookmarks


@router.post("/bookmarks/{story_id}", status_code=status.HTTP_201_CREATED, response_model=dict)
async def bookmark_story(
    story_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Bookmark a story for the authenticated user.

    Returns 409 if the story is already bookmarked.
    """
    db = get_db()
    user_id = current_user["_id"]
    story_oid = _object_id_or_404(story_id, "story")

    # Verify story exists
    story = await db.stories.find_one({"_id": story_oid})
    if story is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")

    # Check for duplicate
    existing = await db.bookmarks.find_one({"user_id": user_id, "story_id": story_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Story already bookmarked"
        )

    await db.bookmarks.insert_one(
        {
            "user_id": user_id,
            "story_id": story_id,
            "created_at": datetime.now(timezone.utc),
        }
    )
    return {"message": "Story bookmarked"}


@router.delete("/bookmarks/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bookmark(
    story_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    """Remove a bookmark for the authenticated user."""
    db = get_db()
    user_id = current_user["_id"]

    result = await db.bookmarks.delete_one({"user_id": user_id, "story_id": story_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

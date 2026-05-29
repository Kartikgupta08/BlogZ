"""
User profile, follow/unfollow, and stats routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.database import get_db
from app.auth.utils import get_current_user
from app.auth.models import UserResponse
from app.users.models import FollowResponse, ProfileUpdate, UserStats

router = APIRouter(prefix="/api/users", tags=["Users"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _user_response(user: dict) -> UserResponse:
    """Build a ``UserResponse`` from a MongoDB user document."""
    from datetime import datetime, timezone

    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        bio=user.get("bio", ""),
        avatar=user.get("avatar", ""),
        followers_count=len(user.get("followers", [])),
        following_count=len(user.get("following", [])),
        created_at=user.get("created_at", datetime.now(timezone.utc)),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    """Return the authenticated user's full profile."""
    return _user_response(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    body: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    """Update the authenticated user's profile fields.

    Only fields present (non-``None``) in the request body are updated.
    """
    db = get_db()

    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    await db.users.update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": update_data},
    )

    updated_user = await db.users.find_one({"_id": ObjectId(current_user["_id"])})
    return _user_response(updated_user)


@router.post("/{user_id}/follow", response_model=FollowResponse)
async def follow_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
) -> FollowResponse:
    """Follow another user.

    Adds the target user to the current user's *following* list and the
    current user to the target user's *followers* list.
    """
    db = get_db()

    if user_id == current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself",
        )

    target_user = await db.users.find_one({"_id": ObjectId(user_id)})
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    current_uid = current_user["_id"]

    # Check if already following
    if ObjectId(current_uid) in target_user.get("followers", []):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already following this user",
        )

    # Add to target's followers
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"followers": ObjectId(current_uid)}},
    )
    # Add to current user's following
    await db.users.update_one(
        {"_id": ObjectId(current_uid)},
        {"$addToSet": {"following": ObjectId(user_id)}},
    )

    updated_target = await db.users.find_one({"_id": ObjectId(user_id)})
    return FollowResponse(
        message="Successfully followed user",
        followers_count=len(updated_target.get("followers", [])),
    )


@router.post("/{user_id}/unfollow", response_model=FollowResponse)
async def unfollow_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
) -> FollowResponse:
    """Unfollow a user.

    Removes the target user from the current user's *following* list and
    the current user from the target user's *followers* list.
    """
    db = get_db()

    if user_id == current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot unfollow yourself",
        )

    target_user = await db.users.find_one({"_id": ObjectId(user_id)})
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    current_uid = current_user["_id"]

    if ObjectId(current_uid) not in target_user.get("followers", []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not following this user",
        )

    # Remove from target's followers
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"followers": ObjectId(current_uid)}},
    )
    # Remove from current user's following
    await db.users.update_one(
        {"_id": ObjectId(current_uid)},
        {"$pull": {"following": ObjectId(user_id)}},
    )

    updated_target = await db.users.find_one({"_id": ObjectId(user_id)})
    return FollowResponse(
        message="Successfully unfollowed user",
        followers_count=len(updated_target.get("followers", [])),
    )


@router.get("/stats", response_model=UserStats)
async def get_stats(
    current_user: dict = Depends(get_current_user),
) -> UserStats:
    """Return aggregated statistics for the authenticated user.

    Totals are computed from the ``stories`` collection (views, reads,
    story count) and the user document (followers, following).
    """
    db = get_db()

    pipeline = [
        {"$match": {"author_id": current_user["_id"]}},
        {
            "$group": {
                "_id": None,
                "total_stories": {"$sum": 1},
                "total_views": {"$sum": {"$ifNull": ["$views", 0]}},
                "total_reads": {"$sum": {"$ifNull": ["$reads", 0]}},
            }
        },
    ]

    cursor = db.stories.aggregate(pipeline)
    results = await cursor.to_list(length=1)

    if results:
        agg = results[0]
        total_stories = agg["total_stories"]
        total_views = agg["total_views"]
        total_reads = agg["total_reads"]
    else:
        total_stories = 0
        total_views = 0
        total_reads = 0

    return UserStats(
        total_stories=total_stories,
        total_views=total_views,
        total_reads=total_reads,
        followers_count=len(current_user.get("followers", [])),
        following_count=len(current_user.get("following", [])),
    )

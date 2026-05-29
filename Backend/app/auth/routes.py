"""
Authentication routes: signup, login, and current-user retrieval.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.database import get_db
from app.auth.models import TokenResponse, UserCreate, UserLogin, UserResponse
from app.auth.utils import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _user_response(user: dict) -> UserResponse:
    """Build a ``UserResponse`` from a MongoDB user document."""
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


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(body: UserCreate) -> TokenResponse:
    """Register a new user account.

    Returns an access token and user profile on success.
    Raises **409** if the email is already registered.
    """
    db = get_db()

    user_doc = {
        "name": body.name,
        "email": body.email,
        "password": hash_password(body.password),
        "bio": "",
        "avatar": "",
        "followers": [],
        "following": [],
        "created_at": datetime.now(timezone.utc),
    }

    try:
        result = await db.users.insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user_doc["_id"] = result.inserted_id
    token = create_access_token({"sub": str(result.inserted_id)})
    return TokenResponse(access_token=token, user=_user_response(user_doc))


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin) -> TokenResponse:
    """Authenticate with email and password.

    Returns an access token and user profile on success.
    Raises **401** for invalid credentials.
    """
    db = get_db()
    user = await db.users.find_one({"email": body.email})

    if user is None or not verify_password(body.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user["_id"])})
    return TokenResponse(access_token=token, user=_user_response(user))


@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return _user_response(current_user)

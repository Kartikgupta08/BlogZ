"""
BlogZ Backend — FastAPI Application Entry Point.

A complete REST API for the BlogZ blogging platform.
Run with: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="BlogZ API",
    description="REST API for the BlogZ blogging platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health Check ---
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Check if the API is running."""
    return {"status": "healthy", "message": "BlogZ API is running 🚀"}


# --- Import and include routers ---
# These imports are deferred to avoid circular imports
from app.auth.routes import router as auth_router
from app.blogs.routes import router as blogs_router
from app.stories.routes import router as stories_router
from app.users.routes import router as users_router
from app.library.routes import router as library_router
from app.comments.routes import router as comments_router

app.include_router(auth_router)
app.include_router(blogs_router)
app.include_router(stories_router)
app.include_router(users_router)
app.include_router(library_router)
app.include_router(comments_router)

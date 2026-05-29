"""
MongoDB async client using Motor.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

# Global client and database references
client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """Connect to MongoDB and create indexes."""
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]

    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.stories.create_index([("author_id", 1), ("status", 1)])
    await db.stories.create_index([("category", 1), ("status", 1)])
    await db.stories.create_index("created_at")
    await db.comments.create_index("story_id")
    await db.bookmarks.create_index([("user_id", 1), ("story_id", 1)], unique=True)
    await db.lists.create_index("user_id")

    print(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")


async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("🔌 MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return db

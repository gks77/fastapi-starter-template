from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create MongoDB connection."""
    try:
        mongodb.client = AsyncIOMotorClient(settings.get_mongodb_url())
        mongodb.database = mongodb.client[settings.MONGODB_DATABASE]
        await mongodb.client.admin.command('ping')
        logger.info("Connected to MongoDB")
    except ConnectionFailure as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close MongoDB connection."""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")

async def get_mongo_db():
    """Get MongoDB database instance."""
    return mongodb.database

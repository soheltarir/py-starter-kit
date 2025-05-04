from typing import Optional

import structlog
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import (
    ServerSelectionTimeoutError,
    OperationFailure,
    ConfigurationError,
)

from src.infrastructure.mongodb.model_registry import MONGODB_MODELS

logger = structlog.stdlib.get_logger()


class MongoDBConnectionError(Exception):
    """Raised when connection to MongoDB fails."""

    pass


class MongoDBAuthenticationError(Exception):
    """Raised when MongoDB authentication fails."""

    pass


class BeanieClient:
    mongo_uri: str
    mongo_database: str
    client: Optional[AsyncIOMotorClient]
    db: Optional[AsyncIOMotorDatabase]

    def __init__(
        self,
        mongo_uri: str,
        mongo_database: str,
        client: Optional[AsyncIOMotorClient] = None,
    ):
        self.mongo_uri = mongo_uri
        self.mongo_database = mongo_database
        self.client = client if client else None
        self.db = None

    async def initialize(self):
        try:
            if self.client is None:
                self.client = AsyncIOMotorClient(
                    self.mongo_uri, serverSelectionTimeoutMS=5000  # 5-second timeout
                )
                # Test the connection
                await self.client.server_info()

            self.db = self.client[self.mongo_database]

            # Initialize Beanie
            logger.info("Attempting to connect to MongoDB")
            await init_beanie(database=self.db, document_models=MONGODB_MODELS)
            logger.info("Successfully connected to MongoDB")

        except ServerSelectionTimeoutError as e:
            logger.error("Failed to connect to MongoDB server", error=str(e))
            raise MongoDBConnectionError(f"Could not connect to MongoDB: {str(e)}")

        except OperationFailure as e:
            if e.code == 13:  # Authentication failed error code
                logger.error("MongoDB authentication failed")
                raise MongoDBAuthenticationError("Authentication failed")
            logger.error("MongoDB operation failed", exc_info=e)
            raise MongoDBConnectionError(f"Operation failed: {str(e)}")

        except ConfigurationError as e:
            logger.error("MongoDB configuration error", error=str(e))
            raise MongoDBConnectionError(f"Invalid MongoDB configuration: {str(e)}")

        except Exception as e:
            logger.error("Unexpected error while connecting to MongoDB", error=str(e))
            raise MongoDBConnectionError(f"Unexpected error: {str(e)}")

    async def close(self):
        try:
            if self.client:
                self.client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error("Error while closing MongoDB connection", error=str(e))
        finally:
            self.client = None
            self.db = None

    async def ping(self) -> bool:
        """Test if the connection is alive."""
        try:
            if self.client:
                await self.client.admin.command("ping")
                return True
            return False
        except Exception as e:
            logger.error("Failed to ping MongoDB", error=str(e))
            return False

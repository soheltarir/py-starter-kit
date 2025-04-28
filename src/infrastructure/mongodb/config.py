from typing import Optional, Union

import structlog
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from mongomock_motor import AsyncMongoMockClient

from src.infrastructure.mongodb.model_registry import MONGODB_MODELS

logger = structlog.get_logger(__name__)


class BeanieClient:
    mongo_uri: str
    mongo_database: str
    client: Optional[Union[AsyncIOMotorClient, AsyncMongoMockClient]]
    db: Optional[AsyncIOMotorDatabase]

    def __init__(
            self, 
            mongo_uri: str, 
            mongo_database: str,
            # Optional client to use for testing
            client: Optional[Union[AsyncIOMotorClient, AsyncMongoMockClient]] = None
        ):
        self.mongo_uri = mongo_uri
        self.mongo_database = mongo_database
        self.client = client if client else None
        self.db = None

    async def initialize(self):
        if self.client is None:
            self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.mongo_database]

        # Initialize Beanie
        logger.info("Attempting to connect to MongoDB")
        await init_beanie(
            database=self.db,
            document_models=MONGODB_MODELS
        )

    async def close(self):
        if self.client:
            self.client.close()
        self.client = None
        self.db = None

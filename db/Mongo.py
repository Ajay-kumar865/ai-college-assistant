import os
import logging
import certifi
from pymongo import MongoClient

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in .env")


class MongoDB:
    def __init__(self):
        self.client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=20000,
        )

        self.db = self.client["college_ai"]

        self.logs = self.db["logs"]
        self.queries = self.db["queries"]

        self._health_check()

    def _health_check(self):
        try:
            self.client.admin.command("ping")
            logger.info("MongoDB connected")
        except Exception as e:
            raise RuntimeError(f"MongoDB connection failed: {e}")

    def log_query(self, data: dict):
        self.queries.insert_one(data)

    def log_response(self, data: dict):
        self.logs.insert_one(data)


mongo = MongoDB()

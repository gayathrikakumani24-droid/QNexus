"""
MongoDB helper module. Connects on demand using PyMongo.
"""
from app.core.database import get_mongo_db, get_mongo_client, close_mongo_connection

__all__ = ["get_mongo_db", "get_mongo_client", "close_mongo_connection"]

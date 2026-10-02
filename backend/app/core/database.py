from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from app.core.config import settings
import logging

logger = logging.getLogger("qnexus.database")

_mongo_client: Optional[MongoClient] = None
_mongo_db: Optional[Database] = None

def _configure_dns_resolver():
    """Configures dnspython default resolver with system nameservers and public DNS fallbacks."""
    try:
        import dns.resolver
        res = dns.resolver.Resolver(configure=True)
        sys_nameservers = list(res.nameservers)
        for ns in ['8.8.8.8', '1.1.1.1', '8.8.4.4']:
            if ns not in sys_nameservers:
                sys_nameservers.append(ns)
        res.nameservers = sys_nameservers
        res.lifetime = 15.0
        dns.resolver.default_resolver = res
    except Exception as e:
        logger.debug(f"Could not customize dnspython resolver: {e}")

def get_mongo_client() -> MongoClient:
    """Returns PyMongo client instance, lazily initialized on demand."""
    global _mongo_client
    if _mongo_client is None:
        _configure_dns_resolver()
        logger.info(f"Initializing PyMongo client connection to {settings.MONGODB_URL}")
        _mongo_client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=10000, connectTimeoutMS=10000)
    return _mongo_client

def get_mongo_db() -> Database:
    """Returns PyMongo database instance, lazily initialized on demand."""
    global _mongo_db
    if _mongo_db is None:
        client = get_mongo_client()
        _mongo_db = client[settings.MONGODB_DB_NAME]
    return _mongo_db

def close_mongo_connection():
    global _mongo_client, _mongo_db
    if _mongo_client is not None:
        logger.info("Closing PyMongo client connection")
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None

"""
Deprecated: Qnexus has migrated to Pinecone Cloud.
Use app.core.pinecone instead.
"""
import logging
from app.core.pinecone import get_pinecone_index, ensure_pinecone_index, get_pinecone_client

logger = logging.getLogger("qnexus.qdrant")

def get_qdrant_client():
    logger.warning("get_qdrant_client is deprecated. Use get_pinecone_index() or get_pinecone_client().")
    return get_pinecone_index()

def ensure_qdrant_collection(*args, **kwargs):
    logger.warning("ensure_qdrant_collection is deprecated. Use ensure_pinecone_index().")
    return ensure_pinecone_index()

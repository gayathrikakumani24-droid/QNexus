"""
Backward compatibility wrapper. Qdrant has been replaced by Pinecone Cloud.
Use PineconeService directly in new code.
"""
import logging
from app.services.pinecone_service import PineconeService

logger = logging.getLogger("qnexus.services.qdrant_service")

class QdrantService(PineconeService):
    def __init__(self, *args, **kwargs):
        logger.warning("QdrantService is deprecated and now proxies to PineconeService.")
        super().__init__(*args, **kwargs)

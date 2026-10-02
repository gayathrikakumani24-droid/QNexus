from typing import Optional, Any
import logging
from app.core.config import settings

logger = logging.getLogger("qnexus.pinecone")

_pinecone_client: Optional[Any] = None

def get_pinecone_client() -> Optional[Any]:
    """
    Returns a Pinecone client instance, lazily initialized on demand.
    """
    global _pinecone_client
    if _pinecone_client is None:
        try:
            from pinecone import Pinecone
            api_key = settings.PINECONE_API_KEY.strip()
            if not api_key:
                logger.warning("PINECONE_API_KEY is not configured in settings or .env.")
                return None

            logger.info("Initializing Pinecone Cloud client...")
            _pinecone_client = Pinecone(api_key=api_key)
            logger.info("Pinecone client initialized successfully.")
        except ImportError:
            logger.warning("The 'pinecone' package is not installed. Please install 'pinecone>=5.0.0'.")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {e}")
            return None

    return _pinecone_client


def ensure_pinecone_index(
    index_name: Optional[str] = None,
    vector_size: int = 384,
    metric: str = "cosine"
) -> bool:
    """
    Checks if target Pinecone index exists; if not, creates a serverless index.
    """
    client = get_pinecone_client()
    if client is None:
        logger.warning("Pinecone client not available; skipping ensure_pinecone_index.")
        return False

    target_index = index_name or settings.PINECONE_INDEX_NAME

    try:
        from pinecone import ServerlessSpec

        # Check existing index names
        existing_indexes = [idx["name"] if isinstance(idx, dict) else idx.name for idx in client.list_indexes()]
        
        if target_index not in existing_indexes:
            logger.info(
                f"Creating Pinecone Serverless Index: '{target_index}' "
                f"(dim={vector_size}, metric={metric}, cloud={settings.PINECONE_CLOUD}, region={settings.PINECONE_REGION})..."
            )
            client.create_index(
                name=target_index,
                dimension=vector_size,
                metric=metric,
                spec=ServerlessSpec(
                    cloud=settings.PINECONE_CLOUD,
                    region=settings.PINECONE_REGION
                )
            )
            logger.info(f"Pinecone index '{target_index}' created successfully.")
        else:
            logger.info(f"Pinecone index '{target_index}' already exists and is ready.")
        return True

    except Exception as e:
        logger.error(f"Failed to ensure Pinecone index '{target_index}': {e}")
        return False


def get_pinecone_index(index_name: Optional[str] = None) -> Optional[Any]:
    """
    Returns the Pinecone Index handle for querying and upserting vectors.
    """
    client = get_pinecone_client()
    if client is None:
        return None

    target_index = index_name or settings.PINECONE_INDEX_NAME
    try:
        return client.Index(target_index)
    except Exception as e:
        logger.error(f"Failed to obtain Pinecone Index '{target_index}': {e}")
        return None

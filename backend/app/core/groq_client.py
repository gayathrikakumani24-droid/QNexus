from typing import Optional
from groq import Groq
from app.core.config import settings
import logging

logger = logging.getLogger("qnexus.groq")

_groq_client: Optional[Groq] = None

def get_groq_client() -> Groq:
    """Returns Groq SDK client instance, lazily initialized on demand."""
    global _groq_client
    if _groq_client is None:
        logger.info("Initializing Groq client instance")
        api_key = settings.GROQ_API_KEY if settings.GROQ_API_KEY else "dummy_key_placeholder"
        _groq_client = Groq(api_key=api_key)
    return _groq_client

import json
import time
import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.groq_client import get_groq_client

logger = logging.getLogger("qnexus.services.llm_client")

class LLMClient:
    def __init__(self, model: Optional[str] = None):
        self.model = model or settings.GROQ_MODEL
        self.max_retries = 3
        self.initial_backoff_seconds = 1.0

    def generate_json_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1
    ) -> Optional[Dict[str, Any]]:
        """
        Calls Groq LLM with JSON response format, exponential backoff, and rate limit handling.
        Returns parsed JSON dict or None on failure.
        """
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not configured. LLM completion skipped.")
            return None

        client = get_groq_client()
        backoff = self.initial_backoff_seconds

        for attempt in range(1, self.max_retries + 1):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=temperature
                )
                raw_content = response.choices[0].message.content
                parsed_json = json.loads(raw_content)
                return parsed_json

            except Exception as e:
                err_str = str(e)
                logger.warning(
                    f"Groq API call attempt {attempt}/{self.max_retries} failed: {err_str}"
                )
                
                # Check for rate limit or transient error to apply backoff
                if "429" in err_str or "rate limit" in err_str.lower() or attempt < self.max_retries:
                    time.sleep(backoff)
                    backoff *= 2  # Exponential backoff
                else:
                    logger.error(f"Groq API call exhausted retries: {err_str}")
                    return None

        return None

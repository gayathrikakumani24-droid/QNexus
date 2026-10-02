import logging
from typing import List, Dict, Any, Optional, Union
from app.core.config import settings
from app.schemas.question_schema import QuestionResponse

logger = logging.getLogger("qnexus.services.embedding")

class EmbeddingService:
    _instance: Optional["EmbeddingService"] = None
    _model: Optional[Any] = None

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME

    def _load_model(self):
        """Loads SentenceTransformer model once on demand and reuses it."""
        if EmbeddingService._model is None:
            import os
            os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
            os.environ.setdefault("OMP_NUM_THREADS", "2")

            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer embedding model: {self.model_name}")
            EmbeddingService._model = SentenceTransformer(self.model_name, device="cpu")
            logger.info("SentenceTransformer model loaded successfully.")

    @property
    def model(self):
        if EmbeddingService._model is None:
            self._load_model()
        return EmbeddingService._model

    @staticmethod
    def format_question_for_embedding(
        content: str,
        subject: Optional[str] = None,
        chapter: Optional[str] = None,
        concept: Optional[str] = None
    ) -> str:
        """
        Constructs rich contextual text representation combining subject, chapter, concept, and question content.
        """
        parts = []
        if subject and subject != "Unknown":
            parts.append(f"Subject: {subject}")
        if chapter and chapter != "Unknown":
            parts.append(f"Chapter: {chapter}")
        if concept and concept != "Unknown":
            parts.append(f"Concept: {concept}")
        
        context_prefix = " | ".join(parts)
        if context_prefix:
            return f"{context_prefix}\nQuestion: {content.strip()}"
        return content.strip()

    def embed_text(self, text: str) -> List[float]:
        """
        Generates a single 384-dimensional normalized embedding vector.
        """
        try:
            vector = self.model.encode(
                text,
                normalize_embeddings=True,
                show_progress_bar=False
            )
        except Exception as e:
            logger.warning(f"Error encoding with cached model: {e}. Reloading model on cpu...")
            from sentence_transformers import SentenceTransformer
            EmbeddingService._model = SentenceTransformer(self.model_name, device="cpu")
            vector = EmbeddingService._model.encode(
                text,
                normalize_embeddings=True,
                show_progress_bar=False
            )
        return vector.tolist()

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generates 384-dimensional normalized embedding vectors in batches.
        """
        if not texts:
            return []
        
        try:
            vectors = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=False
            )
        except Exception as e:
            logger.warning(f"Error encoding batch with cached model: {e}. Reloading model on cpu...")
            from sentence_transformers import SentenceTransformer
            EmbeddingService._model = SentenceTransformer(self.model_name, device="cpu")
            vectors = EmbeddingService._model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=False
            )
        return [v.tolist() for v in vectors]

    def embed_questions(
        self,
        questions: List[Union[QuestionResponse, Dict[str, Any]]],
        batch_size: int = 32,
        existing_vector_ids: Optional[set] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates embeddings for a list of questions, avoiding re-embedding already processed IDs.
        Returns list of structured records containing question_id, embedding, and Qdrant payload.
        Vectors are NOT stored in MongoDB.
        """
        existing_ids = existing_vector_ids or set()
        
        # Filter out questions that have already been embedded
        questions_to_embed = []
        for q in questions:
            q_id = q.question_id if hasattr(q, "question_id") else q["question_id"]
            if q_id not in existing_ids:
                questions_to_embed.append(q)

        if not questions_to_embed:
            logger.info("All questions already embedded. Skipping embedding computation.")
            return []

        formatted_texts = []
        for q in questions_to_embed:
            if hasattr(q, "content"):
                text = self.format_question_for_embedding(
                    content=q.content,
                    subject=q.subject,
                    chapter=q.chapter,
                    concept=q.concept
                )
            else:
                text = self.format_question_for_embedding(
                    content=q.get("content", ""),
                    subject=q.get("subject"),
                    chapter=q.get("chapter"),
                    concept=q.get("concept")
                )
            formatted_texts.append(text)

        logger.info(f"Generating embeddings for {len(formatted_texts)} questions with batch_size={batch_size}...")
        embeddings = self.embed_texts(formatted_texts, batch_size=batch_size)

        records = []
        for q, emb in zip(questions_to_embed, embeddings):
            if hasattr(q, "question_id"):
                record = {
                    "question_id": q.question_id,
                    "embedding": emb,
                    "payload": {
                        "question_id": q.question_id,
                        "paper_id": q.paper_id,
                        "subject": q.subject,
                        "chapter": q.chapter,
                        "concept": q.concept,
                        "difficulty": q.difficulty,
                        "question_type": q.question_type,
                        "year": q.year,
                        "shift": q.shift,
                    }
                }
            else:
                record = {
                    "question_id": q["question_id"],
                    "embedding": emb,
                    "payload": {
                        "question_id": q.get("question_id"),
                        "paper_id": q.get("paper_id"),
                        "subject": q.get("subject"),
                        "chapter": q.get("chapter"),
                        "concept": q.get("concept"),
                        "difficulty": q.get("difficulty"),
                        "question_type": q.get("question_type"),
                        "year": q.get("year"),
                        "shift": q.get("shift"),
                    }
                }
            records.append(record)

        logger.info(f"Successfully prepared {len(records)} embedding records.")
        return records

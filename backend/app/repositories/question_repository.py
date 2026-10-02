from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from app.schemas.question_schema import QuestionCreate, QuestionResponse
import logging

logger = logging.getLogger("qnexus.repositories.question")

class QuestionRepository:
    def __init__(self, db: Database):
        self.collection = db.questions

    def create_question(self, question: QuestionCreate) -> QuestionResponse:
        """
        Inserts a single question into MongoDB.
        Handles duplicate inserts safely by returning existing question if question_id exists.
        Ensures vector embeddings are NOT stored in MongoDB.
        """
        q_dict = question.model_dump()
        q_dict["_id"] = question.question_id
        q_dict["created_at"] = datetime.now(timezone.utc)

        # Explicitly remove vector keys if present to obey rule 9 & 10
        q_dict.pop("vector", None)
        q_dict.pop("embedding", None)

        self.collection.replace_one(
            {"_id": question.question_id},
            q_dict,
            upsert=True
        )
        logger.info(f"Saved/Updated question: {question.question_id}")
        return QuestionResponse(**q_dict)

    def bulk_create_questions(self, questions: List[QuestionCreate]) -> List[QuestionResponse]:
        """
        Inserts multiple question documents into MongoDB safely.
        """
        inserted = []
        for q in questions:
            res = self.create_question(q)
            inserted.append(res)
        return inserted

    def get_question(self, question_id: str) -> Optional[QuestionResponse]:
        """
        Retrieves a single question document by question_id.
        """
        doc = self.collection.find_one({"question_id": question_id})
        if not doc:
            return None
        return QuestionResponse(**doc)

    def get_questions_by_ids(self, question_ids: List[str]) -> List[QuestionResponse]:
        """
        Retrieves multiple questions matching a list of stable question_ids (preserving order).
        """
        if not question_ids:
            return []
        
        cursor = self.collection.find({"question_id": {"$in": question_ids}})
        doc_map = {doc["question_id"]: QuestionResponse(**doc) for doc in cursor}
        
        results = []
        for q_id in question_ids:
            if q_id in doc_map:
                results.append(doc_map[q_id])
        return results

    def list_questions(
        self,
        subject: Optional[str] = None,
        chapter: Optional[str] = None,
        concept: Optional[str] = None,
        difficulty: Optional[str] = None,
        year: Optional[int] = None,
        shift: Optional[str] = None,
        paper_id: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[QuestionResponse]:
        """
        Queries questions with faceted metadata filtering and pagination.
        """
        query_filter: Dict[str, Any] = {}
        if subject:
            query_filter["subject"] = subject
        if chapter:
            query_filter["chapter"] = chapter
        if concept:
            query_filter["concept"] = concept
        if difficulty:
            query_filter["difficulty"] = difficulty
        if year:
            query_filter["year"] = year
        if shift:
            query_filter["shift"] = shift
        if paper_id:
            query_filter["paper_id"] = paper_id

        cursor = self.collection.find(query_filter).skip(skip).limit(limit)
        return [QuestionResponse(**doc) for doc in cursor]

    def update_question_metadata(
        self, question_id: str, metadata: Dict[str, Any]
    ) -> Optional[QuestionResponse]:
        """
        Updates subject, chapter, concept, difficulty, or solution metadata for a question.
        """
        metadata.pop("vector", None)
        metadata.pop("embedding", None)

        doc = self.collection.find_one_and_update(
            {"question_id": question_id},
            {"$set": metadata},
            return_document=True
        )
        if not doc:
            return None
        return QuestionResponse(**doc)

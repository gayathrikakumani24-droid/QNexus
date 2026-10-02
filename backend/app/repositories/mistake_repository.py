import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pymongo.database import Database

logger = logging.getLogger("qnexus.repositories.mistake")

class MistakeRepository:
    def __init__(self, db: Database):
        self.db = db
        self.mistakes = db.mistakes

    def create_or_update_mistake(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates or updates a mistake document for a specific user and question.
        """
        user_id = data.get("user_id", "default_user")
        question_id = data.get("question_id")

        existing = self.mistakes.find_one({"user_id": user_id, "question_id": question_id})
        now = datetime.now(timezone.utc)

        if existing:
            mistake_id = existing["mistake_id"]
            update_fields = {
                "mistake_tag": data.get("mistake_tag", existing.get("mistake_tag", "Conceptual Gap")),
                "user_notes": data.get("user_notes", existing.get("user_notes")),
                "review_status": data.get("review_status", existing.get("review_status", "Needs Review")),
                "user_answer": data.get("user_answer", existing.get("user_answer")),
                "correct_answer": data.get("correct_answer", existing.get("correct_answer")),
                "subject": data.get("subject", existing.get("subject")),
                "chapter": data.get("chapter", existing.get("chapter")),
                "concept": data.get("concept", existing.get("concept")),
                "updated_at": now
            }
            self.mistakes.update_one({"mistake_id": mistake_id}, {"$set": update_fields})
            logger.info(f"Updated existing mistake record {mistake_id} for question {question_id}.")
            return self.mistakes.find_one({"mistake_id": mistake_id})

        mistake_id = f"MST_{uuid.uuid4().hex[:12].upper()}"
        doc = {
            "_id": mistake_id,
            "mistake_id": mistake_id,
            "user_id": user_id,
            "question_id": question_id,
            "subject": data.get("subject"),
            "chapter": data.get("chapter"),
            "concept": data.get("concept"),
            "user_answer": data.get("user_answer"),
            "correct_answer": data.get("correct_answer"),
            "mistake_tag": data.get("mistake_tag", "Conceptual Gap"),
            "user_notes": data.get("user_notes"),
            "review_status": data.get("review_status", "Needs Review"),
            "created_at": now,
            "updated_at": now
        }
        self.mistakes.insert_one(doc)
        logger.info(f"Created new mistake record {mistake_id} for user {user_id} and question {question_id}.")
        return doc

    def get_mistake(self, mistake_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a mistake by its mistake_id.
        """
        return self.mistakes.find_one({"mistake_id": mistake_id})

    def list_mistakes(
        self,
        user_id: Optional[str] = "default_user",
        subject: Optional[str] = None,
        chapter: Optional[str] = None,
        mistake_tag: Optional[str] = None,
        review_status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Queries mistake records with optional filters.
        """
        filter_query: Dict[str, Any] = {}
        if user_id:
            filter_query["user_id"] = user_id
        if subject and subject != "All":
            filter_query["subject"] = subject
        if chapter and chapter != "All":
            filter_query["chapter"] = chapter
        if mistake_tag and mistake_tag != "All":
            filter_query["mistake_tag"] = mistake_tag
        if review_status and review_status != "All":
            filter_query["review_status"] = review_status

        cursor = self.mistakes.find(filter_query).sort("created_at", -1).skip(offset).limit(limit)
        return list(cursor)

    def count_mistakes(
        self,
        user_id: Optional[str] = "default_user",
        subject: Optional[str] = None,
        chapter: Optional[str] = None,
        mistake_tag: Optional[str] = None,
        review_status: Optional[str] = None
    ) -> int:
        """
        Counts mistake records matching query filters.
        """
        filter_query: Dict[str, Any] = {}
        if user_id:
            filter_query["user_id"] = user_id
        if subject and subject != "All":
            filter_query["subject"] = subject
        if chapter and chapter != "All":
            filter_query["chapter"] = chapter
        if mistake_tag and mistake_tag != "All":
            filter_query["mistake_tag"] = mistake_tag
        if review_status and review_status != "All":
            filter_query["review_status"] = review_status

        return self.mistakes.count_documents(filter_query)

    def update_mistake(self, mistake_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates mistake tag, notes, or review status.
        """
        updates["updated_at"] = datetime.now(timezone.utc)
        clean_updates = {k: v for k, v in updates.items() if v is not None}

        res = self.mistakes.update_one(
            {"mistake_id": mistake_id},
            {"$set": clean_updates}
        )
        if res.matched_count == 0:
            return None
        return self.mistakes.find_one({"mistake_id": mistake_id})

    def delete_mistake(self, mistake_id: str) -> bool:
        """
        Removes a mistake record.
        """
        res = self.mistakes.delete_one({"mistake_id": mistake_id})
        return res.deleted_count > 0

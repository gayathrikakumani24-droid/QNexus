import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pymongo.database import Database

logger = logging.getLogger("qnexus.repositories.practice")

class PracticeRepository:
    def __init__(self, db: Database):
        self.db = db
        self.sessions = db.practice_sessions
        self.attempts = db.attempts

    def create_session(
        self,
        question_ids: List[str],
        config: Dict[str, Any],
        duration_minutes: int = 30
    ) -> str:
        """
        Creates a new practice session document in MongoDB.
        """
        session_id = f"SESS_{uuid.uuid4().hex[:12].upper()}"
        session_doc = {
            "_id": session_id,
            "session_id": session_id,
            "question_ids": question_ids,
            "config": config,
            "duration_minutes": duration_minutes,
            "status": "IN_PROGRESS",
            "answers": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        self.sessions.insert_one(session_doc)
        logger.info(f"Created practice session {session_id} with {len(question_ids)} questions.")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a practice session by session_id.
        """
        return self.sessions.find_one({"session_id": session_id})

    def update_session_answer(
        self,
        session_id: str,
        question_id: str,
        selected_answer: Optional[str],
        time_spent_seconds: int,
        marked_for_review: bool
    ) -> bool:
        """
        Updates a candidate's answer and review state for a specific question within a session.
        """
        answer_payload = {
            "selected_answer": selected_answer,
            "time_spent_seconds": time_spent_seconds,
            "marked_for_review": marked_for_review,
            "updated_at": datetime.now(timezone.utc)
        }

        res = self.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    f"answers.{question_id}": answer_payload,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        return res.modified_count > 0

    def complete_session(self, session_id: str, result_summary: Dict[str, Any]) -> bool:
        """
        Marks session as COMPLETED and stores summary score.
        """
        res = self.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "status": "COMPLETED",
                    "result_summary": result_summary,
                    "completed_at": datetime.now(timezone.utc)
                }
            }
        )
        return res.modified_count > 0

    def record_attempts_bulk(self, attempts: List[Dict[str, Any]]) -> int:
        """
        Inserts attempt records into the attempts collection.
        """
        if not attempts:
            return 0
        res = self.attempts.insert_many(attempts)
        logger.info(f"Recorded {len(res.inserted_ids)} question attempts in MongoDB.")
        return len(res.inserted_ids)

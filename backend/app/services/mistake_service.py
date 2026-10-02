import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from app.core.database import get_mongo_db
from app.repositories.mistake_repository import MistakeRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.mistake_schema import (
    MistakeCreateRequest,
    MistakeUpdateRequest,
    MistakeResponse,
    MistakeListResponse
)

logger = logging.getLogger("qnexus.services.mistake")

class MistakeService:
    def __init__(
        self,
        db: Optional[Database] = None,
        mistake_repo: Optional[MistakeRepository] = None,
        question_repo: Optional[QuestionRepository] = None
    ):
        self.db = db if db is not None else get_mongo_db()
        self.repo = mistake_repo or MistakeRepository(self.db)
        self.question_repo = question_repo or QuestionRepository(self.db)

    def create_mistake(self, request: MistakeCreateRequest) -> MistakeResponse:
        """
        Creates or updates a mistake record, auto-populating question metadata.
        """
        q_doc = self.question_repo.get_question(request.question_id)
        if not q_doc:
            raise ValueError(f"Question '{request.question_id}' not found.")

        # Determine correct answer from question doc if missing
        correct_ans = request.correct_answer or q_doc.correct_option or (str(q_doc.numerical_answer) if q_doc.numerical_answer is not None else None)

        payload = {
            "user_id": request.user_id or "default_user",
            "question_id": request.question_id,
            "subject": request.subject or q_doc.subject,
            "chapter": request.chapter or q_doc.chapter,
            "concept": request.concept or q_doc.concept,
            "user_answer": request.user_answer,
            "correct_answer": correct_ans,
            "mistake_tag": request.mistake_tag,
            "user_notes": request.user_notes,
            "review_status": request.review_status or "Needs Review"
        }

        doc = self.repo.create_or_update_mistake(payload)

        return MistakeResponse(
            mistake_id=doc["mistake_id"],
            user_id=doc["user_id"],
            question_id=doc["question_id"],
            subject=doc.get("subject"),
            chapter=doc.get("chapter"),
            concept=doc.get("concept"),
            user_answer=doc.get("user_answer"),
            correct_answer=doc.get("correct_answer"),
            mistake_tag=doc.get("mistake_tag", "Conceptual Gap"),
            user_notes=doc.get("user_notes"),
            review_status=doc.get("review_status", "Needs Review"),
            question=q_doc,
            created_at=doc.get("created_at") or datetime.now(timezone.utc),
            updated_at=doc.get("updated_at") or datetime.now(timezone.utc)
        )

    def list_mistakes(
        self,
        user_id: Optional[str] = "default_user",
        subject: Optional[str] = None,
        chapter: Optional[str] = None,
        mistake_tag: Optional[str] = None,
        review_status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> MistakeListResponse:
        """
        Lists mistake records with hydrated question details.
        """
        raw_list = self.repo.list_mistakes(
            user_id=user_id,
            subject=subject,
            chapter=chapter,
            mistake_tag=mistake_tag,
            review_status=review_status,
            limit=limit,
            offset=offset
        )
        total_count = self.repo.count_mistakes(
            user_id=user_id,
            subject=subject,
            chapter=chapter,
            mistake_tag=mistake_tag,
            review_status=review_status
        )

        question_ids = [m["question_id"] for m in raw_list]
        questions = self.question_repo.get_questions_by_ids(question_ids)
        q_map = {q.question_id: q for q in questions}

        mistake_responses: List[MistakeResponse] = []
        for doc in raw_list:
            q_id = doc["question_id"]
            mistake_responses.append(
                MistakeResponse(
                    mistake_id=doc["mistake_id"],
                    user_id=doc["user_id"],
                    question_id=q_id,
                    subject=doc.get("subject"),
                    chapter=doc.get("chapter"),
                    concept=doc.get("concept"),
                    user_answer=doc.get("user_answer"),
                    correct_answer=doc.get("correct_answer"),
                    mistake_tag=doc.get("mistake_tag", "Conceptual Gap"),
                    user_notes=doc.get("user_notes"),
                    review_status=doc.get("review_status", "Needs Review"),
                    question=q_map.get(q_id),
                    created_at=doc.get("created_at") or datetime.now(timezone.utc),
                    updated_at=doc.get("updated_at") or datetime.now(timezone.utc)
                )
            )

        return MistakeListResponse(
            total=total_count,
            mistakes=mistake_responses
        )

    def update_mistake(self, mistake_id: str, request: MistakeUpdateRequest) -> MistakeResponse:
        """
        Updates mistake tag, notes, or review status.
        """
        updates = request.model_dump(exclude_unset=True)
        updated_doc = self.repo.update_mistake(mistake_id, updates)
        if not updated_doc:
            raise ValueError(f"Mistake record '{mistake_id}' not found.")

        q_doc = self.question_repo.get_question(updated_doc["question_id"])

        return MistakeResponse(
            mistake_id=updated_doc["mistake_id"],
            user_id=updated_doc["user_id"],
            question_id=updated_doc["question_id"],
            subject=updated_doc.get("subject"),
            chapter=updated_doc.get("chapter"),
            concept=updated_doc.get("concept"),
            user_answer=updated_doc.get("user_answer"),
            correct_answer=updated_doc.get("correct_answer"),
            mistake_tag=updated_doc.get("mistake_tag", "Conceptual Gap"),
            user_notes=updated_doc.get("user_notes"),
            review_status=updated_doc.get("review_status", "Needs Review"),
            question=q_doc,
            created_at=updated_doc.get("created_at") or datetime.now(timezone.utc),
            updated_at=updated_doc.get("updated_at") or datetime.now(timezone.utc)
        )

    def delete_mistake(self, mistake_id: str) -> bool:
        """
        Deletes a mistake record.
        """
        deleted = self.repo.delete_mistake(mistake_id)
        if not deleted:
            raise ValueError(f"Mistake record '{mistake_id}' not found.")
        return True

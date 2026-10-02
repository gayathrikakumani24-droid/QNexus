import random
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pymongo.database import Database
from app.core.database import get_mongo_db
from app.repositories.question_repository import QuestionRepository
from app.repositories.practice_repository import PracticeRepository
from app.schemas.practice_schema import (
    PracticeStartRequest,
    PracticeStartResponse,
    PracticeQuestionView,
    PracticeAnswerRequest,
    PracticeSubmitResponse,
    PracticeQuestionResult
)

logger = logging.getLogger("qnexus.services.practice")

class PracticeService:
    def __init__(
        self,
        db: Optional[Database] = None,
        question_repo: Optional[QuestionRepository] = None,
        practice_repo: Optional[PracticeRepository] = None
    ):
        self.db = db if db is not None else get_mongo_db()
        self.question_repo = question_repo or QuestionRepository(self.db)
        self.practice_repo = practice_repo or PracticeRepository(self.db)

    def start_session(self, request: PracticeStartRequest) -> PracticeStartResponse:
        """
        Creates a practice session from existing MongoDB questions matching the user's config.
        Does NOT generate synthetic questions.
        """
        # 1. Fetch matching questions from MongoDB
        target_subject = request.subject if (request.subject and request.subject != "All") else None

        if request.question_ids:
            matched_questions = self.question_repo.get_questions_by_ids(request.question_ids)
        else:
            # 1a. Try exact metadata match first
            matched_questions = self.question_repo.list_questions(
                subject=target_subject,
                chapter=request.chapter if request.chapter else None,
                concept=request.concept if request.concept else None,
                difficulty=request.difficulty if request.difficulty != "All" else None,
                year=request.year if request.year else None,
                shift=request.shift if request.shift != "All" else None,
                paper_id=request.paper_id if request.paper_id else None,
                limit=200
            )

            # 1b. If chapter or concept was specified but returned 0 matches (e.g. unclassified DB fields),
            # use Pinecone vector semantic search to retrieve authentic questions on this topic
            if not matched_questions and (request.chapter or request.concept):
                search_text = f"{request.chapter or ''} {request.concept or ''}".strip()
                try:
                    from app.services.embedding_service import EmbeddingService
                    from app.repositories.vector_repository import VectorRepository
                    vr = VectorRepository()
                    emb = EmbeddingService()
                    q_vec = emb.embed_text(search_text)

                    filter_dict = {}
                    if target_subject:
                        filter_dict["subject"] = {"$eq": target_subject}
                    if request.year:
                        filter_dict["year"] = {"$eq": request.year}

                    vector_matches = vr.query_vectors(
                        query_vector=q_vec,
                        top_k=max(request.num_questions * 3, 20),
                        filter_dict=filter_dict if filter_dict else None
                    )
                    if vector_matches:
                        matched_ids = [m.id if hasattr(m, "id") else m.get("id") for m in vector_matches]
                        matched_questions = self.question_repo.get_questions_by_ids(matched_ids)
                        logger.info(f"Pinecone vector search retrieved {len(matched_questions)} questions for topic '{search_text}' in subject '{target_subject}'")
                except Exception as e:
                    logger.warning(f"Vector search fallback in practice failed: {e}")

                # 1c. If vector search yielded no questions, fallback to content regex matching within the selected subject
                if not matched_questions:
                    query_filter = {}
                    if target_subject:
                        query_filter["subject"] = target_subject
                    if request.year:
                        query_filter["year"] = request.year
                    if request.paper_id:
                        query_filter["paper_id"] = request.paper_id

                    keywords = [w for w in search_text.split() if len(w) > 3]
                    if keywords:
                        regex_pat = "|".join(keywords)
                        query_filter["content"] = {"$regex": regex_pat, "$options": "i"}
                        cursor = self.question_repo.collection.find(query_filter).limit(50)
                        from app.schemas.question_schema import QuestionResponse
                        matched_questions = [QuestionResponse(**doc) for doc in cursor]

            # 1d. Fallback: if no questions match the specific topic, stay strictly within target_subject!
            if not matched_questions and target_subject:
                logger.warning(f"No specific topic matches; strictly selecting from subject '{target_subject}'")
                matched_questions = self.question_repo.list_questions(
                    subject=target_subject,
                    difficulty=request.difficulty if request.difficulty != "All" else None,
                    year=request.year if request.year else None,
                    limit=100
                )

            # 1e. Only if user explicitly chose 'All' subjects do we draw across subjects
            if not matched_questions and not target_subject:
                matched_questions = self.question_repo.list_questions(limit=100)

        if not matched_questions:
            raise ValueError("No questions available in database to start practice session.")

        # Sample target question count if not explicit list
        if request.question_ids:
            sampled_questions = matched_questions
            target_count = len(sampled_questions)
        else:
            target_count = min(request.num_questions, len(matched_questions))
            sampled_questions = random.sample(matched_questions, target_count)

        question_ids = [q.question_id for q in sampled_questions]
        duration_minutes = max(10, target_count * 3)  # Approx 3 mins per question

        # 2. Create session in MongoDB
        session_id = self.practice_repo.create_session(
            question_ids=question_ids,
            config=request.model_dump(),
            duration_minutes=duration_minutes
        )

        # 3. Create question views without revealing answers
        question_views = [
            PracticeQuestionView(
                question_id=q.question_id,
                paper_id=q.paper_id,
                question_number=idx + 1,
                content=q.content,
                options=q.options,
                subject=q.subject,
                chapter=q.chapter,
                concept=q.concept,
                difficulty=q.difficulty,
                question_type=q.question_type,
                has_images=bool(q.has_images or (q.image_urls and len(q.image_urls) > 0)),
                image_urls=q.image_urls or [],
                year=q.year,
                session=q.session,
                date=q.date,
                shift=q.shift
            )
            for idx, q in enumerate(sampled_questions)
        ]

        return PracticeStartResponse(
            session_id=session_id,
            total_questions=len(question_views),
            duration_minutes=duration_minutes,
            status="IN_PROGRESS",
            questions=question_views
        )

    def record_answer(self, session_id: str, request: PracticeAnswerRequest) -> bool:
        """
        Records/updates answer selection and review state for a single question.
        """
        session = self.practice_repo.get_session(session_id)
        if not session:
            raise ValueError(f"Practice session '{session_id}' not found.")

        if session.get("status") == "COMPLETED":
            raise ValueError("Cannot modify answers for an already submitted session.")

        return self.practice_repo.update_session_answer(
            session_id=session_id,
            question_id=request.question_id,
            selected_answer=request.selected_answer,
            time_spent_seconds=request.time_spent_seconds,
            marked_for_review=request.marked_for_review
        )

    def submit_session(self, session_id: str) -> PracticeSubmitResponse:
        """
        Evaluates session answers against verified MongoDB keys, marks session COMPLETED,
        and saves records into attempts collection.
        JEE Main Scoring: +4 for correct, -1 for wrong MCQ, 0 for unattempted.
        """
        session = self.practice_repo.get_session(session_id)
        if not session:
            raise ValueError(f"Practice session '{session_id}' not found.")

        question_ids = session.get("question_ids", [])
        answers = session.get("answers", {})

        # Hydrate authoritative questions from MongoDB
        questions = self.question_repo.get_questions_by_ids(question_ids)
        doc_map = {q.question_id: q for q in questions}

        results: List[PracticeQuestionResult] = []
        attempt_records: List[Dict[str, Any]] = []

        total_score = 0
        correct_count = 0
        incorrect_count = 0
        unattempted_count = 0
        total_time_seconds = 0

        for q_id in question_ids:
            q = doc_map.get(q_id)
            if not q:
                continue

            ans_entry = answers.get(q_id, {})
            selected = ans_entry.get("selected_answer")
            time_spent = ans_entry.get("time_spent_seconds", 0)
            marked = ans_entry.get("marked_for_review", False)
            total_time_seconds += time_spent

            correct_ans = q.correct_option or (str(q.numerical_answer) if q.numerical_answer is not None else None)

            is_attempted = selected is not None and str(selected).strip() != ""
            is_correct = False
            score_delta = 0

            if is_attempted:
                # Compare answers
                if correct_ans and str(selected).strip().upper() == str(correct_ans).strip().upper():
                    is_correct = True
                    correct_count += 1
                    score_delta = 4
                else:
                    is_correct = False
                    incorrect_count += 1
                    # -1 penalty for incorrect MCQ
                    score_delta = -1 if q.question_type == "MCQ" or len(q.options) > 0 else 0
            else:
                unattempted_count += 1
                score_delta = 0

            total_score += score_delta

            results.append(
                PracticeQuestionResult(
                    question=q,
                    selected_answer=selected,
                    correct_answer=correct_ans,
                    is_correct=is_correct,
                    is_attempted=is_attempted,
                    time_spent_seconds=time_spent,
                    score_delta=score_delta
                )
            )

            attempt_records.append({
                "session_id": session_id,
                "question_id": q_id,
                "subject": q.subject,
                "chapter": q.chapter,
                "concept": q.concept,
                "difficulty": q.difficulty,
                "selected_answer": selected,
                "correct_answer": correct_ans,
                "is_correct": is_correct,
                "is_attempted": is_attempted,
                "time_spent_seconds": time_spent,
                "marked_for_review": marked,
                "attempted_at": datetime.now(timezone.utc)
            })

        # Save attempts to attempts collection
        if attempt_records:
            self.practice_repo.record_attempts_bulk(attempt_records)

        # Calculate metrics
        max_score = len(question_ids) * 4
        accuracy = (
            round((correct_count / (correct_count + incorrect_count)) * 100, 1)
            if (correct_count + incorrect_count) > 0
            else 0.0
        )

        summary_data = {
            "score": total_score,
            "max_score": max_score,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "unattempted_count": unattempted_count,
            "accuracy_percentage": accuracy,
            "total_time_seconds": total_time_seconds
        }

        # Mark session completed in MongoDB
        self.practice_repo.complete_session(session_id, summary_data)

        return PracticeSubmitResponse(
            session_id=session_id,
            total_questions=len(question_ids),
            attempted_count=correct_count + incorrect_count,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            unattempted_count=unattempted_count,
            score=total_score,
            max_score=max_score,
            accuracy_percentage=accuracy,
            total_time_seconds=total_time_seconds,
            status="COMPLETED",
            results=results
        )

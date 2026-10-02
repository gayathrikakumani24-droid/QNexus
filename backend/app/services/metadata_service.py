import json
import logging
from typing import Dict, Any, List, Optional
from pymongo.database import Database
from app.schemas.question_metadata import QuestionMetadata, ClassificationSummaryResponse
from app.repositories.question_repository import QuestionRepository
from app.services.llm_client import LLMClient

logger = logging.getLogger("qnexus.services.metadata_service")

CLASSIFICATION_SYSTEM_PROMPT = """You are an expert AI exam analyzer specializing in JEE Main previous year questions.
Analyze the provided JEE Main question and classify its syllabus metadata precisely.

Your response MUST be a JSON object adhering to this exact schema:
{
    "subject": "Physics" | "Chemistry" | "Mathematics" | "Unknown",
    "chapter": "<Exact Chapter/Topic Name e.g. Rotational Motion, Thermodynamics, Electrochemistry, Calculus>",
    "concept": "<Specific Core Concept Tested e.g. Parallel Axis Theorem, Hess's Law, Integration by Parts>",
    "difficulty": "Easy" | "Medium" | "Hard" | "Unknown",
    "question_type": "MCQ" | "Numerical" | "Assertion Reason" | "Multiple Correct" | "Unknown"
}

Strict Rules:
1. Do NOT solve the question.
2. Do NOT provide answers or solutions.
3. Do NOT modify the question text.
4. If you are uncertain about subject, chapter, or concept, return "Unknown".
5. Return ONLY the JSON object.
"""

class MetadataClassificationService:
    def __init__(self, db: Database, llm_client: Optional[LLMClient] = None):
        self.question_repo = QuestionRepository(db)
        self.llm_client = llm_client or LLMClient()

    def classify_question(self, question_text: str, options: List[Dict[str, str]]) -> QuestionMetadata:
        """
        Invokes LLM to classify a single question statement and validates result against Pydantic schema.
        """
        options_text = ""
        if options:
            options_text = "\nOptions:\n" + "\n".join(
                [f"({opt.get('id', '')}) {opt.get('content', '')}" for opt in options]
            )

        user_prompt = f"Question Statement:\n{question_text}\n{options_text}"

        try:
            raw_response = self.llm_client.generate_json_completion(
                system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.1
            )
            if not raw_response:
                logger.warning("LLM returned empty response. Falling back to Unknown metadata.")
                return QuestionMetadata()

            validated = QuestionMetadata.model_validate(raw_response)
            return validated

        except Exception as e:
            logger.error(f"Failed to classify question metadata: {e}")
            return QuestionMetadata()

    def classify_paper_questions(
        self,
        paper_id: str,
        batch_size: int = 10,
        overwrite: bool = False
    ) -> ClassificationSummaryResponse:
        """
        Classifies all questions belonging to a specific paper in controlled batches.
        Skips already classified questions unless overwrite is True.
        """
        questions = self.question_repo.list_questions(paper_id=paper_id, limit=200)
        total_questions = len(questions)
        successful_count = 0
        failed_count = 0

        logger.info(f"Starting metadata classification for paper {paper_id} ({total_questions} questions)")

        for i in range(0, total_questions, batch_size):
            batch = questions[i:i + batch_size]
            for q in batch:
                # Check cache / existing metadata
                has_existing = (
                    q.subject and q.subject != "Unknown" and
                    q.chapter and q.chapter != "Unknown"
                )
                if has_existing and not overwrite:
                    successful_count += 1
                    continue

                opts_list = [opt.model_dump() for opt in q.options] if q.options else []
                metadata = self.classify_question(q.content, opts_list)

                if metadata.subject != "Unknown" or metadata.chapter != "Unknown":
                    # Update question metadata in MongoDB
                    update_data = {
                        "subject": metadata.subject,
                        "chapter": metadata.chapter,
                        "concept": metadata.concept,
                        "difficulty": metadata.difficulty,
                        "question_type": metadata.question_type
                    }
                    self.question_repo.update_question_metadata(q.question_id, update_data)
                    successful_count += 1
                else:
                    failed_count += 1
                    logger.warning(f"Could not classify question {q.question_id}")

        return ClassificationSummaryResponse(
            paper_id=paper_id,
            processed=total_questions,
            successful=successful_count,
            failed=failed_count
        )

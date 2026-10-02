import logging
from typing import Dict, Any, List, Optional
from pymongo.database import Database
from app.core.database import get_mongo_db
from app.core.pinecone import get_pinecone_index, ensure_pinecone_index
from app.core.config import settings
from app.repositories.question_repository import QuestionRepository
from app.services.llm_client import LLMClient
from app.services.embedding_service import EmbeddingService
from app.schemas.ai_schema import ExplainResponse, HintResponse
from app.schemas.search_schema import SearchResultItem

logger = logging.getLogger("qnexus.services.ai")

EXPLAIN_SYSTEM_PROMPT = """You are an expert AI tutor specializing in JEE Main Physics, Chemistry, and Mathematics.
Provide an in-depth, rigorous, and pedagogical step-by-step explanation for the provided JEE Main question.

Your response MUST be a JSON object with this exact structure:
{
    "concept_summary": "<Brief 1-2 sentence overview of the core physics/chemistry/math theory and principles>",
    "step_by_step_solution": "<Full, comprehensive derivation with clear steps. Use LaTeX math delimiters ($...$ for inline, $$...$$ for block)>",
    "key_formulae": ["<Formula 1 in LaTeX>", "<Formula 2 in LaTeX>"],
    "common_pitfalls": "<Important exam pitfalls, sign errors, or misconceptions candidates frequently make on this type of question>"
}

Strict Rules:
1. Ensure all mathematical equations use standard LaTeX notation ($...$ or $$...$$).
2. Adhere strictly to the verified answer/solution provided in context.
3. Be clear, concise, and rigorous.
"""

HINT_SYSTEM_PROMPT = """You are a supportive AI tutor for JEE Main aspirants.
Generate a progressive, non-spoiler hint for the student based on the requested hint level:

Hint Levels:
- Level 1: Conceptual Direction (What physical/mathematical principle or diagram should the student consider?)
- Level 2: Formula & Setup (Which equations connect the given variables?)
- Level 3: Critical Next Step (What is the key substitution or mathematical transformation?)

Strict Rules:
1. NEVER reveal the final correct option (e.g. 'Option A') or the numerical answer.
2. Guide the student to think through the problem independently.
3. Use LaTeX formatting ($...$) for math expressions.

Return ONLY a JSON object:
{
    "hint_text": "<The progressive hint text with LaTeX>"
}
"""

class AIService:
    def __init__(
        self,
        db: Optional[Database] = None,
        llm_client: Optional[LLMClient] = None,
        embedding_service: Optional[EmbeddingService] = None,
        pinecone_index = None,
        qdrant_client = None
    ):
        self.db = db if db is not None else get_mongo_db()
        self.question_repo = QuestionRepository(self.db)
        self.llm_client = llm_client or LLMClient()
        self.embedding_service = embedding_service or EmbeddingService()
        self.pinecone_index = pinecone_index or qdrant_client or get_pinecone_index()
        self.index_name = settings.PINECONE_INDEX_NAME

    def explain_question(self, question_id: str, user_attempt: Optional[str] = None) -> ExplainResponse:
        """
        Generates step-by-step explanation using Groq LLM and verified question data from MongoDB.
        Does NOT modify the stored question.
        """
        question = self.question_repo.get_question(question_id)
        if not question:
            raise ValueError(f"Question with ID '{question_id}' not found in database.")

        opts_text = ""
        if question.options:
            opts_text = "\nOptions:\n" + "\n".join([f"({opt.id}) {opt.content}" for opt in question.options])

        context_info = []
        if question.subject:
            context_info.append(f"Subject: {question.subject}")
        if question.chapter:
            context_info.append(f"Chapter: {question.chapter}")
        if question.concept:
            context_info.append(f"Concept: {question.concept}")
        if question.correct_option:
            context_info.append(f"Verified Correct Option: {question.correct_option}")
        if question.numerical_answer is not None:
            context_info.append(f"Verified Numerical Answer: {question.numerical_answer}")
        if question.official_solution:
            context_info.append(f"Official Solution Reference: {question.official_solution}")
        if user_attempt:
            context_info.append(f"Student's Attempted Answer: {user_attempt}")

        context_str = "\n".join(context_info)
        user_prompt = f"""Question Information:
{context_str}

Question Statement:
{question.content}
{opts_text}

Provide the pedagogical explanation in structured JSON."""

        try:
            raw_json = self.llm_client.generate_json_completion(
                system_prompt=EXPLAIN_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.2
            )

            if not raw_json:
                return ExplainResponse(
                    question_id=question_id,
                    concept_summary=f"Concept: {question.concept or question.chapter or 'JEE Main Problem'}",
                    step_by_step_solution=question.official_solution or "Official solution is currently being populated.",
                    key_formulae=[],
                    common_pitfalls="Ensure consistent units and signs during calculation."
                )

            return ExplainResponse(
                question_id=question_id,
                concept_summary=raw_json.get("concept_summary", ""),
                step_by_step_solution=raw_json.get("step_by_step_solution", ""),
                key_formulae=raw_json.get("key_formulae", []),
                common_pitfalls=raw_json.get("common_pitfalls")
            )

        except Exception as e:
            logger.error(f"Failed to generate explanation for question {question_id}: {e}")
            return ExplainResponse(
                question_id=question_id,
                concept_summary="Conceptual explanation temporarily unavailable.",
                step_by_step_solution=question.official_solution or "Refer to official syllabus and solution keys.",
                key_formulae=[],
                common_pitfalls=None
            )

    def get_hint(self, question_id: str, hint_level: int = 1) -> HintResponse:
        """
        Generates progressive hints without revealing the answer.
        """
        question = self.question_repo.get_question(question_id)
        if not question:
            raise ValueError(f"Question with ID '{question_id}' not found in database.")

        opts_text = ""
        if question.options:
            opts_text = "\nOptions:\n" + "\n".join([f"({opt.id}) {opt.content}" for opt in question.options])

        user_prompt = f"""Target Hint Level: {hint_level} (out of 3)
Subject: {question.subject or 'Unknown'}
Chapter: {question.chapter or 'Unknown'}
Concept: {question.concept or 'Unknown'}

Question Statement:
{question.content}
{opts_text}

Provide the progressive level {hint_level} hint."""

        try:
            raw_json = self.llm_client.generate_json_completion(
                system_prompt=HINT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.3
            )

            hint_text = raw_json.get("hint_text") if raw_json else None
            if not hint_text:
                if hint_level == 1:
                    hint_text = f"Think about the core concepts of {question.chapter or 'this topic'} and identify the known and unknown variables."
                elif hint_level == 2:
                    hint_text = "Write down the governing formula relating the given quantities and check the boundary conditions."
                else:
                    hint_text = "Substitute the given numerical parameters into your governing equation and simplify step by step."

            return HintResponse(
                question_id=question_id,
                hint_level=hint_level,
                hint_text=hint_text,
                next_hint_available=hint_level < 3
            )

        except Exception as e:
            logger.error(f"Failed to generate hint for question {question_id}: {e}")
            return HintResponse(
                question_id=question_id,
                hint_level=hint_level,
                hint_text="Consider the standard governing formulas for this question.",
                next_hint_available=hint_level < 3
            )

    def get_similar_questions(self, question_id: str, top_k: int = 5) -> List[SearchResultItem]:
        """
        Finds semantically similar PYQs using Pinecone vector distance and hydrates full docs from MongoDB.
        Excludes the query question itself from the result set.
        Does NOT use Groq.
        """
        question = self.question_repo.get_question(question_id)
        if not question:
            raise ValueError(f"Question with ID '{question_id}' not found in database.")

        if self.pinecone_index is None:
            ensure_pinecone_index(self.index_name, vector_size=384)

        # 1. Format and embed target question
        formatted_text = self.embedding_service.format_question_for_embedding(
            content=question.content,
            subject=question.subject,
            chapter=question.chapter,
            concept=question.concept
        )
        query_vector = self.embedding_service.embed_text(formatted_text)

        # 2. Query Pinecone for top_k + 1 nearest neighbors
        hits = []
        if self.pinecone_index is not None:
            try:
                if hasattr(self.pinecone_index, "query"):
                    res = self.pinecone_index.query(
                        vector=query_vector,
                        top_k=top_k + 1,
                        include_metadata=True
                    )
                    hits = getattr(res, "matches", []) or (res.get("matches", []) if isinstance(res, dict) else [])
                elif hasattr(self.pinecone_index, "search"):
                    hits = self.pinecone_index.search(
                        collection_name=self.index_name,
                        query_vector=query_vector,
                        limit=top_k + 1,
                        with_payload=True
                    )
            except Exception as e:
                logger.error(f"Pinecone similarity search failed for question {question_id}: {e}")
                return []

        # 3. Filter out current question
        filtered_ids = []
        score_map = {}
        for hit in hits:
            metadata = getattr(hit, "metadata", None) or (hit.get("metadata") if isinstance(hit, dict) else None)
            payload = getattr(hit, "payload", None) or (hit.get("payload") if isinstance(hit, dict) else None)
            
            q_id = None
            if metadata and "question_id" in metadata:
                q_id = metadata["question_id"]
            elif payload and "question_id" in payload:
                q_id = payload["question_id"]
            elif hasattr(hit, "id") and hit.id:
                q_id = hit.id
            elif isinstance(hit, dict) and "id" in hit:
                q_id = hit["id"]

            if q_id and q_id != question_id:
                filtered_ids.append(q_id)
                raw_score = getattr(hit, "score", 0.0) or (hit.get("score", 0.0) if isinstance(hit, dict) else 0.0)
                score_map[q_id] = round(float(raw_score), 4)
            if len(filtered_ids) >= top_k:
                break

        if not filtered_ids:
            return []

        # 4. Hydrate from MongoDB (Source of Truth)
        hydrated_docs = self.question_repo.get_questions_by_ids(filtered_ids)
        doc_map = {q.question_id: q for q in hydrated_docs}

        # 5. Build ranked results
        results = []
        for q_id in filtered_ids:
            if q_id in doc_map:
                results.append(
                    SearchResultItem(
                        similarity_score=score_map.get(q_id, 0.0),
                        question=doc_map[q_id]
                    )
                )

        return results

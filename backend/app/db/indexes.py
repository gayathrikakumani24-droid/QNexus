from pymongo.database import Database
import logging

logger = logging.getLogger("qnexus.db.indexes")

def ensure_indexes(db: Database):
    """
    Creates and verifies unique and compound indexes for MongoDB collections.
    """
    try:
        # Papers collection unique index on paper_id (using _id or paper_id field)
        db.papers.create_index([("paper_id", 1)], unique=True)

        # Questions collection unique index on question_id
        db.questions.create_index([("question_id", 1)], unique=True)
        db.questions.create_index([("paper_id", 1)])

        # Metadata indexes for fast filtering
        db.questions.create_index([("subject", 1)])
        db.questions.create_index([("chapter", 1)])
        db.questions.create_index([("concept", 1)])
        db.questions.create_index([("difficulty", 1)])
        db.questions.create_index([("year", 1), ("shift", 1)])
        db.questions.create_index([("subject", 1), ("chapter", 1), ("difficulty", 1)])

        # Practice Sessions & Attempts indexes for fast aggregation
        db.practice_sessions.create_index([("session_id", 1)], unique=True)
        db.attempts.create_index([("session_id", 1)])
        db.attempts.create_index([("question_id", 1)])
        db.attempts.create_index([("subject", 1)])
        db.attempts.create_index([("chapter", 1)])
        db.attempts.create_index([("concept", 1)])
        db.attempts.create_index([("difficulty", 1)])
        db.attempts.create_index([("attempted_at", -1)])

        # Mistakes collection indexes
        db.mistakes.create_index([("mistake_id", 1)], unique=True)
        db.mistakes.create_index([("user_id", 1), ("question_id", 1)], unique=True)
        db.mistakes.create_index([("subject", 1)])
        db.mistakes.create_index([("chapter", 1)])
        db.mistakes.create_index([("mistake_tag", 1)])
        db.mistakes.create_index([("review_status", 1)])
        db.mistakes.create_index([("created_at", -1)])

        logger.info("MongoDB unique and secondary indexes ensured successfully.")
    except Exception as e:
        logger.warning(f"Could not verify MongoDB indexes: {e}")

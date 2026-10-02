from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
from pymongo.database import Database

logger = logging.getLogger("qnexus.repositories.knowledge")

class BaseKnowledgeRepository(ABC):
    """
    Abstract interface for Knowledge Graph operations.
    Allows swappable implementations (MongoDB initially, Neo4j in future).
    """

    @abstractmethod
    def get_concept_metadata(self, concept: str) -> Optional[Dict[str, Any]]:
        """Retrieves chapter, subject, and question associations for a concept."""
        pass

    @abstractmethod
    def get_related_questions(self, concept: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves questions testing a specific concept."""
        pass

    @abstractmethod
    def get_sibling_concepts_in_chapter(self, chapter: str, exclude_concept: Optional[str] = None) -> List[str]:
        """Retrieves other concepts under the same chapter."""
        pass

    @abstractmethod
    def get_hierarchy_tree(self) -> List[Dict[str, Any]]:
        """Retrieves full Subject -> Chapter -> Concept hierarchy."""
        pass


class MongoKnowledgeRepository(BaseKnowledgeRepository):
    """
    MongoDB-derived implementation of the Knowledge Graph abstraction.
    Derives concepts, hierarchies, and question relationships from MongoDB documents.
    """

    def __init__(self, db: Database):
        self.db = db
        self.questions = db.questions

    def get_concept_metadata(self, concept: str) -> Optional[Dict[str, Any]]:
        """
        Finds the primary subject and chapter associated with a concept name.
        Case-insensitive match.
        """
        doc = self.questions.find_one(
            {"concept": {"$regex": f"^{concept}$", "$options": "i"}},
            {"subject": 1, "chapter": 1, "concept": 1}
        )
        if not doc:
            # Try partial substring match if exact wasn't found
            doc = self.questions.find_one(
                {"concept": {"$regex": concept, "$options": "i"}},
                {"subject": 1, "chapter": 1, "concept": 1}
            )
        return doc

    def get_related_questions(self, concept: str, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Queries MongoDB question documents testing the concept.
        """
        cursor = self.questions.find(
            {"concept": {"$regex": f"^{concept}$", "$options": "i"}}
        ).limit(limit)
        results = list(cursor)

        if not results:
            # Fallback to case-insensitive partial match
            cursor = self.questions.find(
                {"concept": {"$regex": concept, "$options": "i"}}
            ).limit(limit)
            results = list(cursor)

        return results

    def get_sibling_concepts_in_chapter(self, chapter: str, exclude_concept: Optional[str] = None) -> List[str]:
        """
        Finds distinct concepts within the same chapter from MongoDB.
        """
        query = {"chapter": chapter}
        if exclude_concept:
            query["concept"] = {"$ne": exclude_concept}

        distinct_concepts = self.questions.distinct("concept", query)
        # Filter out None/empty
        return [c for c in distinct_concepts if c and c.strip() and c.strip().lower() != "unknown"]

    def get_hierarchy_tree(self) -> List[Dict[str, Any]]:
        """
        Aggregates Subject -> Chapter -> Concept hierarchy tree using MongoDB aggregation.
        """
        pipeline = [
            {
                "$match": {
                    "subject": {"$nin": [None, "", "Unknown"]},
                    "chapter": {"$nin": [None, "", "General"]},
                    "concept": {"$nin": [None, "", "General Concepts", "Unknown"]}
                }
            },
            {
                "$group": {
                    "_id": {
                        "subject": "$subject",
                        "chapter": "$chapter"
                    },
                    "concepts": {"$addToSet": "$concept"}
                }
            },
            {
                "$group": {
                    "_id": "$_id.subject",
                    "chapters": {
                        "$push": {
                            "chapter": "$_id.chapter",
                            "concepts": "$concepts"
                        }
                    }
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]

        return list(self.questions.aggregate(pipeline))

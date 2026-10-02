import logging
from typing import Dict, Any, List, Optional
from pymongo.database import Database

logger = logging.getLogger("qnexus.repositories.analytics")

class AnalyticsRepository:
    def __init__(self, db: Database):
        self.db = db
        self.attempts = db.attempts
        self.sessions = db.practice_sessions
        self.questions = db.questions

    def get_summary_aggregation(self) -> Dict[str, Any]:
        """
        Executes MongoDB aggregation facet pipeline to compute overall attempt stats
        and difficulty breakdown.
        """
        pipeline = [
            {
                "$lookup": {
                    "from": "questions",
                    "localField": "question_id",
                    "foreignField": "question_id",
                    "as": "question_meta"
                }
            },
            {
                "$addFields": {
                    "q_doc": { "$arrayElemAt": ["$question_meta", 0] }
                }
            },
            {
                "$addFields": {
                    "difficulty": {
                        "$ifNull": ["$difficulty", "$q_doc.difficulty", "Unknown"]
                    }
                }
            },
            {
                "$facet": {
                    "overall": [
                        {
                            "$group": {
                                "_id": None,
                                "total_questions_practiced": { "$sum": 1 },
                                "attempted": {
                                    "$sum": { "$cond": [{ "$eq": ["$is_attempted", True] }, 1, 0] }
                                },
                                "correct": {
                                    "$sum": { "$cond": [{ "$eq": ["$is_correct", True] }, 1, 0] }
                                },
                                "incorrect": {
                                    "$sum": {
                                        "$cond": [
                                            {
                                                "$and": [
                                                    { "$eq": ["$is_attempted", True] },
                                                    { "$eq": ["$is_correct", False] }
                                                ]
                                            },
                                            1,
                                            0
                                        ]
                                    }
                                },
                                "unanswered": {
                                    "$sum": { "$cond": [{ "$eq": ["$is_attempted", False] }, 1, 0] }
                                },
                                "total_time_seconds": { "$sum": "$time_spent_seconds" },
                                "unique_sessions": { "$addToSet": "$session_id" }
                            }
                        }
                    ],
                    "difficulty_breakdown": [
                        {
                            "$group": {
                                "_id": "$difficulty",
                                "total_attempts": { "$sum": 1 },
                                "attempted": {
                                    "$sum": { "$cond": [{ "$eq": ["$is_attempted", True] }, 1, 0] }
                                },
                                "correct": {
                                    "$sum": { "$cond": [{ "$eq": ["$is_correct", True] }, 1, 0] }
                                },
                                "incorrect": {
                                    "$sum": {
                                        "$cond": [
                                            {
                                                "$and": [
                                                    { "$eq": ["$is_attempted", True] },
                                                    { "$eq": ["$is_correct", False] }
                                                ]
                                            },
                                            1,
                                            0
                                        ]
                                    }
                                }
                            }
                        },
                        {
                            "$sort": { "total_attempts": -1 }
                        }
                    ]
                }
            }
        ]

        result = list(self.attempts.aggregate(pipeline))
        if not result:
            return {"overall": [], "difficulty_breakdown": []}
        return result[0]

    def get_subject_aggregation(self) -> List[Dict[str, Any]]:
        """
        Aggregates attempt statistics grouped by Subject.
        """
        pipeline = [
            {
                "$lookup": {
                    "from": "questions",
                    "localField": "question_id",
                    "foreignField": "question_id",
                    "as": "question_meta"
                }
            },
            {
                "$addFields": {
                    "q_doc": { "$arrayElemAt": ["$question_meta", 0] }
                }
            },
            {
                "$addFields": {
                    "subject": { "$ifNull": ["$subject", "$q_doc.subject", "Unknown"] }
                }
            },
            {
                "$group": {
                    "_id": "$subject",
                    "total_attempts": { "$sum": 1 },
                    "attempted": {
                        "$sum": { "$cond": [{ "$eq": ["$is_attempted", True] }, 1, 0] }
                    },
                    "correct": {
                        "$sum": { "$cond": [{ "$eq": ["$is_correct", True] }, 1, 0] }
                    },
                    "incorrect": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        { "$eq": ["$is_attempted", True] },
                                        { "$eq": ["$is_correct", False] }
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "unanswered": {
                        "$sum": { "$cond": [{ "$eq": ["$is_attempted", False] }, 1, 0] }
                    },
                    "total_time_seconds": { "$sum": "$time_spent_seconds" }
                }
            },
            {
                "$sort": { "total_attempts": -1 }
            }
        ]
        return list(self.attempts.aggregate(pipeline))

    def get_chapter_aggregation(self, subject: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Aggregates attempt statistics grouped by Subject & Chapter.
        """
        pipeline = [
            {
                "$lookup": {
                    "from": "questions",
                    "localField": "question_id",
                    "foreignField": "question_id",
                    "as": "question_meta"
                }
            },
            {
                "$addFields": {
                    "q_doc": { "$arrayElemAt": ["$question_meta", 0] }
                }
            },
            {
                "$addFields": {
                    "subject": { "$ifNull": ["$subject", "$q_doc.subject", "Unknown"] },
                    "chapter": { "$ifNull": ["$chapter", "$q_doc.chapter", "General"] }
                }
            }
        ]

        if subject and subject != "All":
            pipeline.append({"$match": {"subject": subject}})

        pipeline.extend([
            {
                "$group": {
                    "_id": {
                        "subject": "$subject",
                        "chapter": "$chapter"
                    },
                    "total_attempts": { "$sum": 1 },
                    "attempted": {
                        "$sum": { "$cond": [{ "$eq": ["$is_attempted", True] }, 1, 0] }
                    },
                    "correct": {
                        "$sum": { "$cond": [{ "$eq": ["$is_correct", True] }, 1, 0] }
                    },
                    "incorrect": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        { "$eq": ["$is_attempted", True] },
                                        { "$eq": ["$is_correct", False] }
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "unanswered": {
                        "$sum": { "$cond": [{ "$eq": ["$is_attempted", False] }, 1, 0] }
                    },
                    "total_time_seconds": { "$sum": "$time_spent_seconds" }
                }
            },
            {
                "$sort": { "total_attempts": -1 }
            }
        ])
        return list(self.attempts.aggregate(pipeline))

    def get_concept_aggregation(
        self,
        subject: Optional[str] = None,
        chapter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Aggregates attempt statistics grouped by Subject, Chapter, and Concept.
        """
        pipeline = [
            {
                "$lookup": {
                    "from": "questions",
                    "localField": "question_id",
                    "foreignField": "question_id",
                    "as": "question_meta"
                }
            },
            {
                "$addFields": {
                    "q_doc": { "$arrayElemAt": ["$question_meta", 0] }
                }
            },
            {
                "$addFields": {
                    "subject": { "$ifNull": ["$subject", "$q_doc.subject", "Unknown"] },
                    "chapter": { "$ifNull": ["$chapter", "$q_doc.chapter", "General"] },
                    "concept": { "$ifNull": ["$concept", "$q_doc.concept", "General Concepts"] }
                }
            }
        ]

        match_stage: Dict[str, Any] = {}
        if subject and subject != "All":
            match_stage["subject"] = subject
        if chapter:
            match_stage["chapter"] = chapter

        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend([
            {
                "$group": {
                    "_id": {
                        "subject": "$subject",
                        "chapter": "$chapter",
                        "concept": "$concept"
                    },
                    "total_attempts": { "$sum": 1 },
                    "attempted": {
                        "$sum": { "$cond": [{ "$eq": ["$is_attempted", True] }, 1, 0] }
                    },
                    "correct": {
                        "$sum": { "$cond": [{ "$eq": ["$is_correct", True] }, 1, 0] }
                    },
                    "incorrect": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        { "$eq": ["$is_attempted", True] },
                                        { "$eq": ["$is_correct", False] }
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "unanswered": {
                        "$sum": { "$cond": [{ "$eq": ["$is_attempted", False] }, 1, 0] }
                    },
                    "total_time_seconds": { "$sum": "$time_spent_seconds" }
                }
            },
            {
                "$sort": { "total_attempts": -1 }
            }
        ])
        return list(self.attempts.aggregate(pipeline))

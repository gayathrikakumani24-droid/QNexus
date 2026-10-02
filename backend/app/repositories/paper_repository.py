from typing import List, Optional
from datetime import datetime, timezone
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from app.schemas.paper_schema import PaperCreate, PaperResponse
import logging

logger = logging.getLogger("qnexus.repositories.paper")

class PaperRepository:
    def __init__(self, db: Database):
        self.collection = db.papers

    def create_paper(self, paper: PaperCreate) -> PaperResponse:
        """
        Inserts a new paper document into MongoDB.
        Handles duplicate inserts safely by returning existing paper if paper_id exists.
        """
        paper_dict = paper.model_dump()
        paper_dict["_id"] = paper.paper_id
        paper_dict["created_at"] = datetime.now(timezone.utc)

        try:
            self.collection.insert_one(paper_dict)
            logger.info(f"Created paper: {paper.paper_id}")
        except DuplicateKeyError:
            logger.warning(f"Paper with paper_id {paper.paper_id} already exists. Returning existing paper.")
            existing = self.collection.find_one({"paper_id": paper.paper_id})
            return PaperResponse(**existing)

        return PaperResponse(**paper_dict)

    def get_paper(self, paper_id: str) -> Optional[PaperResponse]:
        """
        Retrieves a paper document by paper_id.
        """
        doc = self.collection.find_one({"paper_id": paper_id})
        if not doc:
            return None
        return PaperResponse(**doc)

    def list_papers(
        self,
        year: Optional[int] = None,
        session: Optional[str] = None,
        shift: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[PaperResponse]:
        """
        Lists papers with optional year/session/shift filtering and sorting.
        """
        query = {}
        if year:
            query["year"] = year
        if session and session != "All":
            query["session"] = {"$regex": f"^{session}$", "$options": "i"}
        if shift and shift != "All":
            query["shift"] = {"$regex": shift, "$options": "i"}
        cursor = self.collection.find(query).sort([("year", -1), ("date", -1), ("shift", 1)]).skip(skip).limit(limit)
        return [PaperResponse(**doc) for doc in cursor]

    def update_paper_status(
        self, paper_id: str, status: str, total_questions: Optional[int] = None
    ) -> Optional[PaperResponse]:
        """
        Updates paper ingestion status and total_questions count.
        """
        update_fields = {"status": status}
        if total_questions is not None:
            update_fields["total_questions"] = total_questions

        doc = self.collection.find_one_and_update(
            {"paper_id": paper_id},
            {"$set": update_fields},
            return_document=True
        )
        if not doc:
            return None
        return PaperResponse(**doc)

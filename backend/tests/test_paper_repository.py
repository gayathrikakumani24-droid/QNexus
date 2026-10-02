import pytest
from unittest.mock import MagicMock
from app.repositories.paper_repository import PaperRepository
from app.schemas.paper_schema import PaperCreate
from pymongo.errors import DuplicateKeyError

def test_create_paper_success():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.papers = mock_collection

    repo = PaperRepository(mock_db)

    paper_data = PaperCreate(
        paper_id="JEE_MAIN_2026_APRIL_SHIFT_2",
        exam="JEE Main",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 2",
        filename="jee_2026_04_04_s2.pdf",
        status="UPLOADED"
    )

    created = repo.create_paper(paper_data)

    assert created.paper_id == "JEE_MAIN_2026_APRIL_SHIFT_2"
    assert created.exam == "JEE Main"
    mock_collection.insert_one.assert_called_once()

def test_create_paper_duplicate_handled():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.papers = mock_collection

    mock_collection.insert_one.side_effect = DuplicateKeyError("Duplicate key")
    mock_collection.find_one.return_value = {
        "paper_id": "JEE_MAIN_2026_APRIL_SHIFT_2",
        "exam": "JEE Main",
        "year": 2026,
        "session": "April",
        "date": "2026-04-04",
        "shift": "Shift 2",
        "filename": "jee_2026_04_04_s2.pdf",
        "total_questions": 90,
        "status": "PROCESSED"
    }

    repo = PaperRepository(mock_db)

    paper_data = PaperCreate(
        paper_id="JEE_MAIN_2026_APRIL_SHIFT_2",
        exam="JEE Main",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 2",
        filename="jee_2026_04_04_s2.pdf",
        status="UPLOADED"
    )

    res = repo.create_paper(paper_data)
    assert res.paper_id == "JEE_MAIN_2026_APRIL_SHIFT_2"
    assert res.status == "PROCESSED"

def test_get_paper():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.papers = mock_collection

    mock_collection.find_one.return_value = {
        "paper_id": "JEE_MAIN_2026_APRIL_SHIFT_2",
        "exam": "JEE Main",
        "year": 2026,
        "session": "April",
        "date": "2026-04-04",
        "shift": "Shift 2",
        "filename": "jee_2026_04_04_s2.pdf",
        "total_questions": 90,
        "status": "PROCESSED"
    }

    repo = PaperRepository(mock_db)
    paper = repo.get_paper("JEE_MAIN_2026_APRIL_SHIFT_2")

    assert paper is not None
    assert paper.paper_id == "JEE_MAIN_2026_APRIL_SHIFT_2"

def test_update_paper_status():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.papers = mock_collection

    mock_collection.find_one_and_update.return_value = {
        "paper_id": "JEE_MAIN_2026_APRIL_SHIFT_2",
        "exam": "JEE Main",
        "year": 2026,
        "session": "April",
        "date": "2026-04-04",
        "shift": "Shift 2",
        "filename": "jee_2026_04_04_s2.pdf",
        "total_questions": 90,
        "status": "PROCESSED"
    }

    repo = PaperRepository(mock_db)
    updated = repo.update_paper_status("JEE_MAIN_2026_APRIL_SHIFT_2", "PROCESSED", 90)

    assert updated is not None
    assert updated.status == "PROCESSED"
    assert updated.total_questions == 90

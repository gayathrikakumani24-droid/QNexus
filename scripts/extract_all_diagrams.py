"""
Qnexus - Script to extract and link diagrams across all papers in data/raw/.
"""

import os
import sys
import glob
import re
import logging

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

# UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.services.diagram_service import extract_diagrams_for_paper
from app.parsers.dispatcher import detect_year_from_input
from app.parsers.y2025.parser import parse_metadata_from_filename as parse_2025_meta
from app.parsers.y2024.parser import parse_metadata_from_filename as parse_2024_meta
from app.parsers.y2026.parser import parse_2026_filename_metadata

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("extract_all_diagrams")

def get_paper_id_for_pdf(pdf_path: str) -> str:
    year = detect_year_from_input(pdf_path)
    base = os.path.basename(pdf_path)
    if year == 2026:
        meta = parse_2026_filename_metadata(base)
        return meta["paper_id"]
    elif year == 2025:
        meta = parse_2025_meta(base)
        return meta["paper_id"]
    elif year == 2024:
        meta = parse_2024_meta(base)
        return meta["paper_id"]
    else:
        clean = re.sub(r'[^A-Za-z0-9_]+', '_', os.path.splitext(base)[0])
        return f"JEE_MAIN_{clean}"

def main():
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    processed_dir = os.path.join(BASE_DIR, "data", "processed")

    pdf_files = sorted(glob.glob(os.path.join(raw_dir, "**", "*.pdf"), recursive=True))
    logger.info(f"Found {len(pdf_files)} PDF papers in {raw_dir}")

    total_diagrams = 0
    for idx, pdf_path in enumerate(pdf_files, 1):
        paper_id = get_paper_id_for_pdf(pdf_path)
        logger.info(f"[{idx}/{len(pdf_files)}] Extracting diagrams for {paper_id} ({os.path.basename(pdf_path)})")

        json_path = os.path.join(processed_dir, f"{paper_id}_questions.json")
        if not os.path.exists(json_path):
            # Check if there are other matching JSON files
            candidates = glob.glob(os.path.join(processed_dir, f"*{paper_id[-10:]}*_questions.json"))
            if candidates:
                json_path = candidates[0]

        extracted = extract_diagrams_for_paper(
            pdf_path=pdf_path,
            paper_id=paper_id,
            processed_json_path=json_path if os.path.exists(json_path) else None
        )
        total_diagrams += len(extracted)

    logger.info(f"\n=======================================================")
    logger.info(f"Diagram Extraction Completed! Total Diagrams Extracted: {total_diagrams}")
    logger.info(f"=======================================================\n")

if __name__ == "__main__":
    main()

import os
import json
import fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger("qnexus.services.pdf_parser")

def extract_pages_from_pdf(pdf_path: str, paper_id: str, output_dir: str = "../data/processed") -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Extracts text page-by-page from a PDF using PyMuPDF while preserving page numbers.
    Saves raw page texts into data/processed/{paper_id}_pages.json.
    Returns (pages_data, warnings).
    """
    warnings: List[str] = []
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    pages_data: List[Dict[str, Any]] = []
    total_characters = 0

    for page_idx in range(total_pages):
        page = doc[page_idx]
        text = page.get_text("text", sort=True)
        total_characters += len(text.strip())
        
        pages_data.append({
            "page_number": page_idx + 1,
            "text": text
        })

    doc.close()

    if total_characters < 100:
        warnings.append(
            "PDF text extraction yield is extremely low. The PDF appears to be scanned or image-based."
        )

    # Save processed page texts to data/processed
    try:
        os.makedirs(output_dir, exist_ok=True)
        processed_file_path = os.path.join(output_dir, f"{paper_id}_pages.json")
        with open(processed_file_path, "w", encoding="utf-8") as f:
            json.dump(pages_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved processed page text to {processed_file_path}")
    except Exception as e:
        logger.warning(f"Failed to write processed page text to file: {e}")
        warnings.append(f"Could not save processed page JSON file: {str(e)}")

    return pages_data, warnings

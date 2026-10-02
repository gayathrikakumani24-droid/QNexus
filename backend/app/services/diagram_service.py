"""
Qnexus - Question Diagram Extraction and Linking Service.
Extracts diagram/figure clips and image options from PDF pages for questions containing diagrams,
saves them to uploads/questions/{paper_id}_Q_{q_num}.png, and updates MongoDB & JSON cache.
"""

import os
import re
import glob
import json
import logging
from typing import Dict, Any, List, Optional
import fitz

from app.core.database import get_mongo_db

logger = logging.getLogger("qnexus.services.diagram")

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "questions")
os.makedirs(UPLOADS_DIR, exist_ok=True)

def extract_diagrams_for_paper(
    pdf_path: str,
    paper_id: str,
    processed_json_path: Optional[str] = None
) -> Dict[int, str]:
    """
    Scans each page of the PDF. For any question whose page area contains embedded images
    or whose options require visual diagrams (e.g. '(See diagram in question)'),
    renders a crisp clip (150 DPI) of the question's diagram area and links it.

    Returns: { question_number: image_relative_url }
    """
    if not os.path.exists(pdf_path):
        logger.warning(f"PDF not found: {pdf_path}")
        return {}

    doc = fitz.open(pdf_path)
    extracted_diagrams: Dict[int, str] = {}

    try:
        for p_idx, page in enumerate(doc):
            imgs = page.get_images()
            page_text = page.get_text("text")

            # Check if this page might be an answer key page
            if "ANSWER KEYS" in page_text.upper() and len(page_text.strip().split("\n")) > 40:
                continue

            words = page.get_text("words")
            q_headers = []
            for w in words:
                m = re.match(r'^Q\.?(\d+)[\.\:]?$', w[4], re.IGNORECASE)
                if m:
                    try:
                        qn = int(m.group(1))
                        q_headers.append((qn, w[1], w[3]))
                    except ValueError:
                        pass

            if not q_headers:
                continue

            q_headers.sort(key=lambda x: x[1])
            ak_rects = sorted(page.search_for("MathonGo Answer Key"), key=lambda r: r.y0)
            if not ak_rects:
                ak_rects = sorted(page.search_for("Answer Key"), key=lambda r: r.y0)

            for i, (qn, y_start, _) in enumerate(q_headers):
                # Calculate vertical end of question
                next_qs = [qh[1] for qh in q_headers if qh[1] > y_start]
                next_aks = [r.y0 for r in ak_rects if r.y0 > y_start]

                candidates = []
                if next_qs:
                    candidates.append(min(next_qs))
                if next_aks:
                    candidates.append(min(next_aks))

                y_end = min(candidates) if candidates else page.rect.height - 35

                # Check for images intersecting this vertical area
                has_intersecting_image = False
                if imgs:
                    for img in imgs:
                        rects = page.get_image_rects(img)
                        for r in rects:
                            if not (r.y1 < y_start or r.y0 > y_end):
                                has_intersecting_image = True
                                break
                        if has_intersecting_image:
                            break

                if has_intersecting_image:
                    # Clip question diagram region
                    clip_rect = fitz.Rect(
                        25,
                        max(0, y_start - 5),
                        page.rect.width - 25,
                        min(page.rect.height, y_end + 2)
                    )
                    pix = page.get_pixmap(clip=clip_rect, dpi=150)
                    img_filename = f"{paper_id}_Q_{qn}.png"
                    save_path = os.path.join(UPLOADS_DIR, img_filename)
                    pix.save(save_path)

                    rel_url = f"/uploads/questions/{img_filename}"
                    extracted_diagrams[qn] = rel_url
                    logger.info(f"Saved diagram for {paper_id} Q{qn} -> {rel_url}")

    finally:
        doc.close()

    # Update processed JSON cache if file exists
    if processed_json_path and os.path.exists(processed_json_path):
        try:
            with open(processed_json_path, "r", encoding="utf-8") as f:
                questions_data = json.load(f)

            modified = False
            for q in questions_data:
                qn = q.get("question_number")
                if qn in extracted_diagrams:
                    q["has_images"] = True
                    q["image_urls"] = [extracted_diagrams[qn]]
                    modified = True

            if modified:
                with open(processed_json_path, "w", encoding="utf-8") as f:
                    json.dump(questions_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Updated JSON cache at {processed_json_path} with diagram URLs.")
        except Exception as e:
            logger.warning(f"Failed to update JSON cache {processed_json_path}: {e}")

    # Update MongoDB if accessible
    try:
        db = get_mongo_db()
        for qn, url in extracted_diagrams.items():
            db["questions"].update_many(
                {"paper_id": paper_id, "question_number": qn},
                {"$set": {"has_images": True, "image_urls": [url]}}
            )
    except Exception as e:
        logger.debug(f"MongoDB update notice: {e}")

    return extracted_diagrams

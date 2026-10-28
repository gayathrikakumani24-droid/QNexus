"""
Paper parsers for Qnexus.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.parsers.dispatcher import parse_paper, UnsupportedPaperFormatError, detect_year_from_input

def __getattr__(name: str):
    if name in ("parse_paper", "UnsupportedPaperFormatError", "detect_year_from_input"):
        import app.parsers.dispatcher as dispatcher
        return getattr(dispatcher, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ["parse_paper", "UnsupportedPaperFormatError", "detect_year_from_input"]

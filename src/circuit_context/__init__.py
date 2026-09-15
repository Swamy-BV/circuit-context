"""Source-backed engineering references, independent of CAD contracts."""

from .index import catalogue
from .index import get as get_guideline
from .retrieval import search as search_guidelines

__all__ = ["catalogue", "get_guideline", "search_guidelines"]

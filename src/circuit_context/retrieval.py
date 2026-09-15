"""Explicit retrieval strategies and rank fusion, independent of CAD and generation."""

from __future__ import annotations

import math
from typing import Any, Literal

from . import index

Method = Literal["keyword", "semantic", "hybrid"]


def fuse(rankings: list[list[str]], limit: int, constant: int = 60) -> list[str]:
    """Fuse one-based ranks equally, deduplicate, and break ties by stable guide ID."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, identifier in enumerate(dict.fromkeys(ranking), start=1):
            scores[identifier] = scores.get(identifier, 0.0) + 1 / (constant + rank)
    return sorted(scores, key=lambda key: (-scores[key], key))[:limit]


def search(
    query: str,
    topic: str = "",
    limit: int = 3,
    match: Literal["all", "any"] = "all",
    *,
    level: str = "",
    interface: str = "",
    domain: str = "",
    method: Method = "keyword",
    rerank: bool = False,
    candidate_limit: int = 20,
) -> dict[str, Any]:
    """Retrieve with explicit strategy selection and optional local reranking."""
    if method not in ("keyword", "semantic", "hybrid"):
        raise ValueError("method must be keyword, semantic or hybrid")
    if not 5 <= candidate_limit <= 100:
        raise ValueError("candidate_limit must be between 5 and 100")
    corpus, digest, terms, filters = index.query_context(
        query,
        topic,
        limit,
        match,
        level=level,
        interface=interface,
        domain=domain,
    )
    keyword: list[str] = []
    semantic: list[str] = []
    if method in ("keyword", "hybrid"):
        keyword = index.keyword_ids(
            corpus,
            digest,
            terms,
            filters,
            match,
            candidate_limit + 1,
        )
    if method in ("semantic", "hybrid"):
        from .semantic import ranked_ids

        semantic = ranked_ids(query, corpus, digest, filters, candidate_limit + 1)
    more_candidates = len(keyword) > candidate_limit or len(semantic) > candidate_limit
    keyword = keyword[:candidate_limit]
    semantic = semantic[:candidate_limit]
    more_candidates = more_candidates or len(set(keyword + semantic)) > candidate_limit
    candidates = (
        fuse([keyword, semantic], candidate_limit)
        if method == "hybrid"
        else keyword
        if method == "keyword"
        else semantic
    )
    if rerank:
        from .local_models import RERANKER, fingerprint
        from .local_models import rerank as score_pairs
        from .semantic import passage

        fingerprint(RERANKER)  # Reject missing setup even for an empty candidate set.
        if candidates:
            by_id = {g.id: g for g in corpus.guidelines}
            scores = score_pairs(query, [passage(by_id[key]) for key in candidates])
            if len(scores) != len(candidates) or not all(map(math.isfinite, scores)):
                raise ValueError("Reranker returned invalid scores.")
            candidates = [
                key
                for key, _ in sorted(
                    zip(candidates, scores, strict=True),
                    key=lambda row: (-row[1], row[0]),
                )
            ]
    result = index.search_response(
        corpus,
        digest,
        candidates,
        terms,
        filters,
        match,
        limit,
    )
    result["retrieval"] = {
        "method": method,
        "reranked": rerank,
        "candidate_limit": candidate_limit,
        "keyword_candidates": len(keyword),
        "semantic_candidates": len(semantic),
        "fusion": "rrf" if method == "hybrid" else None,
        "note": "Semantic neighbors and rank scores do not establish answerability.",
    }
    result["has_more"] = result["has_more"] or more_candidates
    return result

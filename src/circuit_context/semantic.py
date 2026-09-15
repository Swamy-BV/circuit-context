"""Prepared semantic vectors with exact cosine search over the small corpus."""

from __future__ import annotations

import json
import math
import os
import tempfile
from functools import lru_cache
from pathlib import Path

from . import local_models
from .corpus import load
from .models import Corpus, Guideline

_TEXT_VERSION = "1"
_DIMENSIONS = 384


def passage(guide: Guideline) -> str:
    """Use the same summary/scope fields as lexical search; full guides stay intact."""
    return "\n".join(
        [
            guide.title,
            " ".join(guide.keywords),
            guide.summary,
            guide.applies_to,
        ]
    )


def _unit(row: list[float]) -> list[float]:
    if len(row) != _DIMENSIONS or not all(math.isfinite(x) for x in row):
        raise ValueError("Invalid semantic vector dimensions or values.")
    norm = math.sqrt(sum(x * x for x in row))
    if norm == 0:
        raise ValueError("Zero-length semantic vector.")
    return [x / norm for x in row]


def _path(digest: str, fingerprint: str) -> Path:
    return local_models.cache_root() / (
        f"semantic-{_TEXT_VERSION}-{digest}-{fingerprint}.json"
    )


def prepare(offline: bool = False, with_reranker: bool = False) -> dict[str, object]:
    """Explicitly prepare pinned models and atomically publish corpus vectors."""
    local_models.prepare_model(local_models.EMBEDDER, offline)
    if with_reranker:
        local_models.prepare_model(local_models.RERANKER, offline)
    corpus, digest = load()
    fingerprint = local_models.fingerprint(local_models.EMBEDDER)
    rows = local_models.embed([passage(g) for g in corpus.guidelines])
    if len(rows) != len(corpus.guidelines):
        raise ValueError("Embedder returned an incorrect vector count.")
    vectors = {g.id: _unit(row) for g, row in zip(corpus.guidelines, rows, strict=True)}
    path = _path(digest, fingerprint)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, suffix=".part")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(
                {
                    "corpus_sha256": digest,
                    "model_fingerprint": fingerprint,
                    "vectors": vectors,
                },
                output,
                allow_nan=False,
            )
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    _read.cache_clear()
    return {
        "ok": True,
        "guides": len(vectors),
        "model": local_models.EMBEDDER.name,
        "model_revision": local_models.EMBEDDER.revision,
        "model_fingerprint": fingerprint,
        "index": str(path),
        "reranker_prepared": with_reranker,
    }


@lru_cache(maxsize=4)
def _read(
    path: str, stamp: int, size: int, digest: str, fingerprint: str
) -> dict[str, list[float]]:
    del stamp, size  # Cache keys invalidate replaced files.
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data["corpus_sha256"] != digest or data["model_fingerprint"] != fingerprint:
            raise ValueError("Semantic index does not match corpus/model.")
        vectors = {key: _unit(value) for key, value in data["vectors"].items()}
        return vectors
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "Invalid semantic index; run prepare-search --offline."
        ) from exc


def eligible(guide: Guideline, filters: dict[str, str]) -> bool:
    """Apply identical explicit scopes before ranking any semantic candidates."""
    return (
        (not filters["topic"] or guide.topic == filters["topic"])
        and (not filters["level"] or guide.level == filters["level"])
        and (not filters["interface"] or filters["interface"] in guide.interfaces)
        and (not filters["domain"] or filters["domain"] in guide.domains)
    )


def ranked_ids(
    query: str, corpus: Corpus, digest: str, filters: dict[str, str], limit: int
) -> list[str]:
    """Read prepared vectors and rank eligible guides without network access."""
    fingerprint = local_models.fingerprint(local_models.EMBEDDER)
    path = _path(digest, fingerprint)
    if not path.is_file():
        raise ValueError("Semantic index is missing or stale; run prepare-search.")
    stat = path.stat()
    vectors = _read(str(path), stat.st_mtime_ns, stat.st_size, digest, fingerprint)
    if set(vectors) != {g.id for g in corpus.guidelines}:
        raise ValueError("Semantic index IDs differ; run prepare-search --offline.")
    query_vector = _unit(local_models.embed([query], query=True)[0])
    scores = [
        (
            guide.id,
            sum(a * b for a, b in zip(query_vector, vectors[guide.id], strict=True)),
        )
        for guide in corpus.guidelines
        if eligible(guide, filters)
    ]
    return [
        identifier
        for identifier, _ in sorted(scores, key=lambda item: (-item[1], item[0]))[
            :limit
        ]
    ]

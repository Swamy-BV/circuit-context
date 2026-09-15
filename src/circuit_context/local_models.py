"""Explicit model preparation and offline, pinned CPU inference."""

from __future__ import annotations

import hashlib
import json
import os
import threading
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ModelSpec:
    """Pin a model's repository revision and required local files."""

    name: str
    repository: str
    revision: str
    weights: str


EMBEDDER = ModelSpec(
    "BAAI/bge-small-en-v1.5",
    "qdrant/bge-small-en-v1.5-onnx-q",
    "52398278842ec682c6f32300af41344b1c0b0bb2",
    "model_optimized.onnx",
)
RERANKER = ModelSpec(
    "Xenova/ms-marco-MiniLM-L-6-v2",
    "Xenova/ms-marco-MiniLM-L-6-v2",
    "a09144355adeed5f58c8ed011d209bf8ee5a1fec",
    "onnx/model.onnx",
)
_FILES = (
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "vocab.txt",
)
_LOCK = threading.RLock()


def cache_root() -> Path:
    """Resolve the shared cache without creating directories."""
    return (
        Path(
            os.environ.get(
                "CIRCUIT_CONTEXT_DIR", str(Path.home() / ".circuit-context" / "cache")
            )
        )
        .expanduser()
        .resolve()
    )


def model_path(spec: ModelSpec) -> Path:
    """Keep pinned revisions in separate directories."""
    return cache_root() / "models" / spec.revision


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def prepare_model(spec: ModelSpec, offline: bool = False) -> None:
    """Download only in this explicit setup command; record exact local bytes."""
    destination = model_path(spec)
    if offline:
        _verify(str(destination), spec)
        return
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise ValueError('Install "circuit-context[search]" first.') from exc
    snapshot_download(
        repo_id=spec.repository,
        revision=spec.revision,
        local_dir=str(destination),
        allow_patterns=[*_FILES, spec.weights, "README.md"],
    )
    hashes = {name: _hash(destination / name) for name in (*_FILES, spec.weights)}
    # Readers require the complete manifest; a partial download is never ready.
    temporary = destination / "verified.json.part"
    temporary.write_text(json.dumps(hashes, sort_keys=True), encoding="utf-8")
    os.replace(temporary, destination / "verified.json")
    _verify.cache_clear()
    _load.cache_clear()


@lru_cache(maxsize=4)
def _verify(path: str, spec: ModelSpec) -> str:
    destination = Path(path)
    manifest = destination / "verified.json"
    if not manifest.is_file():
        raise ValueError(
            "Local search model is not prepared. Run circuit-context "
            "prepare-search --reranker. No download occurs during search."
        )
    hashes = json.loads(manifest.read_text(encoding="utf-8"))
    expected = {*_FILES, spec.weights}
    if not isinstance(hashes, dict) or set(hashes) != expected:
        raise ValueError("Invalid model manifest; run prepare-search again.")
    for name in sorted(expected):
        if _hash(destination / name) != hashes[name]:
            raise ValueError("Model checksum mismatch; run prepare-search again.")
    return hashlib.sha256(manifest.read_bytes()).hexdigest()


def fingerprint(spec: ModelSpec) -> str:
    """Identify model bytes and inference-library versions before loading vectors."""
    digest = _verify(str(model_path(spec)), spec)
    try:
        libraries = [version(name) for name in ("fastembed", "onnxruntime")]
    except PackageNotFoundError as exc:
        raise ValueError('Install "circuit-context[search]" first.') from exc
    return hashlib.sha256(
        json.dumps([spec.name, spec.revision, digest, libraries]).encode()
    ).hexdigest()


@lru_cache(maxsize=4)
def _load(path: str, spec: ModelSpec) -> tuple[Any, Any]:
    _verify(path, spec)
    try:
        from fastembed import TextEmbedding
        from fastembed.rerank.cross_encoder import TextCrossEncoder
        from tokenizers import Tokenizer
    except ImportError as exc:
        raise ValueError('Install "circuit-context[search]" first.') from exc
    cls = TextEmbedding if spec == EMBEDDER else TextCrossEncoder
    model = cls(
        model_name=spec.name,
        specific_model_path=path,
        local_files_only=True,
        threads=2,
        providers=["CPUExecutionProvider"],
    )
    tokenizer = Tokenizer.from_file(str(Path(path) / "tokenizer.json"))
    tokenizer.no_truncation()
    tokenizer.no_padding()
    return model, tokenizer


def embed(texts: list[str], query: bool = False) -> list[list[float]]:
    """Embed locally and reject passages that the model would silently truncate."""
    with _LOCK:
        model, tokenizer = _load(str(model_path(EMBEDDER)), EMBEDDER)
        if any(len(tokenizer.encode(text).ids) > 512 for text in texts):
            raise ValueError("Embedding input exceeds 512 tokens; shorten the input.")
        output = model.query_embed(texts) if query else model.embed(texts)
        return [[float(value) for value in row] for row in output]


def rerank(query: str, documents: list[str]) -> list[float]:
    """Score query/passage pairs locally, without generating an answer."""
    with _LOCK:
        model, tokenizer = _load(str(model_path(RERANKER)), RERANKER)
        if any(len(tokenizer.encode(query, text).ids) > 512 for text in documents):
            raise ValueError("Reranking input exceeds 512 tokens; shorten the query.")
        return [float(score) for score in model.rerank(query, documents)]

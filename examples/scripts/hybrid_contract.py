"""Exercise retrieval failure contracts without downloading optional models."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastmcp import Client

from circuit_context import local_models, semantic
from circuit_context.corpus import load
from circuit_context.retrieval import fuse
from circuit_context.server import mcp


def offline(event: str, args: tuple[object, ...]) -> None:
    """Reject accidental network access, including model setup during a query."""
    del args
    if event == "socket.connect":
        raise RuntimeError("Unexpected network access")


async def exercise(cache: Path, mode: str) -> None:
    """Check the real MCP adapter with missing and corrupted local artifacts."""
    os.environ["CIRCUIT_CONTEXT_DIR"] = str(cache)
    async with Client(mcp, mode=mode) as client:
        for args in ({"method": "hybrid"}, {"rerank": True}):
            result = (
                await client.call_tool(
                    "search_guidelines",
                    {
                        "query": "stackup",
                        **args,
                    },
                )
            ).data
            assert not result["ok"] and "prepare-search" in result["error"]
        result = (
            await client.call_tool(
                "search_guidelines",
                {
                    "query": "ground",
                    "limit": 5,
                    "candidate_limit": 5,
                },
            )
        ).data
        assert result["ok"] and result["has_more"]

        corpus, digest = load()
        filters = {"topic": "", "level": "", "interface": "can", "domain": "pcb"}
        row = [1.0] + [0.0] * 383
        path = semantic._path(digest, "fixture")
        valid = {
            "corpus_sha256": digest,
            "model_fingerprint": "fixture",
            "vectors": {g.id: row for g in corpus.guidelines},
        }
        with (
            patch.object(local_models, "fingerprint", return_value="fixture"),
            patch.object(local_models, "embed", return_value=[row]),
        ):
            for bad in (
                {},
                {**valid, "corpus_sha256": "stale"},
                {**valid, "vectors": {"wrong-id": row}},
                {**valid, "vectors": {g.id: [0.0] for g in corpus.guidelines}},
                {
                    **valid,
                    "vectors": {g.id: [float("nan")] * 384 for g in corpus.guidelines},
                },
            ):
                path.write_text(json.dumps(bad), encoding="utf-8")
                semantic._read.cache_clear()
                result = (
                    await client.call_tool(
                        "search_guidelines",
                        {
                            "query": "termination",
                            "method": "hybrid",
                        },
                    )
                ).data
                assert not result["ok"] and "prepare-search" in result["error"]
            path.write_text(json.dumps(valid), encoding="utf-8")
            semantic._read.cache_clear()
            expected = {
                g.id for g in corpus.guidelines if semantic.eligible(g, filters)
            }
            for method in ("semantic", "hybrid"):
                result = (
                    await client.call_tool(
                        "search_guidelines",
                        {
                            "query": "termination",
                            "method": method,
                            "interface": "can",
                            "domain": "pcb",
                        },
                    )
                ).data
                assert result["ok"] and result["results"]
                assert {hit["id"] for hit in result["results"]} <= expected
                with patch.object(local_models, "rerank", return_value=[float("nan")]):
                    failed = (
                        await client.call_tool(
                            "search_guidelines",
                            {
                                "query": "termination",
                                "method": method,
                                "rerank": True,
                            },
                        )
                    ).data
                    assert not failed["ok"] and "invalid scores" in failed["error"]
    print(f"PASS {mode}: missing setup, cache integrity, filters, score validation")


async def main() -> None:
    """Check deterministic fusion and both MCP protocol modes offline."""
    assert fuse([["a", "a", "b"], ["b", "c"]], 3) == ["b", "a", "c"]
    assert fuse([["b"], ["a"]], 2) == ["a", "b"]
    sys.addaudithook(offline)
    with tempfile.TemporaryDirectory(prefix="circuit-context-contract-") as tmp:
        for mode in ("auto", "legacy"):
            cache = Path(tmp) / mode
            cache.mkdir()
            await exercise(cache, mode)


if __name__ == "__main__":
    asyncio.run(main())

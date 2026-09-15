"""Compare real local retrieval models through MCP; report wins and regressions."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

from fastmcp import Client

from circuit_context.corpus import load
from circuit_context.server import mcp

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    "pcb_knowledge",
    "emc_knowledge",
    "two_layer_knowledge",
    "basic_interface_knowledge",
    "usb_c_knowledge",
    "semantic_knowledge",
)
STRATEGIES = (
    ("keyword", False),
    ("semantic", False),
    ("hybrid", False),
    ("hybrid", True),
)


def offline(event: str, args: tuple[object, ...]) -> None:
    """Fail the run if inference attempts a network connection."""
    del args
    if event == "socket.connect":
        raise RuntimeError("Network access attempted during offline retrieval")


async def run(cache: Path) -> None:
    """Evaluate unchanged fixtures and additional paraphrases through real tools."""
    os.environ["CIRCUIT_CONTEXT_DIR"] = str(cache.resolve())
    cases = [
        dict(case, suite=name)
        for name in FILES
        for case in json.loads(
            (ROOT / "examples/prompts" / f"{name}.json").read_text()
        )["cases"]
    ]
    corpus, _ = load()
    known = {guide.id for guide in corpus.guidelines}
    assert all(not c["expected_id"] or c["expected_id"] in known for c in cases)
    sys.addaudithook(offline)
    rows: list[dict[str, Any]] = []
    async with Client(mcp) as client:
        for method, rerank in STRATEGIES:
            label = method + ("+rerank" if rerank else "")
            # Warm models separately so startup cost is not hidden in query averages.
            start = time.perf_counter()
            warm = (
                await client.call_tool(
                    "search_guidelines",
                    {
                        "query": "stackup",
                        "method": method,
                        "rerank": rerank,
                    },
                )
            ).data
            assert warm["ok"], warm
            print(f"{label}: startup {time.perf_counter() - start:.3f}s", flush=True)
            for i, case in enumerate(cases):
                start = time.perf_counter()
                result = (
                    await client.call_tool(
                        "search_guidelines",
                        {
                            "query": case["query"],
                            **case.get("filters", {}),
                            "method": method,
                            "rerank": rerank,
                            "limit": 3,
                        },
                    )
                ).data
                assert result["ok"], (case, result)
                hits = result["results"]
                for hit in hits:
                    assert hit["citations"] and hit["applies_to"] and hit["limitations"]
                    for key, value in case.get("filters", {}).items():
                        field = (
                            hit[key + "s"] if key in ("interface", "domain") else None
                        )
                        assert (
                            value in field if field is not None else hit[key] == value
                        )
                ids = [hit["id"] for hit in hits]
                expected = case["expected_id"]
                rows.append(
                    {
                        "strategy": label,
                        "suite": case["suite"],
                        "query": case["query"],
                        "expected_id": expected,
                        "ids": ids,
                        "passed": expected in ids if expected else not ids,
                        "elapsed_ms": (time.perf_counter() - start) * 1000,
                    }
                )
                if (i + 1) % 40 == 0:
                    print(f"  {i + 1}/{len(cases)}", flush=True)
    output = ROOT / "out/hybrid-benchmark.json"
    output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    for method, rerank in STRATEGIES:
        label = method + ("+rerank" if rerank else "")
        selected = [r for r in rows if r["strategy"] == label]
        for suite in ("existing", "paraphrases"):
            group = [
                r
                for r in selected
                if (r["suite"] == "semantic_knowledge") == (suite == "paraphrases")
            ]
            print(f"{label} {suite}: {sum(r['passed'] for r in group)}/{len(group)}")
        print(f"  median {statistics.median(r['elapsed_ms'] for r in selected):.1f}ms")
    print(f"Offline checks passed. Results: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    asyncio.run(run(parser.parse_args().cache))

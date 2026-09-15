"""Exercise offline PCB retrieval and provenance through the real MCP surface."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sqlite3
import tempfile
import time
from contextlib import closing
from pathlib import Path
from typing import Any

from fastmcp import Client

from circuit_context.server import mcp

OUT = Path("out/knowledge").resolve()
PROMPTS = Path(__file__).resolve().parents[1] / "prompts"
CASES = (
    PROMPTS / "pcb_knowledge.json", PROMPTS / "emc_knowledge.json",
    PROMPTS / "two_layer_knowledge.json",
    PROMPTS / "basic_interface_knowledge.json",
    PROMPTS / "usb_c_knowledge.json",
    PROMPTS / "four_layer_knowledge.json",
    PROMPTS / "pcb_calculations.json",
)


async def exercise(cache: Path, mode: str) -> dict[str, Any]:
    """Check results, bounds and failure handling without invoking a model."""
    os.environ["CIRCUIT_CONTEXT_DIR"] = str(cache)
    rows = []
    async with Client(mcp, mode=mode) as client:
        tools = {tool.name: tool for tool in await client.list_tools()}
        for name in ("search_guidelines", "get_guideline"):
            assert tools[name].annotations.read_only_hint
        resources = await client.read_resource("circuit-context://catalogue")
        catalogue = json.loads(resources[0].text)
        assert not list(cache.glob("*.sqlite3")), "catalogue should not build cache"
        identifiers = {g["id"] for g in catalogue["guidelines"]}
        sources = {s["id"]: s for s in catalogue["sources"]}
        assert identifiers and sources
        available = catalogue["available_filters"]
        assert set(available["level"]) == {"general", "interface", "mechanical"}
        assert set(available["domain"]) == {"schematic", "pcb", "mechanical"}
        assert {"usb", "can", "rs485", "i2c", "ethernet", "wireless"} <= set(
            available["interface"]
        )
        # Concurrent first use must never expose a partially written index.
        cold = await asyncio.gather(*[
            client.call_tool("search_guidelines", {"query": "stackup"})
            for _ in range(6)
        ])
        assert all(r.data["ok"] and r.data["count"] for r in cold)
        databases = list(cache.glob("*.sqlite3"))
        assert len(databases) == 1 and not list(cache.glob("*.part"))
        original_hash = hashlib.sha256(databases[0].read_bytes()).hexdigest()

        cases = [case for path in CASES
                 for case in json.loads(path.read_text())["cases"]]
        for case in cases:
            start = time.perf_counter()
            reply = await client.call_tool("search_guidelines", {
                "query": case["query"], "limit": 3,
                **case.get("filters", {}),
            })
            elapsed = (time.perf_counter() - start) * 1000
            result = reply.data
            assert result["ok"], result
            hits = result["results"]
            expected = case["expected_id"]
            assert (expected in [h["id"] for h in hits]) if expected else not hits, case
            for hit in hits:
                assert hit["applies_to"] and hit["limitations"]
                assert "pattern" not in hit, "search must not expand topology details"
                for key, value in case.get("filters", {}).items():
                    if key in ("interface", "domain"):
                        assert value in hit[key + "s"], (case, hit)
                    else:
                        assert value == hit[key], (case, hit)
                for citation in hit["citations"]:
                    assert citation["locator"] and citation["id"] in sources
                    assert citation["url"] == sources[citation["id"]]["url"]
                full = (await client.call_tool(
                    "get_guideline", {"id": hit["id"]}
                )).data
                assert full["ok"] and full["corpus_sha256"] == result["corpus_sha256"]
                assert full["guideline"]["required_inputs"]
                assert full["guideline"]["verification"]
                assert set(full["guideline"]["related_ids"]) <= identifiers
                if hit["id"] == expected:
                    assert set(case.get("expected_related", [])) <= set(
                        full["guideline"]["related_ids"]
                    ), case
            rows.append({"query": case["query"], "filters": result["filters"],
                         "ids": [h["id"] for h in hits],
                         "elapsed_ms": round(elapsed, 2),
                         "response_bytes": len(json.dumps(result).encode())})

        # Explicit OR is broader, but topic filtering must remain exact.
        broad = (await client.call_tool("search_guidelines", {
            "query": "grounding routing placement", "match": "any", "limit": 1,
        })).data
        assert broad["count"] == 1 and broad["has_more"]
        filtered = (await client.call_tool("search_guidelines", {
            "query": "grounding routing placement", "match": "any",
            "topic": "placement", "limit": 5,
        })).data
        assert filtered["count"] and all(
            h["topic"] == "placement" for h in filtered["results"]
        )
        for args in ({"query": "the and"}, {"query": "***"},
                     {"query": "stackup", "topic": "unknown"},
                     {"query": "termination", "interface": "unknown"},
                     {"query": "termination", "interface": "ca"},
                     {"query": "termination", "interface": "can|usb"}):
            refused = (await client.call_tool("search_guidelines", args)).data
            assert not refused["ok"]
        for args in ({"query": ""}, {"query": "x" * 501},
                     {"query": "stackup", "limit": 0},
                     {"query": "stackup", "limit": 6},
                     {"query": "stackup", "level": "unknown"},
                     {"query": "stackup", "domain": "unknown"},
                     {"query": "stackup", "match": "guess"}):
            reply = await client.call_tool("search_guidelines", args,
                                           raise_on_error=False)
            assert reply.is_error, args
        assert not (await client.call_tool(
            "get_guideline", {"id": "../../missing"}
        )).data["ok"]
        punctuation = (await client.call_tool("search_guidelines", {
            "query": '"stackup"; DROP TABLE guidance --',
        })).data
        assert punctuation["ok"] and not punctuation["results"]
        assert hashlib.sha256(databases[0].read_bytes()).hexdigest() == original_hash

        # Delete only this example's disposable database bytes, never user data.
        databases[0].write_bytes(b"corrupt cache")
        rebuilt = (await client.call_tool("search_guidelines", {
            "query": "stackup",
        })).data
        assert rebuilt["ok"] and rebuilt["count"]
        # A readable SQLite file with a missing FTS table is also a bad cache.
        with closing(sqlite3.connect(databases[0])) as db, db:
            db.execute("DROP TABLE guidance")
        repaired = (await client.call_tool("search_guidelines", {
            "query": "return path",
        })).data
        assert repaired["ok"] and repaired["count"]
        # Every advertised guide must be retrievable by ID, even if not top-ranked.
        pattern_ids: set[str] = set()
        for identifier in identifiers:
            complete = (await client.call_tool(
                "get_guideline", {"id": identifier}
            )).data
            assert complete["ok"]
            guide = complete["guideline"]
            if guide["kind"] == "routing-pattern":
                assert all(guide["pattern"][key] for key in (
                    "diagram", "placement", "routing", "return_path", "pitfalls"
                ))
                pattern_ids.add(identifier)
            else:
                assert guide["pattern"] is None
        for family in ("gpio", "uart", "spi", "i2c", "usb-c"):
            overview = (await client.call_tool(
                "get_guideline", {"id": f"{family}-overview"}
            )).data["guideline"]
            assert overview["kind"] == "overview"
            assert set(overview["related_ids"]) & pattern_ids
            hit = (await client.call_tool("search_guidelines", {
                "query": "overview", "topic": "interface-overview",
                "interface": family, "domain": "schematic",
            })).data
            assert [g["id"] for g in hit["results"]] == [f"{family}-overview"]
        # Follow the review from its entry point through real MCP reads. Search
        # ranking must not be the only way to reach a required supporting guide.
        pending = ["two-layer-emc-workflow"]
        visited: set[str] = set()
        while pending:
            identifier = pending.pop()
            if identifier in visited:
                continue
            result = (await client.call_tool(
                "get_guideline", {"id": identifier}
            )).data
            assert result["ok"]
            guide = result["guideline"]
            assert guide["id"] == identifier and "guidelines" not in result
            assert set(guide["related_ids"]) <= identifiers
            visited.add(identifier)
            pending.extend(guide["related_ids"])
        assert {
            "fabrication-profile", "board-thickness-choice", "ground-pour-stitching",
            "decoupling-loop", "two-layer-bottom-jump", "power-conductor-sizing",
            "emc-source-termination", "emc-filter-resonance", "crystal-placement",
            "usb-channel-constraints", "i2c-pullup-window", "can-end-termination",
            "rs485-termination-stubs", "ethernet-magnetics-boundary",
            "esd-flow-through", "shield-apertures", "emc-brownout-recovery",
            "two-layer-emc-test-plan", "two-layer-escalation",
            "layout-intent-handoff", "two-layer-power-return-budget",
            "motor-ground-grid", "motor-current-sense-kelvin",
            "capacitive-touch-ground-exception", "touch-fpc-orientation",
            "precision-analog-thermal-gradients", "two-layer-reference-design-transfer",
        } <= visited
    return {"mode": mode, "guidelines": len(identifiers), "sources": len(sources),
            "cases": rows, "workflow_guides": sorted(visited),
            "corpus_sha256": catalogue["corpus_sha256"]}


async def main() -> None:
    """Run both protocol modes using isolated cache directories."""
    OUT.mkdir(parents=True, exist_ok=True)
    previous = os.environ.get("CIRCUIT_CONTEXT_DIR")
    results = []
    try:
        for mode in ("auto", "legacy"):
            with tempfile.TemporaryDirectory(prefix="pcb-knowledge-") as directory:
                results.append(await exercise(Path(directory), mode))
    finally:
        if previous is None:
            os.environ.pop("CIRCUIT_CONTEXT_DIR", None)
        else:
            os.environ["CIRCUIT_CONTEXT_DIR"] = previous
    (OUT / "retrieval.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for row in results:
        print(f"{row['mode']}: {len(row['cases'])} retrieval cases passed; "
              f"{row['guidelines']} guides, {row['sources']} sources")
        print(f"  Workflow: {len(row['workflow_guides'])} linked guides read.")
    print("PASS: citation reads, missing coverage, validation, bounds, "
          "concurrent cold reads and corrupt-cache recovery. AI behavior not measured.")


if __name__ == "__main__":
    asyncio.run(main())

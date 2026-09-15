# Local hybrid retrieval

The caller selects `keyword` (default), `semantic`, or `hybrid` through Python,
CLI or MCP. Hybrid retrieves candidates from BM25 and dense cosine search,
combines their ranks with RRF, and optionally reranks that pool with a local
cross-encoder. The AI client reads the resulting evidence and generates answers.

## Setup

```sh
python -m pip install ".[mcp,search]"
circuit-context prepare-search --reranker
circuit-context search "Where does returning current go when a signal changes layers?" --method hybrid
```

Add `--rerank` to search to enable the cross-encoder. MCP uses `method="hybrid"`
and `rerank=true`. Preparation downloads pinned models from Hugging Face;
queries never download models or call a hosted inference service. Missing models
or stale vectors return errors, without switching strategies. After a corpus or
inference-library change, rebuild with `prepare-search --offline` using already
verified models. Omit `--reranker` if only embeddings are needed.

The search extra pins FastEmbed 0.7.4 and runs CPU ONNX inference with two threads.
Models are loaded lazily and reused. Base keyword search has no model dependency.

| Purpose | Model repository | Pinned revision | License |
| --- | --- | --- | --- |
| Embeddings | qdrant/bge-small-en-v1.5-onnx-q | 52398278842ec682c6f32300af41344b1c0b0bb2 | MIT |
| Reranker | Xenova/ms-marco-MiniLM-L-6-v2 | a09144355adeed5f58c8ed011d209bf8ee5a1fec | Apache-2.0 |

Model downloads retain their model cards. File checksums detect subsequent local
corruption; they are not publisher signatures. Prepared vectors are keyed by
corpus hash, passage format, model bytes/revision and inference-library versions.
Files live under `CIRCUIT_CONTEXT_DIR` or `~/.circuit-context/cache/`.

## Retrieval contract

- Both paths search title, keywords, summary and applicability. Full guidance,
  limitations and citations remain available through `get_guideline`.
- Exact scope filters apply before candidate selection in both paths.
- `match=all|any` controls only BM25. Semantic candidates need not contain query words.
- Each path supplies up to `candidate_limit` candidates (default 20, range 5–100).
  RRF assigns each guide the sum of `1 / (60 + rank)` across paths, with ranks
  starting at one. Equal scores break ties by guide ID. The fused pool is bounded
  by the same candidate limit; optional reranking sees only that pool.
- Public results remain limited to 1–5 guides. `has_more` reports additional
  candidates, including candidates excluded by the pool bound.
- Embedding search uses exact cosine comparison over the small corpus, without a
  vector database. Inputs exceeding model token limits are rejected rather than
  silently truncated. Reranker limits apply to the combined query/passage pair.
- Rank scores are not confidence or proof of coverage. There is no calibrated
  semantic abstention threshold. Read scope and evidence before answering.

## Measured comparison

Run after preparing models:

```sh
python examples/scripts/hybrid_contract.py
python examples/scripts/hybrid_benchmark.py --cache out/hybrid-cache
```

The `--cache` path must match the directory used during preparation. The example
above assumes `CIRCUIT_CONTEXT_DIR` was set to `out/hybrid-cache` before running
`prepare-search`; otherwise pass the default `~/.circuit-context/cache` path.

The benchmark uses real MCP calls and blocks socket connections during retrieval.
On the development Windows CPU, corpus version 2026-09-14.7 (98 guides), results
were measured with limit 3 and candidate limit 20:

| Strategy | Existing cases | New paraphrases | Median warm query |
| --- | --- | --- | --- |
| Keyword, strict all terms | 152/152 | 0/12 | 2.1 ms |
| Semantic | 135/152 | 12/12 | 7.1 ms |
| Hybrid | 138/152 | 12/12 | 10.6 ms |
| Hybrid + reranker | 138/152 | 11/12 | 380.6 ms |

An existing case passes when its expected guide appears in the first three hits,
or an expected-empty query returns no hits. All 14 hybrid failures were
expected-empty cases: semantic neighbors appeared for unsupported or deliberately
mismatched requests, including DDR5 termination and USB4 compliance procedures.
They must not be treated as answers. The reranker did not improve the aggregate
existing-case result and regressed one paraphrase; it remains off by default.
Keyword remains the default to preserve existing behavior. Callers can explicitly
choose hybrid for paraphrased questions.

These are retrieval checks, not independent engineering or AI reasoning evaluations.
The 12 paraphrases are a small, locally authored set. The baseline uses strict
keyword matching; these numbers do not compare hybrid against a tuned `match=any`
workflow. Timings depend on hardware and exclude preparation and model startup.
Generated per-query results are stored in ignored `out/hybrid-benchmark.json`.

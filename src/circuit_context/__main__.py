"""Command-line access to the same evidence as the MCP tools."""

from __future__ import annotations

import argparse
import json
import sqlite3

from . import index, retrieval


def main() -> None:
    """Run offline retrieval or the optional stdio MCP server."""
    parser = argparse.ArgumentParser(description="Hardware engineering knowledge")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("serve", help="Run the read-only stdio MCP server")
    commands.add_parser("catalogue", help="List coverage and source editions")
    prepare = commands.add_parser(
        "prepare-search", help="Download pinned models and build local vectors",
    )
    prepare.add_argument("--reranker", action="store_true")
    prepare.add_argument("--offline", action="store_true",
                         help="Rebuild using previously verified local models")
    get = commands.add_parser("get", help="Read a guide by its exact ID")
    get.add_argument("id")
    search = commands.add_parser("search", help="Search editorial guidance")
    search.add_argument("query")
    search.add_argument("--topic", default="")
    search.add_argument("--level", default="")
    search.add_argument("--interface", default="")
    search.add_argument("--domain", default="")
    search.add_argument("--limit", type=int, default=3)
    search.add_argument("--match", choices=("all", "any"), default="all")
    search.add_argument("--method", choices=("keyword", "semantic", "hybrid"),
                        default="keyword")
    search.add_argument("--rerank", action="store_true")
    search.add_argument("--candidate-limit", type=int, default=20)
    args = parser.parse_args()
    if args.command == "serve":
        try:
            from .server import mcp
        except ModuleNotFoundError as exc:
            if exc.name != "fastmcp":
                raise
            parser.error('Install the MCP extra: pip install "circuit-context[mcp]"')
        mcp.run(transport="stdio")
        return
    try:
        if args.command == "prepare-search":
            from .semantic import prepare as prepare_search

            result = prepare_search(args.offline, args.reranker)
        elif args.command == "get":
            result = index.get(args.id)
        elif args.command == "catalogue":
            result = index.catalogue()
        else:
            result = retrieval.search(
                args.query, args.topic, args.limit, args.match,
                level=args.level, interface=args.interface, domain=args.domain,
                method=args.method, rerank=args.rerank,
                candidate_limit=args.candidate_limit,
            )
    except (OSError, ValueError, sqlite3.Error) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()

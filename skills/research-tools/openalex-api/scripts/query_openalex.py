#!/usr/bin/env python3
"""Query OpenAlex entities with search/filter/pagination support."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BASE_URL = "https://api.openalex.org"
ENTITY_CHOICES = [
    "works",
    "authors",
    "institutions",
    "sources",
    "concepts",
    "topics",
    "funders",
    "publishers",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query OpenAlex and export results.")
    parser.add_argument("entity", choices=ENTITY_CHOICES, help="OpenAlex entity route")
    parser.add_argument("--entity-id", help="Fetch one entity by ID (for example W2741809807)")
    parser.add_argument("--search", help="Free-text search value")
    parser.add_argument(
        "--filter",
        action="append",
        default=[],
        help="One filter expression, repeat for AND logic",
    )
    parser.add_argument("--select", help="Comma-separated fields to return")
    parser.add_argument(
        "--sort",
        action="append",
        default=[],
        help="Sort expression, repeat to apply multiple sorts",
    )
    parser.add_argument("--per-page", type=int, default=25, help="Results per page (max 200)")
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Page count for basic paging mode (ignored when --cursor is set)",
    )
    parser.add_argument(
        "--cursor",
        help="Cursor value for deep paging. Use '*' to start cursor pagination.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=200,
        help="Maximum records to collect in list mode",
    )
    parser.add_argument("--sample", type=int, help="Sample size supported by OpenAlex")
    parser.add_argument("--seed", type=int, help="Seed for deterministic sampling")
    parser.add_argument("--mailto", help="Contact email to include in User-Agent")
    parser.add_argument(
        "--api-key",
        default=os.getenv("OPENALEX_API_KEY"),
        help="OpenAlex API key (defaults to OPENALEX_API_KEY)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "jsonl"],
        default="json",
        help="Output format",
    )
    parser.add_argument(
        "--output",
        default="-",
        help="Output path. Use '-' for stdout.",
    )
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")
    parser.add_argument(
        "--retries",
        type=int,
        default=4,
        help="Retry attempts for 429/5xx responses",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print final request URL(s) without sending requests",
    )
    return parser


def encode_params(params: dict[str, Any]) -> str:
    clean = {k: v for k, v in params.items() if v is not None and v != ""}
    return urllib.parse.urlencode(clean)


def build_url(entity: str, entity_id: str | None, params: dict[str, Any]) -> str:
    base = f"{BASE_URL}/{entity}"
    if entity_id:
        base = f"{base}/{entity_id}"
    query = encode_params(params)
    if not query:
        return base
    return f"{base}?{query}"


def request_json(url: str, timeout: int, retries: int, mailto: str | None) -> dict[str, Any]:
    user_agent = "codex-openalex-skill/1.0"
    if mailto:
        user_agent += f" ({mailto})"
    headers = {
        "Accept": "application/json",
        "User-Agent": user_agent,
    }

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = resp.read().decode("utf-8")
                return json.loads(payload)
        except urllib.error.HTTPError as err:
            last_error = err
            retriable = err.code == 429 or err.code >= 500
            if attempt >= retries or not retriable:
                detail = err.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"HTTP {err.code} for {url}: {detail}") from err
            retry_after = err.headers.get("Retry-After")
            sleep_seconds = float(retry_after) if retry_after and retry_after.isdigit() else 1.5 * (attempt + 1)
            time.sleep(sleep_seconds)
        except urllib.error.URLError as err:
            last_error = err
            if attempt >= retries:
                raise RuntimeError(f"Request failed for {url}: {err}") from err
            time.sleep(1.5 * (attempt + 1))

    if last_error:
        raise RuntimeError(f"Request failed for {url}: {last_error}") from last_error
    raise RuntimeError(f"Request failed for {url}")


def list_params(args: argparse.Namespace) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if args.search:
        params["search"] = args.search
    if args.filter:
        params["filter"] = ",".join(args.filter)
    if args.select:
        params["select"] = args.select
    if args.sort:
        params["sort"] = ",".join(args.sort)
    if args.sample is not None:
        params["sample"] = args.sample
    if args.seed is not None:
        params["seed"] = args.seed
    if args.api_key:
        params["api_key"] = args.api_key
    return params


def collect_with_cursor(args: argparse.Namespace, base_params: dict[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    rows: list[dict[str, Any]] = []
    cursor = args.cursor
    next_cursor = cursor
    while len(rows) < args.max_results:
        params = dict(base_params)
        params["cursor"] = next_cursor
        params["per-page"] = min(args.per_page, 200)
        url = build_url(args.entity, None, params)
        if args.dry_run:
            print(url)
            break
        payload = request_json(url, timeout=args.timeout, retries=args.retries, mailto=args.mailto)
        batch = payload.get("results", [])
        if not batch:
            break
        remaining = args.max_results - len(rows)
        rows.extend(batch[:remaining])
        next_cursor = payload.get("meta", {}).get("next_cursor")
        if not next_cursor:
            break
    return rows, next_cursor


def collect_with_pages(args: argparse.Namespace, base_params: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    page = 1
    while page <= args.pages and len(rows) < args.max_results:
        params = dict(base_params)
        params["page"] = page
        params["per-page"] = min(args.per_page, 200)
        url = build_url(args.entity, None, params)
        if args.dry_run:
            print(url)
            break
        payload = request_json(url, timeout=args.timeout, retries=args.retries, mailto=args.mailto)
        batch = payload.get("results", [])
        if not batch:
            break
        remaining = args.max_results - len(rows)
        rows.extend(batch[:remaining])
        page += 1
    return rows


def write_output(args: argparse.Namespace, payload: Any) -> None:
    destination = sys.stdout if args.output == "-" else open(args.output, "w", encoding="utf-8")
    try:
        if args.format == "json":
            json.dump(payload, destination, ensure_ascii=False, indent=2)
            destination.write("\n")
            return
        if not isinstance(payload, dict) or "results" not in payload:
            raise ValueError("JSONL output requires list-mode payload with a results field.")
        for row in payload["results"]:
            destination.write(json.dumps(row, ensure_ascii=False) + "\n")
    finally:
        if destination is not sys.stdout:
            destination.close()


def main() -> int:
    args = build_parser().parse_args()

    if args.per_page < 1 or args.per_page > 200:
        raise ValueError("--per-page must be between 1 and 200")
    if args.pages < 1:
        raise ValueError("--pages must be >= 1")
    if args.max_results < 1:
        raise ValueError("--max-results must be >= 1")
    if args.entity_id and args.cursor:
        raise ValueError("--entity-id cannot be used with --cursor")

    params = list_params(args)

    if args.entity_id:
        url = build_url(args.entity, args.entity_id, params)
        if args.dry_run:
            print(url)
            return 0
        payload = request_json(url, timeout=args.timeout, retries=args.retries, mailto=args.mailto)
        if args.format == "jsonl":
            raise ValueError("--format jsonl is not valid with --entity-id")
        write_output(args, payload)
        return 0

    if args.cursor:
        rows, next_cursor = collect_with_cursor(args, params)
        if args.dry_run:
            return 0
        payload: dict[str, Any] = {
            "entity": args.entity,
            "retrieved_results": len(rows),
            "next_cursor": next_cursor,
            "results": rows,
        }
    else:
        rows = collect_with_pages(args, params)
        if args.dry_run:
            return 0
        payload = {
            "entity": args.entity,
            "retrieved_results": len(rows),
            "results": rows,
        }

    write_output(args, payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)

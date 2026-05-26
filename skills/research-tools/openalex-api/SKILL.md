---
name: openalex-api
description: Access and analyze OpenAlex scholarly metadata through the REST API, including works, authors, institutions, sources, concepts, topics, funders, and publishers. Use when asked to retrieve publication or citation metadata, run OpenAlex searches with filters, map author-institution relationships, or build reproducible bibliometric datasets from OpenAlex.
curated-by: John Barrios
collection: barrios-skills
---
> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# OpenAlex API

## Overview

Use this skill to turn research questions into reliable OpenAlex API queries and structured outputs. Prefer `scripts/query_openalex.py` for repeatable retrieval, pagination, and filter-safe URL construction.

## Workflow

1. Define the target entity: `works`, `authors`, `institutions`, `sources`, `concepts`, `topics`, `funders`, or `publishers`.
2. Define retrieval scope: exact ID lookup, search, or filtered dataset pull.
3. Build query parameters with `scripts/query_openalex.py` instead of handcrafting URLs.
4. Retrieve data to JSON/JSONL and keep the raw export before downstream cleaning.
5. Validate key fields (IDs, dates, citation counts, authorships) before analysis.

## Query Rules

- Use repeated `--filter` flags for AND logic.
- Use OpenAlex pipe syntax (for example `value1|value2`) inside one filter for OR logic.
- Use `--select` to reduce payload size for large pulls.
- Use `--cursor '*'` for deep paging beyond basic page limits.
- Include `--mailto you@domain.edu` for polite-pool style identification.
- Use `OPENALEX_API_KEY` or `--api-key` when available for higher-rate access.

## Common Commands

```bash
# Fetch one work by OpenAlex ID
python3 scripts/query_openalex.py works --entity-id W2741809807 --select "id,display_name,publication_year,cited_by_count"

# Search works and save first 200 records
python3 scripts/query_openalex.py works \
  --search "political polarization" \
  --filter "from_publication_date:2020-01-01" \
  --sort "cited_by_count:desc" \
  --per-page 100 \
  --pages 2 \
  --output polarization_works.json

# Cursor-paginate author records to JSONL
python3 scripts/query_openalex.py authors \
  --filter "last_known_institutions.country_code:US" \
  --cursor "*" \
  --max-results 500 \
  --format jsonl \
  --output us_authors.jsonl
```

## Output Guidance

- Prefer JSON for full response bundles and JSONL for row-wise pipelines.
- Keep original IDs (`id`, `ids.openalex`, DOI fields) unchanged in exports.
- When reporting findings, cite exact query parameters used to ensure reproducibility.

## Resources

- Use `scripts/query_openalex.py` for all API calls.
- Use `references/openalex-query-patterns.md` for entity routing, filter templates, and reusable query patterns.

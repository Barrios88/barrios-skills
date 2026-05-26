---
name: econ-lit-search
description: Search a curated corpus of ~51k economics papers (NBER working papers, JEL-coded journals) with full-text search, abstract retrieval, body-passage snippets, and citation sorting. Use this skill whenever the user asks to search for papers, find literature, look up references, do a lit review, check what's been published on a topic, find papers by an author, or any other request that involves discovering or retrieving academic economics papers. Also trigger when the user says "search econ-lit", "search the corpus", "find me papers on…", "what papers exist about…", "look up [topic] in the literature", or similar. This skill searches a local indexed corpus — it does NOT overlap with OpenAlex (which covers 240M+ works broadly). Let the user decide which to use; do not auto-combine with OpenAlex unless asked.
---

# Econ-Lit Search

Search a Meilisearch-powered index of ~51k economics papers. The corpus covers NBER working papers and JEL-coded journal articles with full text, abstracts, author metadata, citation counts, JEL codes, and DOIs.

## Setup

The helper script at `scripts/econ_lit_search.py` handles all API interaction. Import it like this:

```python
import sys
sys.path.insert(0, "<this skill's directory>/scripts")
from econ_lit_search import EconLitSearch

api = EconLitSearch()
```

The API key and endpoint are baked into the script. No environment variables needed.

## Workflow: how to run a literature search

Follow this progression from broad to narrow. Each step uses more tokens, so start lean and drill in only where needed.

### 1. Broad scan (cheap — metadata + short snippet)

Start here. Returns titles, authors, journal, year, citation count, DOI, and a ~60-word abstract snippet. Sorted by citations by default.

```python
results = api.scan("gig economy entrepreneurship", limit=10, filter="year > 2015")
api.print_hits(results, show_abstract=True)
```

Use this to orient: which authors keep appearing? Which journals? What's the citation landscape?

### 2. Narrow with full abstracts (moderate)

Once you've spotted a thread, switch to `read_abstracts()`. This uses `matchingStrategy: "all"` so every query term must appear. Returns full abstracts with keyword highlighting.

```python
results = api.read_abstracts("occupational licensing labor market regulation", limit=5, filter="year > 2005")
api.print_hits(results, show_abstract=True)
```

### 3. Body snippets (moderate — see how papers discuss a method/concept)

Want to see how papers talk about a specific method or idea without downloading full text? `body_snippets()` returns a ~300-char window from inside the paper centered on the best match.

```python
results = api.body_snippets("staggered difference in differences treatment effects", limit=5, filter="year > 2015")
api.print_hits(results, show_body=True)
```

### 4. Full text (expensive — use sparingly)

Only when you've identified a specific paper you need to read in full. Responses can be 10k–50k+ chars. Always target a specific paper by DOI.

```python
result = api.full_text("10.3386/w26783")
paper = result["hits"][0]
print(paper["body"])
```

### 5. Explore the corpus (free — no documents returned)

Use `facets()` to understand coverage before searching. Returns counts per journal, year, JEL code — zero document content.

```python
results = api.facets("corporate disclosure", facet_fields=["journal", "year"])
print(results["facetDistribution"])
```

## Common patterns

### Search by author
```python
results = api.by_author("Yael V. Hochberg", limit=20)
api.print_hits(results)
```

### Filter by JEL codes
```python
results = api.search(
    "regulation entry barriers",
    limit=10,
    filter='jel_codes IN ["L26", "M41", "J44"] AND year > 2015',
    attributesToRetrieve=["title", "authors", "year", "jel_codes", "cited_by_count"],
    sort=["cited_by_count:desc"],
)
```

### Filter by journal
```python
results = api.search(
    "",
    limit=10,
    filter='journal = "Journal of Accounting Research"',
    attributesToRetrieve=["title", "authors", "year", "cited_by_count"],
    sort=["cited_by_count:desc"],
)
```

### Year ranges
```python
results = api.search(
    "financial reporting quality",
    limit=10,
    filter="year >= 2018 AND year <= 2025",
    attributesToRetrieve=["title", "authors", "year", "cited_by_count"],
    sort=["year:desc"],
)
```

### Most-cited in a journal
```python
results = api.search(
    "",
    limit=10,
    filter='journal = "Journal of Financial Economics"',
    attributesToRetrieve=["title", "authors", "year", "cited_by_count"],
    sort=["cited_by_count:desc"],
)
```

## Presenting results to the user

When showing search results, format them cleanly. For a broad scan, a table or numbered list works well:

```
1. "Paper Title" — Card, et al. (2021) — QJE — Cited 342x
2. "Another Paper" — Autor (2019) — AER — Cited 218x
```

When the user asks for detail on specific papers, show the abstract or body snippet inline. For full text, summarize key sections rather than dumping the entire body unless they explicitly ask for it.

## Field reference

| Field | Type | Filterable | Sortable |
|---|---|---|---|
| title | string | no | no |
| authors | string[] | yes | no |
| abstract | string | no | no |
| body | string | no | no |
| journal | string | yes | no |
| year | number | yes | yes |
| jel_codes | string[] | yes | no |
| cited_by_count | number | no | yes |
| doi | string | yes | no |
| url | string | no | no |
| text_char_count | number | no | yes |

## Important constraints

- **Rate limit**: 2 requests/second, burst of 5. Space requests if doing multiple sequential searches.
- **Max results per request**: 50.
- **Full text is large**: 10k–50k+ chars per paper. Only fetch `body` when you need it, and keep `limit` low (1–3).
- **Author names must match exactly** in filters. Use the `scan()` results to find the exact name string before filtering.
- **`body` is only in `_formatted`** when using crops/highlights. The raw `body` field must be explicitly requested via `attributesToRetrieve`.

"""
Econ-Lit Search API client.

Searches ~51k economics papers (NBER, JEL-coded journals) via Meilisearch.
Supports broad scans, narrowed searches, body snippets, full-text retrieval,
facet exploration, and filtering by author/journal/year/JEL code.

Usage:
    from scripts.econ_lit_search import EconLitSearch

    api = EconLitSearch()
    results = api.search("gig economy entrepreneurship", limit=10)
    for hit in results["hits"]:
        print(hit["title"], hit["year"])
"""

import json
import os
import sys
import urllib.request

MEILI_KEY = os.environ.get("MEILI_API_KEY", "")
MEILI_URL = "${MEILI_HOST:-https://your-search-host.example.com}/indexes/public-econ-lit/search"


class EconLitSearch:
    """Client for the econ-lit Meilisearch index."""

    def __init__(self, key=None, url=None):
        self.key = key or MEILI_KEY
        self.url = url or MEILI_URL

    # ── core request ────────────────────────────────────────────────

    def _post(self, body: dict) -> dict:
        req = urllib.request.Request(
            self.url,
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    # ── public methods ──────────────────────────────────────────────

    def search(self, query: str, limit: int = 10, **kwargs) -> dict:
        """
        General-purpose search. All Meilisearch search params accepted as kwargs.

        Common kwargs:
            filter:                 e.g. 'year > 2015', 'authors = "Card"'
            sort:                   e.g. ["cited_by_count:desc"]
            matchingStrategy:       "all" for strict, "last" (default) for lenient
            attributesToRetrieve:   list of fields to return
            attributesToCrop:       e.g. ["abstract:60", "body:300"]
            attributesToHighlight:  e.g. ["abstract", "body"]
            highlightPreTag/Post:   e.g. "<hit>", "</hit>"
            facets:                 e.g. ["journal", "year"]
        """
        body = {"q": query, "limit": limit, **kwargs}
        return self._post(body)

    def scan(self, query: str, limit: int = 10, **kwargs) -> dict:
        """
        Broad literature scan — returns metadata + short abstract snippet.
        Token-efficient; good for initial exploration.
        Sorted by citation count descending by default.
        """
        defaults = dict(
            attributesToRetrieve=["title", "authors", "journal", "year",
                                  "cited_by_count", "doi"],
            attributesToCrop=["abstract:60"],
            attributesToHighlight=["abstract"],
            highlightPreTag="<hit>",
            highlightPostTag="</hit>",
            sort=["cited_by_count:desc"],
        )
        defaults.update(kwargs)
        return self.search(query, limit=limit, **defaults)

    def read_abstracts(self, query: str, limit: int = 5, **kwargs) -> dict:
        """
        Narrowed search — full abstracts with highlighting.
        Uses matchingStrategy 'all' by default for precision.
        """
        defaults = dict(
            matchingStrategy="all",
            attributesToRetrieve=["title", "authors", "journal", "year",
                                  "cited_by_count", "doi"],
            attributesToHighlight=["title", "abstract"],
            highlightPreTag="<hit>",
            highlightPostTag="</hit>",
            sort=["cited_by_count:desc"],
        )
        defaults.update(kwargs)
        return self.search(query, limit=limit, **defaults)

    def body_snippets(self, query: str, limit: int = 5,
                      snippet_len: int = 300, **kwargs) -> dict:
        """
        Search inside paper bodies — returns a ~snippet_len char window
        centered on the best-matching passage. Great for seeing how papers
        discuss a specific method or concept without downloading full text.
        """
        defaults = dict(
            attributesToRetrieve=["title", "authors", "year", "doi"],
            attributesToCrop=[f"abstract:80", f"body:{snippet_len}"],
            attributesToHighlight=["abstract", "body"],
            highlightPreTag="<hit>",
            highlightPostTag="</hit>",
            sort=["cited_by_count:desc"],
        )
        defaults.update(kwargs)
        return self.search(query, limit=limit, **defaults)

    def full_text(self, doi: str) -> dict:
        """Retrieve a single paper's full text by DOI."""
        return self.search(
            "",
            limit=1,
            filter=f'doi = "{doi}"',
            attributesToRetrieve=["title", "authors", "year", "doi",
                                  "abstract", "body", "journal",
                                  "cited_by_count", "jel_codes"],
        )

    def by_author(self, author_name: str, limit: int = 20, **kwargs) -> dict:
        """Find all papers by an author, sorted by citations."""
        defaults = dict(
            attributesToRetrieve=["title", "authors", "journal", "year",
                                  "cited_by_count", "doi"],
            sort=["cited_by_count:desc"],
        )
        defaults.update(kwargs)
        return self.search(
            "",
            limit=limit,
            filter=f'authors = "{author_name}"',
            **defaults,
        )

    def facets(self, query: str = "", facet_fields=None, **kwargs) -> dict:
        """
        Get facet counts (papers per journal, year, JEL code) without
        returning any documents. Useful for understanding corpus coverage
        before drilling in.
        """
        if facet_fields is None:
            facet_fields = ["journal", "year"]
        return self.search(query, limit=0, facets=facet_fields, **kwargs)

    # ── display helpers ─────────────────────────────────────────────

    @staticmethod
    def fmt_authors(authors):
        if not authors:
            return "Unknown"
        if len(authors) > 1:
            return f"{authors[0]}, et al."
        return authors[0]

    def print_hits(self, results: dict, show_abstract: bool = False,
                   show_body: bool = False):
        """Pretty-print search results to stdout."""
        hits = results.get("hits", [])
        total = results.get("estimatedTotalHits", len(hits))
        print(f"≈{total} total results, showing {len(hits)}:\n")

        for i, hit in enumerate(hits, 1):
            f = hit.get("_formatted", {})
            authors = self.fmt_authors(hit.get("authors"))
            year = hit.get("year", "?")
            journal = hit.get("journal", "")
            cites = hit.get("cited_by_count", 0)
            doi = hit.get("doi", "")
            title = f.get("title", hit.get("title", "Untitled"))

            print(f"[{i}] {title}")
            print(f"    {authors} ({year}) — {journal}")
            print(f"    Cited {cites}x | doi:{doi}")

            if show_abstract and "abstract" in f:
                print(f"    Abstract: {f['abstract']}")
            if show_body and "body" in f:
                print(f"    Passage: {f['body']}")
            print()


# ── CLI usage ───────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python econ_lit_search.py <query> [limit]")
        sys.exit(1)

    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    api = EconLitSearch()
    results = api.scan(query, limit=limit)
    api.print_hits(results, show_abstract=True)

# OpenAlex Query Patterns

## Entity Routing

- Use `works` for publications, citation counts, venues, and authorships.
- Use `authors` for profile-level metrics and affiliations.
- Use `institutions` for organization metadata and geo fields.
- Use `sources` for journals/conference venues.
- Use `concepts` and `topics` for topical tagging and hierarchy.
- Use `funders` and `publishers` for funding/publishing organization analysis.

## Filter Templates

- Publication date window: `from_publication_date:2020-01-01,to_publication_date:2024-12-31`
- Publication year range: `from_publication_year:2018,to_publication_year:2025`
- Institution constraint: `institutions.id:I97018004`
- Country constraint (author affiliation): `authorships.institutions.country_code:US`
- Open access only: `is_oa:true`
- DOI-present records: `has_doi:true`
- Multiple values (OR): `institutions.country_code:US|CA|GB`

Use repeated `--filter` arguments for AND:

```bash
python3 scripts/query_openalex.py works \
  --filter "from_publication_year:2020" \
  --filter "is_oa:true"
```

## Select Patterns

- Minimal bibliometrics: `id,display_name,publication_year,cited_by_count`
- Authorship-focused: `id,display_name,authorships,primary_location`
- Provenance-heavy: `id,ids,doi,open_access,primary_location`

## Example Queries

```bash
# Top-cited works in a topic since 2020
python3 scripts/query_openalex.py works \
  --search "partisan polarization" \
  --filter "from_publication_date:2020-01-01" \
  --sort "cited_by_count:desc" \
  --select "id,display_name,publication_year,cited_by_count,authorships" \
  --per-page 100 \
  --pages 3 \
  --output top_cited_polarization.json

# Sample US institutions
python3 scripts/query_openalex.py institutions \
  --filter "country_code:US" \
  --sample 100 \
  --seed 42 \
  --output us_institutions_sample.json

# Cursor-paginate large author pull to JSONL
python3 scripts/query_openalex.py authors \
  --filter "last_known_institutions.country_code:US" \
  --cursor "*" \
  --max-results 1000 \
  --format jsonl \
  --output us_authors.jsonl
```

## Reproducibility Checklist

- Save exact command strings with arguments in your project notes.
- Keep raw JSON/JSONL exports before transformation.
- Preserve OpenAlex IDs and DOI fields without rewriting.
- Record retrieval date for each dataset extraction.

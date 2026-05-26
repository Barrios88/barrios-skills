---
name: web-scrape
description: >
  Web scraping skill for economists and applied researchers. Use this skill
  whenever the user wants to extract data from websites, scrape tables, download
  PDFs, access paywalled academic journals (JSTOR, ScienceDirect, Elsevier,
  NBER, SSRN, AER, etc.), bulk-download papers, scrape government data, hit
  REST APIs, or build reusable scraping scripts. Triggers on: "scrape", "download
  PDF", "get data from", "pull from website", "extract table", "journal article",
  "paywall", "curl", "Playwright", "bulk download", "DOI download", or any
  request to collect data from an external URL. Always use this skill — even for
  seemingly simple scrape tasks — because tool selection (curl vs. curl_yale vs.
  browserless vs. Playwright) matters enormously and the wrong choice silently
  fails.
curated-by: John Barrios
collection: barrios-skills
---
> **Barrios Skills** — John Barrios's curated workflow for economists and accountants. Prioritize reproducible empirical work, clear identification language, and journal-ready output.

# Web Scraping — Economist's Toolkit

## Guiding principle: escalate only as needed

Start simple, escalate when blocked. The tiers:

```
curl / curl_chrome142   →  fastest, works for most static pages and APIs
curl_yale               →  add Yale IP for paywalled journals + PDFs
url-scrape / url-content→  add JS rendering (browserless) for SPAs and dynamic tables
Playwright via WS       →  full browser for login flows, pagination, complex interactions
```

Never jump to Playwright when `curl_chrome142` will do. The escalation cost is real: each tier is slower and more complex.

---

## Quick decision table

| Target | Tool |
|---|---|
| Open static page or government data | `curl_chrome142` |
| REST API / JSON endpoint | `curl` |
| JSTOR, ScienceDirect, Elsevier, AER, any paywall | `curl_yale` |
| PDF via DOI redirect | `curl_yale -sfL -o file.pdf` |
| NBER, SSRN (usually open, sometimes gated) | try `curl_chrome142` first, then `curl_yale` |
| Table that renders via JavaScript | `url-scrape -s 'table'` or `url-content` |
| SPA / React app | `url-content -w '.main-selector'` |
| Login flow, multi-page pagination, form submission | Playwright via WebSocket |
| Bulk download: list of DOIs / URLs | loop + `curl_yale` (see patterns below) |

---

## Tool reference

### `curl_chrome142` — bot-resistant scraping (no paywall)

Uses curl-impersonate: real Chrome 142 TLS fingerprint, defeats most Cloudflare/Akamai blocks.

```bash
# Scrape page text
curl_chrome142 -sf https://example.com | htmlq 'article' --text

# Extract all links
curl_chrome142 -sf https://example.com | htmlq 'a' --attribute href

# Hit a JSON API
curl -sf 'https://api.bls.gov/publicAPI/v2/timeseries/data/' | jq '.Results.series[0].data'

# Download a file
curl_chrome142 -sfL -o paper.pdf https://example.com/paper.pdf
```

### `curl_yale` — paywalled journal access

Routes through a SOCKS5 proxy on the Yale network. Requires the proxy to be running — see [setup-yale.md](./references/setup-yale.md) if `curl_yale` is unavailable or times out.

```bash
# Download a JSTOR article as HTML
curl_yale -sfL 'https://www.jstor.org/stable/10.2307/1234567' -o article.html

# Download a PDF via DOI (follows redirects to publisher PDF)
curl_yale -sfL 'https://doi.org/10.1257/aer.20150154' -o paper.pdf

# Scrape article metadata from ScienceDirect
curl_yale -sf 'https://www.sciencedirect.com/science/article/pii/S0304405X19301234' | htmlq 'meta[name="citation_title"]' --attribute content

# Verify your Yale IP is active
curl_yale -sf https://httpbin.org/ip | jq .
```

### `url-scrape` — extract specific elements from JS-rendered pages

Returns JSON with text + HTML for each matched CSS selector. Use when the page requires JavaScript to render (inspect page source: if the data isn't there, it's JS-rendered).

```bash
# Scrape a dynamic table
url-scrape -s 'table' https://example.com/data | jq '.data[0].results[].html'

# Multiple selectors
url-scrape -s 'h1' -s '.abstract' -s 'table.results' https://journal.com/article

# Wait for content to load, skip images for speed
url-scrape -s '.data-table' -w '.data-table' -r image,stylesheet,font https://spa-app.com

# Save output
url-scrape -s 'table' https://example.com ./tmp/scraped.json

# Extract just the text from results
url-scrape -s 'p.abstract' https://example.com | jq '.data[0].results[].text'
```

### `url-content` — get full rendered HTML

Use when you need the whole page after JS runs, then pipe to `htmlq`/`pup`.

```bash
# Get full rendered HTML, extract article
url-content https://example.com | htmlq 'article' --text

# Wait for SPA content
url-content -w '.main-content' -r image,stylesheet,font https://spa-site.com | htmlq 'table'

# Save page for inspection
url-content https://example.com > ./tmp/page.html
```

### Playwright via WebSocket — full browser control

For multi-step scraping only: login flows, pagination clicking, form interaction. See [playwright-patterns.md](./references/playwright-patterns.md) for complete examples.

```bash
# Quick template — Python (preferred for data work)
uv run --with playwright python3 -c "
import json, urllib.parse
from playwright.sync_api import sync_playwright

token = '$BROWSERLESS_TOKEN'
host = '$BROWSERLESS_HOST'
launch = urllib.parse.quote(json.dumps({'stealth': True, 'args': ['--disable-blink-features=AutomationControlled']}))
ws = f'wss://{host}/chromium/playwright?token={token}&launch={launch}'

with sync_playwright() as p:
    browser = p.chromium.connect(ws)
    page = browser.new_page()
    page.goto('https://example.com')
    # your logic here
    print(page.content())
    browser.close()
"
```

---

## Economist patterns

### Download a batch of PDFs by DOI

```bash
# dois.txt — one DOI per line
while IFS= read -r doi; do
    filename=$(echo "$doi" | tr '/' '_').pdf
    echo "Downloading: $doi → $filename"
    curl_yale -sfL "https://doi.org/${doi}" -o "${OUTPUT_DIR}/${filename}" || echo "FAILED: $doi"
    sleep 1  # be polite
done < dois.txt
```

### Scrape an HTML table to CSV (Python)

```bash
python3 -c "
import subprocess, sys
html = subprocess.check_output(['curl_chrome142', '-sf', sys.argv[1]]).decode()
import re
from html.parser import HTMLParser
# Simple: pipe through pandas
" URL

# OR: use pandas directly
python3 -c "
import pandas as pd
tables = pd.read_html('URL')
tables[0].to_csv('data.csv', index=False)
print(f'Found {len(tables)} tables, saved first as data.csv')
"

# For JS-rendered tables:
url-scrape -s 'table' https://example.com | python3 -c "
import json, sys
data = json.load(sys.stdin)
html = data['data'][0]['results'][0]['html']
import pandas as pd, io
df = pd.read_html(io.StringIO(html))[0]
df.to_csv('table.csv', index=False)
print(df.head())
"
```

### Scrape paginated data (static pagination)

```bash
# Loop over page numbers
for page in $(seq 1 20); do
    curl_chrome142 -sf "https://example.com/data?page=${page}" | htmlq '.result-item' --text >> results.txt
    sleep 0.5
done
```

### NBER working papers bulk download

```bash
# Get paper list for a topic, then download PDFs
curl_chrome142 -sf 'https://www.nber.org/search?q=labor+supply&searchType=Public' | \
  htmlq 'a[href*="/papers/"]' --attribute href | \
  sed 's|/papers/||' | \
  while read paper_id; do
    curl_chrome142 -sfL "https://www.nber.org/papers/${paper_id}.pdf" -o "nber_${paper_id}.pdf"
    sleep 1
  done
```

### SSRN download by paper ID

```bash
curl_chrome142 -sfL "https://papers.ssrn.com/sol3/Delivery.cfm/DELIVERY_ID?abstractid=PAPER_ID&type=2" -o paper.pdf
# If blocked: try curl_yale instead
```

---

## Output format guidance

**For analysis (Stata, R, Python):** Save scraped tables as CSV. Use `pandas.read_html()` for HTML tables, or parse JSON from `url-scrape` → CSV.

**For inspection first:** Save raw HTML/JSON, then extract. Good for debugging when you're unsure what's on the page.

**For bulk PDF datasets:** Organize as `author_year_keyword.pdf` or by DOI slug. Always log successes/failures to a text file when batch downloading.

**When choosing output format:**
- Data that looks like a table → CSV
- Metadata, structured records → JSON or CSV depending on complexity
- Full article text → plain text or Markdown

---

## Troubleshooting

**`curl_yale` hangs / times out** → SOCKS5 proxy not running. See [setup-yale.md](./references/setup-yale.md).

**Getting 403 / bot detection** → Try `curl_yale` (adds Yale IP + Chrome fingerprint). If still blocked, escalate to `url-scrape` / `url-content`.

**Content not in HTML (JS-rendered)** → Use `url-content` or `url-scrape`. Tip: compare `curl_chrome142 -sf URL | htmlq 'body' --text` vs. what you see in browser — if they differ, it's JS-rendered.

**`url-scrape` returns empty** → Add `-w 'SELECTOR' -t 5000` to wait longer for dynamic content.

**PDF is HTML (access denied page)** → `curl_yale` not routing through Yale IP. Check proxy. Run `curl_yale -sf https://httpbin.org/ip | jq .` to verify.

**Need help with setup** → See [setup-general.md](./references/setup-general.md) for curl-impersonate + htmlq/pup/jq install, and [setup-yale.md](./references/setup-yale.md) for the Yale proxy + browserless.

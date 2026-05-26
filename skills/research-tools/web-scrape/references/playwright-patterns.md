# Playwright Patterns (via browserless WebSocket)

Use Playwright when you need: login flows, clicking through pagination, filling forms, waiting for network requests, or any multi-step browser interaction.

## Connection setup (Python)

```python
import json, urllib.parse
from playwright.sync_api import sync_playwright

TOKEN = '$BROWSERLESS_TOKEN'
HOST = '$BROWSERLESS_HOST'
launch = urllib.parse.quote(json.dumps({
    'stealth': True,
    'args': ['--disable-blink-features=AutomationControlled']
}))
WS = f'wss://{HOST}/chromium/playwright?token={TOKEN}&launch={launch}'
```

## Pattern: scrape paginated table

```python
uv run --with playwright python3 << 'EOF'
import json, urllib.parse, csv
from playwright.sync_api import sync_playwright

TOKEN = '$BROWSERLESS_TOKEN'
HOST = '$BROWSERLESS_HOST'
launch = urllib.parse.quote(json.dumps({'stealth': True, 'args': ['--disable-blink-features=AutomationControlled']}))
ws = f'wss://{HOST}/chromium/playwright?token={TOKEN}&launch={launch}'

rows = []
with sync_playwright() as p:
    browser = p.chromium.connect(ws)
    page = browser.new_page()
    page.goto('https://example.com/data-table')

    while True:
        page.wait_for_selector('table tbody tr')
        # Extract rows
        page_rows = page.eval_on_selector_all('table tbody tr', '''
            rows => rows.map(r => Array.from(r.querySelectorAll('td')).map(td => td.innerText.trim()))
        ''')
        rows.extend(page_rows)

        # Click next page if exists
        next_btn = page.query_selector('a.next-page:not(.disabled)')
        if not next_btn:
            break
        next_btn.click()
        page.wait_for_load_state('networkidle')

    browser.close()

# Save to CSV
with open('data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)
print(f'Saved {len(rows)} rows to data.csv')
EOF
```

## Pattern: login then scrape

```python
uv run --with playwright python3 << 'EOF'
import json, urllib.parse
from playwright.sync_api import sync_playwright

TOKEN = '$BROWSERLESS_TOKEN'
HOST = '$BROWSERLESS_HOST'
launch = urllib.parse.quote(json.dumps({'stealth': True, 'args': ['--disable-blink-features=AutomationControlled']}))
ws = f'wss://{HOST}/chromium/playwright?token={TOKEN}&launch={launch}'

with sync_playwright() as p:
    browser = p.chromium.connect(ws)
    page = browser.new_page()

    # Login
    page.goto('https://example.com/login')
    page.fill('#username', 'your_username')
    page.fill('#password', 'your_password')
    page.click('button[type="submit"]')
    page.wait_for_url('**/dashboard**')

    # Now scrape authenticated content
    page.goto('https://example.com/restricted-data')
    page.wait_for_selector('.data-table')
    content = page.inner_text('.data-table')
    print(content)

    browser.close()
EOF
```

## Pattern: wait for API response, extract JSON

```python
uv run --with playwright python3 << 'EOF'
import json, urllib.parse
from playwright.sync_api import sync_playwright

TOKEN = '$BROWSERLESS_TOKEN'
HOST = '$BROWSERLESS_HOST'
launch = urllib.parse.quote(json.dumps({'stealth': True, 'args': ['--disable-blink-features=AutomationControlled']}))
ws = f'wss://{HOST}/chromium/playwright?token={TOKEN}&launch={launch}'

with sync_playwright() as p:
    browser = p.chromium.connect(ws)
    page = browser.new_page()

    # Intercept the API call the page makes
    api_data = []
    def handle_response(response):
        if '/api/data' in response.url and response.status == 200:
            api_data.append(response.json())

    page.on('response', handle_response)
    page.goto('https://example.com/chart-page')
    page.wait_for_load_state('networkidle')

    print(json.dumps(api_data, indent=2))
    browser.close()
EOF
```

## TypeScript alternative

```bash
npx -y tsx -e "
import { chromium } from 'playwright';

const launch = encodeURIComponent(JSON.stringify({stealth: true, args: ['--disable-blink-features=AutomationControlled']}));
const ws = \`wss://$BROWSERLESS_HOST/chromium/playwright?token=$BROWSERLESS_TOKEN&launch=\${launch}\`;

const browser = await chromium.connect(ws);
const page = await browser.newPage();
await page.goto('https://example.com');
console.log(await page.title());
await browser.close();
"
```

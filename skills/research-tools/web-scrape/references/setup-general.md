# General Setup: curl-impersonate + HTML/JSON tools

## curl-impersonate (curl_chrome142)

```bash
# macOS Apple Silicon (pin a release; "latest/download" filenames can change)
cd /tmp
curl -sfL -o curl-impersonate.tar.gz \
  https://github.com/lexiforest/curl-impersonate/releases/download/v1.5.2/curl-impersonate-v1.5.2.arm64-macos.tar.gz
tar xzf curl-impersonate.tar.gz
mkdir -p ~/.local/bin
cp curl-impersonate curl_* ~/.local/bin/
chmod +x ~/.local/bin/curl-impersonate ~/.local/bin/curl_*
rm -f curl-impersonate.tar.gz

# macOS Intel
# Use: curl-impersonate-v1.5.2.x86_64-macos.tar.gz

# Linux x86_64
# Use: curl-impersonate-v1.5.2.x86_64-linux-gnu.tar.gz
```

Add to PATH in `~/.zshrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Verify: `curl_chrome142 -sf https://httpbin.org/headers | jq .`

## HTML/JSON parsing tools

```bash
# Homebrew: jq + htmlq (pup is not a Homebrew formula on macOS as of 2026)
brew install jq htmlq

# pup (alternative HTML parser) — install Go once, then:
brew install go
GOBIN="$HOME/.local/bin" go install github.com/ericchiang/pup@latest

# Without Homebrew
# jq: https://github.com/jqlang/jq/releases/latest
curl -sfL -o ~/.local/bin/jq https://github.com/jqlang/jq/releases/latest/download/jq-macos-arm64
chmod +x ~/.local/bin/jq

# htmlq without Homebrew:
cargo install htmlq   # requires Rust
```

## Common htmlq patterns

```bash
# Extract text content
htmlq 'article' --text
htmlq 'p' --text

# Extract attribute
htmlq 'a' --attribute href
htmlq 'meta[name="citation_title"]' --attribute content

# Extract inner HTML
htmlq 'table'

# Multiple selectors (pipe separately)
htmlq 'h1' --text; htmlq 'p.abstract' --text
```

## Common jq patterns

```bash
# Pretty print
jq .

# Extract field
jq '.results[].title'

# Filter and format
jq '[.data[] | {id: .id, name: .name}]'

# To CSV (simple)
jq -r '.results[] | [.id, .title, .year] | @csv'
```

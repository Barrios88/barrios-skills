# Contributing

## Adding a skill

1. Create a folder under the appropriate category in `skills/`:
   ```
   skills/econometrics/my-new-skill/SKILL.md
   ```
2. Use YAML frontmatter with `name` and `description` (the description tells the agent when to trigger).
3. Run `bash scripts/audit-secrets.sh` — no real API keys or personal paths.
4. Update the catalog: `python3 scripts/sync-skills.py` is for syncing from local installs; for manual adds, edit `catalog/skills.json` or re-run the catalog generator.

## Requesting a skill

Open a GitHub issue describing the workflow (e.g. "audit working papers in LaTeX") and which tools you use (Stata, Python, etc.).

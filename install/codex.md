# Install skills in Codex

Codex discovers skills under `~/.codex/skills/`.

## Install

```bash
cp -R skills/documents/spreadsheets ~/.codex/skills/
cp -R skills/research-tools/openalex-api ~/.codex/skills/
```

Structure:

```
~/.codex/skills/
└── openalex-api/
    ├── SKILL.md
    └── scripts/
```

## Using the skill installer (optional)

Codex includes a built-in skill installer for curated skills from GitHub:

```
$skill-installer install the wrds skill from https://github.com/YOUR_USERNAME/barrios-skills/tree/main/skills/econometrics/wrds
```

## Verify

Ask Codex to perform a task described in the skill's frontmatter — e.g. "Query OpenAlex for papers on pass-through taxation."

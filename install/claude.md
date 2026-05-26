# Install skills in Claude Code

Claude Code reads skills from `~/.claude/skills/` (personal) or `.claude/skills/` (project).

## Personal install

```bash
cp -R skills/writing-and-review/econ-humanizer-plus ~/.claude/skills/
cp -R skills/econometrics/wrds ~/.claude/skills/
```

Each skill needs a folder with a `SKILL.md` file:

```
~/.claude/skills/
└── econ-humanizer-plus/
    └── SKILL.md
```

## Project install

```bash
mkdir -p .claude/skills
cp -R /path/to/barrios-skills/skills/research-tools/web-scrape .claude/skills/
```

## Verify

Start Claude Code in a project and ask a task that matches the skill description. Claude loads skills when the request triggers the skill's `description` field.

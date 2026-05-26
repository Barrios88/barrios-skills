# Install skills in Cursor

Cursor discovers skills from markdown files in skill folders.

## Personal skills (all projects)

Copy any skill folder into your personal skills directory:

```bash
# Example: install stata-regression
cp -R skills/econometrics/stata-regression ~/.cursor/skills/

# Example: install econ-humanizer-plus
cp -R skills/writing-and-review/econ-humanizer-plus ~/.cursor/skills/
```

Path: `~/.cursor/skills/<skill-name>/SKILL.md`

## Project skills (share with collaborators)

For a specific repo, copy into that project's `.cursor/skills/` folder instead:

```bash
mkdir -p /path/to/your/project/.cursor/skills
cp -R skills/econometrics/stata-regression /path/to/your/project/.cursor/skills/
```

## Verify

In Cursor Agent chat, ask something that matches the skill — e.g. "Run a DiD regression in Stata with firm fixed effects." Cursor should load the matching skill automatically based on its `description` in the frontmatter.

## More info

- [Cursor skills docs](https://cursor.com/docs)
- Do **not** copy skills into `~/.cursor/skills-cursor/` — that folder is managed by Cursor.

## WRDS data access

To query Compustat, CRSP, etc. through the agent, set up **[wrds-mcp](../install/wrds-mcp.md)** with **your own** WRDS username and password.

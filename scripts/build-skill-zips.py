#!/usr/bin/env python3
"""Build per-skill zip downloads for the GitHub Pages site."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG = REPO_ROOT / "catalog" / "skills.json"
OUT_DIR = REPO_ROOT / "docs" / "downloads" / "skills"


def zip_skill(skill_dir: Path, out_file: Path) -> None:
    folder_name = skill_dir.name
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(skill_dir.rglob("*")):
            if not path.is_file():
                continue
            arcname = Path(folder_name) / path.relative_to(skill_dir)
            zf.write(path, arcname.as_posix())


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    built = 0
    missing = []

    for skill in catalog["skills"]:
        skill_dir = REPO_ROOT / skill["path"]
        if not skill_dir.is_dir():
            missing.append(skill["id"])
            continue
        out_file = OUT_DIR / f"{skill['id']}.zip"
        zip_skill(skill_dir, out_file)
        built += 1

    if missing:
        raise SystemExit(f"Missing skill folders: {', '.join(missing)}")

    print(f"Built {built} skill zip(s) in {OUT_DIR.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

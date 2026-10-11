from __future__ import annotations

import json
import re
from pathlib import Path


BOOK_DIR = Path(__file__).resolve().parent
MANUSCRIPT_PATTERN = re.compile(r"^(\d{2})_.+\.md$")
EXCLUDED = {"全書正文_持續更新.md", "寫作進度.md"}


def count_text(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def main() -> None:
    files = []
    for path in BOOK_DIR.glob("*.md"):
        if path.name in EXCLUDED:
            continue
        match = MANUSCRIPT_PATTERN.match(path.name)
        if match and int(match.group(1)) >= 10:
            files.append((int(match.group(1)), path))
    files.sort(key=lambda item: (item[0], item[1].name))

    records = []
    sections = ["# 《陰陽相和：從〈黃帝內經〉讀懂養生之道》\n"]
    total = 0
    for _, path in files:
        text = path.read_text(encoding="utf-8").strip()
        chars = count_text(text)
        total += chars
        records.append({"file": path.name, "characters": chars})
        sections.append(text)

    (BOOK_DIR / "全書正文_持續更新.md").write_text(
        "\n\n---\n\n".join(sections) + "\n", encoding="utf-8"
    )
    progress = {
        "title": "陰陽相和：從《黃帝內經》讀懂養生之道",
        "target_characters": 200000,
        "current_characters": total,
        "completed_units": len(files),
        "records": records,
    }
    (BOOK_DIR / "字數紀錄.json").write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Updated {len(files)} units; {total:,} non-whitespace characters.")


if __name__ == "__main__":
    main()

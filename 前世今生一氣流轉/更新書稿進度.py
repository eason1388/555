from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "全書正文_持續更新.md"
RECORD = ROOT / "字數紀錄.json"


def count_characters(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def manuscript_files() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.glob("[0-9][0-9]_*.md"))
        if int(path.name[:2]) >= 10
    ]


def main() -> None:
    records: list[dict[str, object]] = []
    sections: list[str] = ["# 《前世今生：一氣流轉的生命之書》\n"]
    for path in manuscript_files():
        text = path.read_text(encoding="utf-8").strip()
        records.append({"file": path.name, "characters": count_characters(text)})
        sections.append(text)

    total = sum(int(record["characters"]) for record in records)
    OUTPUT.write_text("\n\n---\n\n".join(sections) + "\n", encoding="utf-8")
    RECORD.write_text(
        json.dumps(
            {
                "title": "前世今生：一氣流轉的生命之書",
                "target_characters": 200000,
                "current_characters": total,
                "completed_units": len(records),
                "records": records,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Updated {len(records)} units; {total:,} non-whitespace characters.")


if __name__ == "__main__":
    main()


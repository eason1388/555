from __future__ import annotations

import html
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BOOKS = [
    {
        "name": "天眼風水師",
        "page": "https://fanqienovel.com/page/7326876174989134910",
        "directory": ROOT / "天眼風水師導讀",
        "expected": 992,
    },
    {
        "name": "畫眼睛",
        "page": "https://fanqienovel.com/page/7513623524011936793",
        "directory": ROOT / "畫眼睛導讀",
        "expected": 256,
    },
    {
        "name": "修仙封神榜",
        "page": "https://fanqienovel.com/page/7417422869342211097",
        "directory": ROOT / "修仙封神榜導讀",
        "expected": 555,
    },
]


def fetch(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; reading-guide-catalog/1.0)",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.7",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def chapters_from_page(source: str, expected: int) -> list[tuple[str, str]]:
    matches = re.findall(
        r'<a[^>]+href="(?:https://fanqienovel\.com)?/reader/(\d+)"[^>]*>(.*?)</a>',
        source,
        flags=re.DOTALL,
    )
    candidates: list[tuple[str, str]] = []
    for item_id, label_html in matches:
        label = html.unescape(re.sub(r"<[^>]+>", "", label_html))
        label = re.sub(r"\s+", " ", label).strip()
        candidates.append((item_id, label))

    first_chapter = next(
        (
            index
            for index, (_, label) in enumerate(candidates)
            if re.match(r"^第\s*1\s*章(?:\s|$)", label)
        ),
        None,
    )
    if first_chapter is None:
        return []
    chapters: list[tuple[str, str]] = []
    seen: set[str] = set()
    for item_id, label in candidates[first_chapter:]:
        if item_id in seen:
            continue
        seen.add(item_id)
        chapters.append((item_id, label))
        if len(chapters) == expected:
            break
    return chapters


def write_catalog(book: dict[str, object], chapters: list[tuple[str, str]]) -> None:
    directory = Path(book["directory"])
    directory.mkdir(exist_ok=True)
    for old in directory.glob("4[0-9]_官方完整章目_*.md"):
        old.unlink()

    for batch_index, start in enumerate(range(0, len(chapters), 100)):
        end = min(start + 100, len(chapters))
        filename = directory / f"{40 + batch_index:02d}_官方完整章目_{start + 1}至{end}章.md"
        lines = [
            f"# 《{book['name']}》官方完整章目　第{start + 1}至{end}章",
            "",
            f"以下每一章都連往[官方作品頁]({book['page']})的正版閱讀內容。本站只提供導讀與索引，不轉載正文。",
            "",
        ]
        for item_id, label in chapters[start:end]:
            lines.append(f"- [{label}](https://fanqienovel.com/reader/{item_id})")
        lines.append("")
        filename.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    for book in BOOKS:
        expected = int(book["expected"])
        chapters = chapters_from_page(fetch(str(book["page"])), expected)
        if len(chapters) != expected:
            raise RuntimeError(
                f"{book['name']}: expected {expected} chapters, found {len(chapters)}"
            )
        write_catalog(book, chapters)
        print(f"{book['name']}: wrote {len(chapters)} official chapter links")


if __name__ == "__main__":
    main()

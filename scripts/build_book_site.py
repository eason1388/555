from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "修道與濟世"
OUTPUT_DIR = ROOT / "docs"


GROUPS = [
    (0, 0, "導論"),
    (1, 6, "第一篇　道法之本"),
    (7, 12, "第二篇　經典中的修道骨架"),
    (13, 18, "第三篇　氣與神"),
    (19, 24, "第四篇　靜坐與內丹"),
    (25, 30, "第五篇　九竅與關竅"),
    (31, 36, "第六篇　符籙、咒訣與科儀"),
    (37, 42, "第七篇　清、調、安"),
    (43, 48, "第八篇　禳解、補益與護持"),
    (49, 54, "第九篇　家宅、幽冥與超拔"),
    (55, 60, "第十篇　改命與濟世"),
    (61, 66, "附錄"),
    (67, 67, "後記"),
]


def group_for(index: int) -> str:
    for start, end, label in GROUPS:
        if start <= index <= end:
            return label
    return "其他"


def inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return escaped


def markdown_to_html(markdown: str) -> tuple[str, list[dict[str, str]]]:
    lines = markdown.replace("\r\n", "\n").split("\n")
    output: list[str] = []
    toc: list[dict[str, str]] = []
    paragraph: list[str] = []
    list_type: str | None = None
    in_code = False
    code_lines: list[str] = []
    heading_count = 0

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{inline(' '.join(part.strip() for part in paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = None

    for line in lines:
        if line.startswith("```"):
            flush_paragraph()
            close_list()
            if in_code:
                output.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            label = heading.group(2).strip()
            heading_count += 1
            anchor = f"section-{heading_count}"
            output.append(f'<h{level} id="{anchor}">{inline(label)}</h{level}>')
            if level == 2:
                toc.append({"id": anchor, "label": label})
            continue

        if re.match(r"^\s*([-*_])\1\1+\s*$", line):
            flush_paragraph()
            close_list()
            output.append("<hr>")
            continue

        unordered = re.match(r"^\s*[-*]\s+(.+)$", line)
        ordered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if unordered or ordered:
            flush_paragraph()
            desired = "ul" if unordered else "ol"
            if list_type != desired:
                close_list()
                output.append(f"<{desired}>")
                list_type = desired
            match = unordered or ordered
            output.append(f"<li>{inline(match.group(1))}</li>")
            continue

        quote = re.match(r"^>\s?(.*)$", line)
        if quote:
            flush_paragraph()
            close_list()
            output.append(f"<blockquote>{inline(quote.group(1))}</blockquote>")
            continue

        if not line.strip():
            flush_paragraph()
            close_list()
            continue

        paragraph.append(line)

    flush_paragraph()
    close_list()
    if in_code:
        output.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    return "\n".join(output), toc


def build() -> None:
    chapter_files = sorted(BOOK_DIR.glob("[0-9][0-9]_*.md"))
    chapters: list[dict[str, object]] = []

    for path in chapter_files:
        index = int(path.name[:2])
        markdown = path.read_text(encoding="utf-8")
        first_heading = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
        title = first_heading.group(1).strip() if first_heading else path.stem[3:]
        rendered, toc = markdown_to_html(markdown)
        search_text = re.sub(r"[#*_>`\[\]()]+", " ", markdown)
        search_text = re.sub(r"\s+", " ", search_text).strip()
        chapters.append(
            {
                "id": f"{index:02d}",
                "index": index,
                "title": title,
                "group": group_for(index),
                "html": rendered,
                "toc": toc,
                "searchText": search_text,
                "characters": len(re.sub(r"\s+", "", markdown)),
            }
        )

    payload = {
        "title": "修道與濟世",
        "motto": "道為本，德為承，氣為行，神為主，法為用，濟世為驗。",
        "chapterCount": len(chapters),
        "characters": sum(int(chapter["characters"]) for chapter in chapters),
        "chapters": chapters,
    }
    OUTPUT_DIR.mkdir(exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    (OUTPUT_DIR / "book-data.js").write_text(
        f"window.BOOK_DATA={serialized};\n", encoding="utf-8"
    )
    (OUTPUT_DIR / ".nojekyll").touch()
    print(
        f"Built {payload['chapterCount']} chapters, "
        f"{payload['characters']:,} non-whitespace characters."
    )


if __name__ == "__main__":
    build()

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs"


XIUDAO_GROUPS = [
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

YINYANG_GROUPS = [
    (10, 10, "導論"),
    (11, 16, "第一篇　一陰一陽之謂生"),
    (17, 22, "第二篇　四時陰陽"),
    (23, 28, "第三篇　人身陰陽"),
    (29, 36, "第四篇　日用陰陽"),
    (37, 44, "第五篇　男女陰陽"),
    (45, 52, "第六篇　陰陽之偏"),
    (53, 60, "第七篇　一生陰陽"),
    (61, 64, "附錄"),
    (65, 65, "後記"),
]

QINGSONG_GROUPS = [
    (10, 10, "導讀"),
    (11, 16, "第一篇　這部古書到底在說什麼"),
    (17, 24, "第二篇　古人畫下的身體地圖"),
    (25, 30, "第三篇　醫者怎樣讀懂一個人"),
    (31, 37, "第四篇　病是怎樣一步一步形成的"),
    (38, 44, "第五篇　《內經》怎樣談治療"),
    (45, 51, "第六篇　把《內經》放回日常生活"),
    (52, 57, "第七篇　從出生到老去"),
    (58, 60, "第八篇　今天怎樣讀《黃帝內經》"),
    (61, 64, "附錄"),
    (70, 70, "後記"),
]

LIFE_GROUPS = [
    (10, 10, "導讀"),
    (11, 16, "第一篇　先讀懂自己的日常"),
    (17, 22, "第二篇　起居有常，從早晨到夜晚"),
    (23, 29, "第三篇　飲食有節，讓每一餐接得起來"),
    (30, 36, "第四篇　動靜相養，讓身體保持可用"),
    (37, 44, "第五篇　情志與關係"),
    (45, 51, "第六篇　四季與環境"),
    (52, 57, "第七篇　生命階段，各有各的養法"),
    (58, 60, "第八篇　做出自己的生活養生法"),
    (61, 65, "附錄"),
    (70, 70, "後記"),
]

BOOKS = [
    {
        "slug": "xiudao",
        "directory": ROOT / "修道與濟世",
        "title": "修道與濟世",
        "mark": "道",
        "motto": "道為本，德為承，氣為行，神為主，法為用，濟世為驗。",
        "intro": "從修道的根基出發，經由德、氣、神而進入符籙、科儀與濟世之用。章節不是各自分離的知識，而是一條由內在修持走向人間實踐的路。",
        "theme_count": 10,
        "groups": XIUDAO_GROUPS,
        "start": 0,
        "end": 67,
    },
    {
        "slug": "yinyang",
        "directory": ROOT / "黃帝內經養生書",
        "title": "陰陽相和",
        "subtitle": "從《黃帝內經》讀懂養生之道",
        "mark": "和",
        "motto": "養生，就是使陰陽隨時而和。",
        "intro": "從四時晝夜、起居飲食，到男女相感、伴侶相養與一生的變化，循《黃帝內經》的陰陽之道，讀懂身體如何在日常裡復和。",
        "theme_count": 7,
        "groups": YINYANG_GROUPS,
        "start": 10,
        "end": 65,
    },
    {
        "slug": "qingsong",
        "directory": ROOT / "黃帝內經輕鬆談",
        "title": "黃帝內經輕鬆談",
        "mark": "經",
        "motto": "看一個完整的人，如何隨天地、時間與生活而變化。",
        "intro": "從成書、身體觀、藏府經絡與四診，談到病因、治療、日常生活與生命階段，用平常語氣讀懂《黃帝內經》的完整世界。",
        "theme_count": 8,
        "groups": QINGSONG_GROUPS,
        "start": 10,
        "end": 70,
    },
    {
        "slug": "life",
        "directory": ROOT / "黃帝內經實用生活篇",
        "title": "黃帝內經實用生活篇",
        "mark": "養",
        "motto": "每天的節律，決定身體能否用得出去、收得回來、再補得上。",
        "intro": "把《黃帝內經》的整體眼光放進作息、飲食、活動、情緒、關係與四季，在真實日子裡建立能長久維持的生活節律。",
        "theme_count": 8,
        "groups": LIFE_GROUPS,
        "start": 10,
        "end": 70,
    },
]


def group_for(groups: list[tuple[int, int, str]], index: int) -> str:
    for start, end, label in groups:
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


def build_book(config: dict[str, object]) -> dict[str, object]:
    book_dir = Path(config["directory"])
    start = int(config["start"])
    end = int(config["end"])
    chapter_files = [
        path
        for path in sorted(book_dir.glob("[0-9][0-9]_*.md"))
        if start <= int(path.name[:2]) <= end
    ]
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
                "group": group_for(config["groups"], index),
                "html": rendered,
                "toc": toc,
                "searchText": search_text,
                "characters": len(re.sub(r"\s+", "", markdown)),
            }
        )

    return {
        "slug": config["slug"],
        "title": config["title"],
        "subtitle": config.get("subtitle", "線上全文"),
        "mark": config["mark"],
        "motto": config["motto"],
        "intro": config["intro"],
        "themeCount": config["theme_count"],
        "chapterCount": len(chapters),
        "characters": sum(int(chapter["characters"]) for chapter in chapters),
        "chapters": chapters,
    }


def build() -> None:
    books = {str(config["slug"]): build_book(config) for config in BOOKS}
    payload = {"defaultBook": "yinyang", "books": books}
    OUTPUT_DIR.mkdir(exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    (OUTPUT_DIR / "book-data.js").write_text(
        f"window.BOOK_LIBRARY={serialized};\n", encoding="utf-8"
    )
    (OUTPUT_DIR / ".nojekyll").touch()
    for book in books.values():
        print(
            f"Built {book['title']}: {book['chapterCount']} units, "
            f"{book['characters']:,} non-whitespace characters."
        )


if __name__ == "__main__":
    build()

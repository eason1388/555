from pathlib import Path
import json
import re
import unicodedata

ROOT = Path(__file__).resolve().parent


def count_body(text):
    body = text.split("\n---\n", 1)[0]
    body = "\n".join(line for line in body.splitlines() if not line.startswith("#"))
    body = re.sub(r"\[\d+\]", "", body)
    return sum(
        not char.isspace() and unicodedata.category(char)[0] in "LN"
        for char in body
    )


def main():
    rows = []
    for path in sorted(ROOT.glob("[0-9][0-9]_*.md")):
        text = path.read_text(encoding="utf-8")
        rows.append({"file": path.name, "title": text.splitlines()[0].lstrip("# "), "words": count_body(text)})
    total = sum(row["words"] for row in rows)
    outline = (ROOT / "全書章節規劃.md").read_text(encoding="utf-8")
    chapter_titles = {int(n): title for n, title in re.findall(r"\*\*第 (\d+) 章　([^\n*]+)\*\*", outline)}
    completed = [int(row["file"][:2]) for row in rows if int(row["file"][:2]) > 0]
    next_number = next((n for n in range(1, 61) if n not in completed), None)
    next_step = (
        f"下一個交付單位：第 {next_number} 章〈{chapter_titles[next_number]}〉。"
        if next_number else "正文六十章均已有稿件；接續附錄、後記與全書統稿。"
    )
    lines = [
        "# 書稿進度", "", "狀態：逐章完成正文初稿；全書持續寫作中。", "",
        "計算規則：計入正文 Unicode 字母與數字；不計空白、標點、章節標題、注釋標號及篇末注釋。",
        "此規則以字元計算，不以中文斷詞計算。", "",
        "| 文件 | 正文字數 |", "|---|---:|",
    ]
    lines += [f"| [{row['title']}]({row['file']}) | {row['words']:,} |" for row in rows]
    lines += ["", f"累計正文：**{total:,} 字**。", f"全書目標：300,000 字；尚差 {300000 - total:,} 字。", "",
              next_step, "",
              "目前稿件為正文初稿，尚未經作者確認個人立場；未寫入虛構師承或親身案例。",
              "已完成引句的網路文本對照；正式出版底本、頁碼與全書統稿仍待後續處理。", ""]
    (ROOT / "書稿進度.md").write_text("\n".join(lines), encoding="utf-8")
    (ROOT / "字數紀錄.json").write_text(json.dumps({"chapters": rows, "total": total, "target": 300000}, ensure_ascii=False, indent=2), encoding="utf-8")
    collected = ["# 修道與濟世：隨緣堂道教義理、養氣與科儀研究", "", "持續更新正文初稿｜尚未完成全書統稿", ""]
    for row in rows:
        collected += [(ROOT / row["file"]).read_text(encoding="utf-8"), "\n\n"]
    (ROOT / "全書正文_持續更新.md").write_text("\n".join(collected), encoding="utf-8")
    print(json.dumps({"chapters": rows, "total": total}, ensure_ascii=False))


if __name__ == "__main__":
    main()

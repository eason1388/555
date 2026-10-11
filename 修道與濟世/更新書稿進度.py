from pathlib import Path
import json
import re
import sys
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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rows = []
    for path in sorted(ROOT.glob("[0-9][0-9]_*.md")):
        text = path.read_text(encoding="utf-8")
        rows.append({"file": path.name, "title": text.splitlines()[0].lstrip("# "), "words": count_body(text)})
    total = sum(row["words"] for row in rows)
    outline = (ROOT / "全書章節規劃.md").read_text(encoding="utf-8")
    chapter_titles = {int(n): title for n, title in re.findall(r"\*\*第 (\d+) 章　([^\n*]+)\*\*", outline)}
    completed = [int(row["file"][:2]) for row in rows if int(row["file"][:2]) > 0]
    next_number = next((n for n in range(1, 61) if n not in completed), None)
    completed_units = {int(row["file"][:2]) for row in rows}
    if next_number:
        next_step = f"下一個交付單位：第 {next_number} 章〈{chapter_titles[next_number]}〉。"
    elif not all(n in completed_units for n in range(61, 67)):
        next_appendix = next(n for n in range(61, 67) if n not in completed_units)
        next_step = f"下一個交付單位：附錄 {next_appendix - 60}。"
    elif 67 not in completed_units:
        next_step = "下一個交付單位：後記。"
    else:
        next_step = "六十章、六項附錄與後記均已有初稿；接續全書統稿、補足字數與總檢。"
    lines = [
        "# 書稿進度", "", "狀態：六十章、六項附錄與後記均已有初稿；全書統稿中。", "",
        "計算規則：計入各書稿單元 Unicode 字母與數字；不計空白、標點、章節標題、注釋標號及篇末注釋。",
        "此規則以字元計算，不以中文斷詞計算。", "",
        "| 文件 | 本文計數 |", "|---|---:|",
    ]
    lines += [f"| [{row['title']}]({row['file']}) | {row['words']:,} |" for row in rows]
    lines += ["", f"全稿累計：**{total:,} 字**。", f"全書目標：300,000 字；尚差 {max(0, 300000 - total):,} 字。", "",
              next_step, "",
              "目前稿件為正文初稿，尚未經作者確認個人立場；未寫入虛構師承或親身案例。",
              "已完成引句的網路文本對照；正式出版底本、頁碼與全書統稿仍待後續處理。", ""]
    (ROOT / "書稿進度.md").write_text("\n".join(lines), encoding="utf-8")
    (ROOT / "字數紀錄.json").write_text(json.dumps({"chapters": rows, "total": total, "target": 300000}, ensure_ascii=False, indent=2), encoding="utf-8")
    collected = ["# 《修道與濟世》", "", "持續更新正文初稿｜尚未完成全書統稿", ""]
    for row in rows:
        collected += [(ROOT / row["file"]).read_text(encoding="utf-8"), "\n\n"]
    (ROOT / "全書正文_持續更新.md").write_text("\n".join(collected), encoding="utf-8")
    print(json.dumps({"chapters": rows, "total": total}, ensure_ascii=False))


if __name__ == "__main__":
    main()

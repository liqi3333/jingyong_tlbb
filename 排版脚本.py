#!/usr/bin/env python3
"""天龙八部简介 → 精美排版 HTML + DOCX"""

import re
import subprocess
import textwrap
from pathlib import Path

md = Path("天龙八部简介.md").read_text(encoding="utf-8")
html_path = Path("天龙八部简介-排版版.html")
docx_path = Path("天龙八部简介-排版版.docx")


def md2html(md_text):
    lines = md_text.split("\n")
    out, buf, i, n = [], [], 0, len(lines)

    def inline(s):
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
        s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        return s

    def flush():
        if buf:
            p = inline(" ".join(x.strip() for x in buf if x.strip()))
            if p:
                out.append(f"<p>{p}</p>")
            buf.clear()

    while i < n:
        s = lines[i].strip()
        if not s:
            flush()
            i += 1
            continue
        if s.startswith("#"):
            flush()
            level = len(s.split()[0])
            out.append(f"<h{level}>{inline(s[level:].strip())}</h{level}>")
            i += 1
            continue
        if s == "---":
            flush()
            out.append("<hr>")
            i += 1
            continue
        if s.startswith(("- ", "* ")):
            flush()
            items = []
            while i < n and lines[i].strip().startswith(("- ", "* ")):
                items.append(f"<li>{inline(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("<ul>\n" + "\n".join(items) + "\n</ul>")
            continue
        if s.startswith(">"):
            flush()
            ql = []
            while i < n and lines[i].strip().startswith(">"):
                ql.append(inline(lines[i].strip()[1:].strip()))
                i += 1
            out.append(f"<blockquote>{' '.join(ql)}</blockquote>")
            continue
        buf.append(lines[i])
        i += 1
    flush()
    return "\n".join(out)


body = md2html(md)

CSS = textwrap.dedent("""\
body { font-family: "STSong","SimSun","Songti SC",serif; font-size: 12pt; line-height: 2.0; max-width: 780px; margin: 0 auto; padding: 40px 30px; color: #1a1a1a; }
h1 { font-size: 22pt; text-align: center; letter-spacing: 4pt; color: #8b0000; margin: 50pt 0 20pt; border-bottom: 2px solid #8b0000; padding-bottom: 10pt; }
h2 { font-size: 18pt; color: #8b0000; margin: 35pt 0 16pt; border-left: 5px solid #8b0000; padding-left: 12pt; }
h3 { font-size: 15pt; color: #333; margin: 25pt 0 12pt; padding-left: 10pt; border-left: 3px solid #e67e22; }
p { text-indent: 2em; margin: 8pt 0; }
blockquote { margin: 15pt 0; padding: 12pt 18pt; background: #f9f5f0; border-left: 4px solid #8b0000; }
blockquote p { text-indent: 0; }
hr { border: none; border-top: 2px solid #d4c5b0; margin: 30pt 0; }
ul { margin: 8pt 0 8pt 2em; }
li { margin: 4pt 0; }
strong { color: #8b0000; }
code { background: #f0ece6; padding: 2px 6px; border-radius: 3px; font-family: Menlo, monospace; }
@media print { body { padding: 20pt; } }
""")

full = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>《天龙八部》全本纪事</title>
<style>{CSS}</style></head>
<body>
<div style="text-align:center;padding:100pt 0 60pt;page-break-after:always">
<div style="font-size:42pt;letter-spacing:12pt;color:#8b0000;margin-bottom:10pt">天龙八部</div>
<div style="width:80px;height:3px;background:#8b0000;margin:20pt auto"></div>
<div style="font-size:20pt;letter-spacing:6pt;color:#555;margin-bottom:30pt">全本纪事</div>
<div style="font-size:12pt;color:#999;margin-top:60pt;line-height:2">无人不冤 · 有情皆孽<br>—— 金庸 原著 · 全景导读 ——</div>
</div>
{body}
<div style="text-align:center;margin:50pt 0;color:#8b0000;font-size:11pt">
◇ ◆ ◇<br>—— 全文完 ——
</div>
</body></html>"""

html_path.write_text(full, encoding="utf-8")
print(f"✅ HTML: {html_path}")

subprocess.run(
    ["textutil", "-convert", "docx", str(html_path), "-output", str(docx_path)]
)
print(f"✅ DOCX: {docx_path}")

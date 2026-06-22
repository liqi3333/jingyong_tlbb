#!/usr/bin/env python3
"""将 50 篇天龙八部深度解析 MD 文件批量转换为排版精美的 HTML"""

import json
import re
from pathlib import Path

PROJECT = Path(__file__).parent

# 查找所有深度解析 MD 文件
md_files = sorted(PROJECT.glob("天龙八部-*-深度解析.md"))


def parse_sort_key(path):
    """从文件名提取数字，用于排序"""
    name = path.stem
    # 匹配 "第X章" 或 "第X十X回"
    m = re.search(r"第([一二三四五六七八九十百零]+)(章|回)", name)
    if not m:
        return 999
    num_str = m.group(1)
    unit = m.group(2)
    # 中文数字转阿拉伯数字
    CHN = {
        "零": 0,
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
        "十": 10,
        "百": 100,
    }

    def c2a(s):
        if "百" in s:
            parts = s.split("百")
            return c2a(parts[0]) * 100 + (c2a(parts[1]) if parts[1] else 0)
        if "十" in s:
            parts = s.split("十")
            left = c2a(parts[0]) if parts[0] else 1
            return left * 10 + (c2a(parts[1]) if parts[1] else 0)
        # 个位数
        return sum(CHN.get(c, 0) for c in s)

    return c2a(num_str)


md_files.sort(key=parse_sort_key)

CSS = """\
body { font-family: "STSong","SimSun","Songti SC","Noto Serif SC",serif; font-size: 12pt; line-height: 2.0; max-width: 780px; margin: 0 auto; padding: 40px 30px; color: #1a1a1a; -webkit-font-smoothing: antialiased; }
h1 { font-size: 22pt; text-align: center; letter-spacing: 4pt; color: #8b0000; margin: 50pt 0 20pt; border-bottom: 2px solid #8b0000; padding-bottom: 10pt; }
h2 { font-size: 18pt; color: #8b0000; margin: 35pt 0 16pt; border-left: 5px solid #8b0000; padding-left: 12pt; }
h3 { font-size: 15pt; color: #333; margin: 25pt 0 12pt; padding-left: 10pt; border-left: 3px solid #e67e22; }
h4 { font-size: 13pt; color: #555; margin: 20pt 0 10pt; padding-left: 10pt; border-left: 3px solid #c49a6c; }
p { text-indent: 2em; margin: 8pt 0; }
blockquote { margin: 15pt 0; padding: 12pt 18pt; background: #f9f5f0; border-left: 4px solid #8b0000; }
blockquote p { text-indent: 0; }
hr { border: none; border-top: 2px solid #d4c5b0; margin: 30pt 0; }
ul, ol { margin: 8pt 0 8pt 2em; }
li { margin: 4pt 0; }
strong { color: #8b0000; }
code { background: #f0ece6; padding: 2px 6px; border-radius: 3px; font-family: Menlo, monospace; font-size: 0.9em; }
table { width: 100%; border-collapse: collapse; margin: 20pt 0; font-size: 11pt; }
th, td { border: 1px solid #d4c5b0; padding: 8pt 12pt; text-align: left; }
th { background: #8b0000; color: #fff; font-weight: normal; letter-spacing: 2px; }
td { background: #faf8f5; }
tr:nth-child(even) td { background: #f5f0ea; }
a { color: #8b0000; text-decoration: none; }
a:hover { text-decoration: underline; }
@media print { body { padding: 20pt; } }
"""


def inline(text):
    """处理行内标记：粗体、斜体、代码"""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


def md2html(md_text):
    """将简单 markdown 转换为 HTML"""
    lines = md_text.split("\n")
    out = []
    buf = []
    i, n = 0, len(lines)

    def flush():
        nonlocal buf
        if buf:
            text = inline("".join(buf))
            if text.strip():
                out.append(f"<p>{text}</p>")
            buf = []

    while i < n:
        s = lines[i].rstrip()
        stripped = s.strip()

        # 空行
        if not stripped:
            flush()
            i += 1
            continue

        # 标题
        if (
            stripped.startswith("## ")
            or stripped.startswith("### ")
            or stripped.startswith("#### ")
        ):
            flush()
            level = len(stripped.split()[0])
            title = inline(stripped[level:].strip())
            out.append(f"<h{level}>{title}</h{level}>")
            i += 1
            continue

        # 一级标题（# 开头）
        if stripped.startswith("# ") and not stripped.startswith("## "):
            flush()
            title = inline(stripped[2:].strip())
            out.append(f"<h1>{title}</h1>")
            i += 1
            continue

        # 分割线
        if stripped == "---":
            flush()
            out.append("<hr>")
            i += 1
            continue

        # 无序列表
        if stripped.startswith("- ") or stripped.startswith("* "):
            flush()
            items = []
            while i < n and lines[i].rstrip().strip().startswith(("- ", "* ")):
                items.append(f"<li>{inline(lines[i].rstrip().strip()[2:])}</li>")
                i += 1
            out.append(f"<ul>{''.join(items)}</ul>")
            continue

        # 有序列表
        if re.match(r"^\d+[\.\、]\s", stripped):
            flush()
            items = []
            while i < n and re.match(r"^\d+[\.\、]\s", lines[i].rstrip().strip()):
                content = re.sub(r"^\d+[\.\、]\s", "", lines[i].rstrip().strip())
                items.append(f"<li>{inline(content)}</li>")
                i += 1
            out.append(f"<ol>{''.join(items)}</ol>")
            continue

        # 引用
        if stripped.startswith(">"):
            flush()
            qlines = []
            while i < n and lines[i].rstrip().strip().startswith(">"):
                qlines.append(inline(lines[i].rstrip().strip()[1:].strip()))
                i += 1
            out.append(f"<blockquote>{''.join(qlines)}</blockquote>")
            continue

        # 表格行
        if "|" in stripped and lines[i].count("|") >= 3:
            flush()
            table_rows = []
            header_done = False
            while i < n and lines[i].rstrip().strip().startswith("|"):
                row = lines[i].rstrip().strip()
                # 跳过分隔行 (---|---|---)
                if re.match(r"^\|[\s\-:]+\|", row):
                    i += 1
                    continue
                cells = [inline(c.strip()) for c in row.split("|")[1:-1]]
                tag = "th" if not header_done else "td"
                table_rows.append(
                    f"<tr><{tag}>" + f"</{tag}><{tag}>".join(cells) + f"</{tag}></tr>"
                )
                if not header_done:
                    header_done = True
                i += 1
            if table_rows:
                out.append(f"<table>{''.join(table_rows)}</table>")
            continue

        # 普通段落行
        buf.append(lines[i])
        i += 1

    flush()
    return "\n".join(out)


def build_chapter_nav(current_sort_key, all_files_with_keys):
    """构建上一篇/下一篇导航"""
    prev_link = ""
    next_link = ""
    for idx, (fpath, skey) in enumerate(all_files_with_keys):
        if skey == current_sort_key:
            if idx > 0:
                prev_path = all_files_with_keys[idx - 1][0]
                prev_name = prev_path.stem.replace("-深度解析", "").replace(
                    "天龙八部-", ""
                )
                prev_link = f'<a href="{prev_path.with_suffix(".html").name}" class="nav-prev">← {prev_name}</a>'
            if idx < len(all_files_keys) - 1:
                next_path = all_files_keys[idx + 1][0]
                next_name = next_path.stem.replace("-深度解析", "").replace(
                    "天龙八部-", ""
                )
                next_link = f'<a href="{next_path.with_suffix(".html").name}" class="nav-next">{next_name} →</a>'
            break
    return prev_link, next_link


# 预计算所有文件的排序键
all_files_keys = [(f, parse_sort_key(f)) for f in md_files]

# 逐个转换
success = 0
for md_path in md_files:
    md_text = md_path.read_text(encoding="utf-8")
    html_body = md2html(md_text)

    # 提取标题
    title_match = re.search(r"<h1>(.+?)</h1>", html_body)
    page_title = title_match.group(1) if title_match else md_path.stem

    sort_key = parse_sort_key(md_path)
    prev_link, next_link = build_chapter_nav(sort_key, all_files_keys)

    # 计算回目编号标签
    label = ""
    stem = md_path.stem
    m = re.search(r"(第[^\-]+)", stem)
    if m:
        label = m.group(1)

    # 前/后导航 HTML
    nav_html = ""
    if prev_link or next_link:
        nav_html = f"""
    <div class="chapter-nav">
      {prev_link}
      <a href="深度解析目录.html" class="nav-index">📖 目录</a>
      {next_link}
    </div>"""

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title} — 天龙八部深度解析</title>
<style>{CSS}
.chapter-nav {{
  display: flex; justify-content: space-between; align-items: center;
  margin: 20pt 0 10pt; padding: 12pt 0; border-bottom: 1px solid #e0d6c8;
  font-size: 12pt;
}}
.chapter-nav a {{
  color: #8b0000; text-decoration: none; letter-spacing: 1px;
  padding: 4px 12px; border: 1px solid #e0d6c8; border-radius: 4px;
  transition: all 0.2s;
}}
.chapter-nav a:hover {{
  background: #8b0000; color: #fff; border-color: #8b0000;
}}
.chapter-nav .nav-index {{
  border: none; color: #888; font-size: 11pt;
}}
.chapter-nav .nav-index:hover {{
  background: transparent; color: #8b0000;
}}
</style>
</head>
<body>
{nav_html}
{html_body}
{nav_html}
<div style="text-align:center;margin:40pt 0 20pt;color:#aaa;font-size:10pt;letter-spacing:2px">
— 金庸 · 《天龙八部》深度解析 · {label} —
</div>
<div style="text-align:center;margin:10pt 0 30pt">
<a href="深度解析目录.html" style="color:#8b0000;font-size:11pt;letter-spacing:2px">← 返回目录</a>
&nbsp;·&nbsp;
<a href="index.html" style="color:#8b0000;font-size:11pt;letter-spacing:2px">返回主页</a>
</div>
</body>
</html>"""

    html_path = md_path.with_suffix(".html")
    html_path.write_text(full_html, encoding="utf-8")
    print(f"  ✅ {html_path.name}")
    success += 1

print(f"\n共转换 {success} 篇深度解析为 HTML")

# ===== 生成目录页 =====
print("正在生成深度解析目录...")

index_items = []
for fpath, skey in all_files_keys:
    stem = fpath.stem
    label = stem.replace("天龙八部-", "").replace("-深度解析", "")
    # 提取简短的章节描述
    h1_match = re.search(r"<h1>(.+?)</h1>", md2html(fpath.read_text(encoding="utf-8")))
    desc = h1_match.group(1) if h1_match else label
    # 截断过长的标题
    if len(desc) > 50:
        desc = desc[:48] + "…"

    # 分类（第一章～第十章 / 第十一回～第五十回）
    if "章" in label:
        cls = "章"
    else:
        cls = "回"

    index_items.append((skey, label, desc, fpath.name.replace(".md", ".html"), cls))

# 生成目录 HTML
index_html_items = []
current_group = None
for skey, label, desc, href, cls in index_items:
    group_label = "章" if cls == "章" else "回"
    if group_label != current_group:
        if current_group is not None:
            index_html_items.append("    </div>\n  </div>\n")
        current_group = group_label
        group_title = "第一章～第十章" if group_label == "章" else "第十一回～第五十回"
        index_html_items.append(f"""
  <div class="group-section">
    <h2 class="group-title">{group_title}</h2>
    <div class="chapter-list">""")
    index_html_items.append(f"""
      <a href="{href}" class="chapter-item">
        <span class="ch-label">{label}</span>
        <span class="ch-desc">{desc}</span>
        <span class="ch-arrow">→</span>
      </a>""")

if index_html_items:
    index_html_items.append("    </div>\n  </div>\n")

index_css = (
    CSS
    + """
.group-section { margin: 30pt 0; }
.group-title { font-size: 16pt; color: #8b0000; margin: 30pt 0 16pt; border-left: 5px solid #8b0000; padding-left: 12pt; letter-spacing: 3px; }
.chapter-list { display: grid; gap: 10px; }
.chapter-item {
  display: flex; align-items: center; gap: 16px;
  padding: 14px 20px; background: #fff; border: 1px solid rgba(139,0,0,0.08);
  border-radius: 6px; text-decoration: none; color: #333;
  transition: all 0.25s ease;
}
.chapter-item:hover {
  border-color: rgba(139,0,0,0.25); box-shadow: 0 4px 20px rgba(139,0,0,0.06);
  transform: translateX(4px);
}
.chapter-item .ch-label {
  font-size: 14px; color: #8b0000; font-weight: bold; letter-spacing: 2px; min-width: 90px;
  flex-shrink: 0;
}
.chapter-item .ch-desc {
  flex: 1; font-size: 13px; color: #666; line-height: 1.6; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.chapter-item .ch-arrow {
  color: #ccc; font-size: 14px; transition: all 0.2s; flex-shrink: 0;
}
.chapter-item:hover .ch-arrow { color: #8b0000; transform: translateX(4px); }
.stats-bar { text-align: center; margin: 20pt 0; font-size: 12pt; color: #888; letter-spacing: 2px; }
.stats-bar strong { color: #8b0000; }
"""
)

index_html_str = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>天龙八部深度解析 · 目录</title>
<style>{index_css}</style>
</head>
<body>
<div style="text-align:center;padding:40pt 0 20pt;page-break-after:always">
<div style="font-size:32pt;letter-spacing:8pt;color:#8b0000;margin-bottom:8pt">深度解析</div>
<div style="width:60px;height:2px;background:#c49a6c;margin:12pt auto"></div>
<div style="font-size:14pt;letter-spacing:4pt;color:#555;margin-bottom:4pt">天龙八部 · 逐回解读</div>
<div class="stats-bar">
共 <strong>{len(index_items)}</strong> 篇 · 从无量山到雁门关 · 全景细读
</div>
</div>
{"".join(index_html_items)}
<div style="text-align:center;margin:50pt 0 30pt">
<a href="index.html" style="color:#8b0000;font-size:12pt;letter-spacing:3px;border:1px solid #8b0000;padding:10px 36px;border-radius:4px;text-decoration:none;transition:all 0.2s;">← 返回天龙八部主页</a>
</div>
<div style="text-align:center;margin:20pt 0;color:#aaa;font-size:10pt;letter-spacing:2px">
金庸 · 《天龙八部》深度解析 · 全五十篇
</div>
</body>
</html>"""

index_path = PROJECT / "深度解析目录.html"
index_path.write_text(index_html_str, encoding="utf-8")
print(f"  ✅ {index_path.name}")
print("\n全部完成！")

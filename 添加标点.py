#!/usr/bin/env python3
"""
为天龙八部深度解析第44-50回添加中文标点符号。

这些文件中，正文使用空格代替了中文标点（逗号、句号、问号、引号等）。
本脚本使用启发式规则自动添加正确的标点。

用法: python3 添加标点.py
"""

import re
from pathlib import Path

PROJECT = Path(__file__).parent

# 需要处理的文件（第44-50回）
FILE_NAMES = [
    "天龙八部-第四十四回-深度解析.md",
    "天龙八部-第四十五回-深度解析.md",
    "天龙八部-第四十六回-深度解析.md",
    "天龙八部-第四十七回-深度解析.md",
    "天龙八部-第四十八回-深度解析.md",
    "天龙八部-第四十九回-深度解析.md",
    "天龙八部-第五十回-深度解析.md",
]


def has_chinese_punctuation(text):
    """检查文本是否已经包含中文标点符号"""
    return bool(
        re.search(
            r'[\u3000-\u303f\uff00-\uffef，。？、；：""' "「」！《》（）\[\]【】——……·]",
            text,
        )
    )


def is_heading_or_markdown(line):
    """判断是否为标题行或Markdown语法行"""
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    if stripped == "---":
        return True
    if stripped.startswith(">"):
        return True
    if stripped.startswith("- ") or stripped.startswith("* "):
        # 列表项 - 但也要检测是否只有空格分隔
        return False
    if stripped.startswith("<") and stripped.endswith(">"):
        return True
    if re.match(r"^\d+[\.\、]\s", stripped):
        return False
    if stripped.startswith("|"):
        # 表格行
        return True
    return False


def contains_only_chinese_spaces(text):
    """判断文本是否只包含中文字符和空格（没有标点）"""
    # 去掉空格
    no_space = text.replace(" ", "")
    # 检查是否包含中文标点
    if has_chinese_punctuation(no_space):
        return False
    # 检查是否主要是中文字符
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", no_space)
    if len(chinese_chars) > 0 and len(chinese_chars) / max(len(no_space), 1) > 0.5:
        return True
    return False


# ==================== 标点规则 ====================

# 疑问词（句子末尾出现时应加问号）
QUESTION_END_WORDS = {"吗", "呢", "么", "嘛", "否", "不成", "与否"}

# 疑问句标志词（包含这些词时该分句为疑问句）
QUESTION_MARKERS = [
    "什么",
    "怎么",
    "为什么",
    "为啥",
    "为何",
    "何必",
    "何不",
    "谁",
    "哪个",
    "哪些",
    "何处",
    "何方",
    "何地",
    "何时",
    "如何",
    "怎样",
    "怎么样",
    "咋样",
    "是否",
    "是不是",
    "有没有",
    "能不能",
    "会不会",
    "要不要",
    "敢不敢",
    "安在",
    "何在",
    "在何处",
    "在哪里",
    "在哪儿",
    "做什么",
    "干什么",
    "为何故",
    "难道",
    "究竟",
    "到底",
    "凭啥",
    "哪来",
    "哪去",
    "哪能",
    "哪敢",
    "几时",
    "多长",
    "多远",
    "多重",
    "可好",
    "可否",
    "能否",
    "是否",
]

# 转折/因果/递进词（新句子开始）
SENTENCE_START_MARKERS = [
    "但",
    "但是",
    "可",
    "可是",
    "然而",
    "不过",
    "却",
    "只是",
    "所以",
    "因此",
    "于是",
    "故而",
    "为此",
    "而且",
    "并且",
    "况且",
    "何况",
    "甚至",
    "更",
    "或者",
    "还是",
    "要么",
    "如果",
    "假如",
    "倘若",
    "要是",
    "若",
    "因为",
    "由于",
    "虽然",
    "尽管",
    "固然",
    "不但",
    "不仅",
    "不只",
    "不光",
    "然后",
    "接着",
    "随后",
    "此后",
    "此外",
    "另外",
    "还有",
    "再说",
    "总之",
    "总而言之",
    "综上",
    "第一",
    "第二",
    "第三",
    "首先",
    "其次",
    "最后",
    "一方面",
    "另一方面",
    "例如",
    "比如",
    "譬如",
    "同时",
    "与此同时",
    "否则",
    "不然",
]

# 引用动词（前后可能出现引号）
QUOTE_VERBS = [
    "说",
    "道",
    "问",
    "答",
    "喊道",
    "叫道",
    "说道",
    "问道",
    "答道",
    "大喊",
    "大叫",
    "高呼",
    "心想",
    "寻思",
    "思忖",
    "暗想",
    "念道",
    "想道",
    "写道",
    "写着",
    "描述道",
    "解释道",
    "回答",
    "反问",
    "追问",
    "质问",
    "称赞",
    "赞叹",
    "感叹",
    "骂",
    "骂道",
    "怒道",
    "笑道",
    "哭道",
    "叹道",
    "劝道",
    "劝说道",
    "吩咐",
    "命令",
    "告诉",
    "告知",
    "自言自语",
    "喃喃自语",
    "发誓",
    "承诺",
    "保证",
    "提醒",
    "警告",
    "批评",
    "批评道",
    "总结道",
    "指出",
]

# 感叹词
EXCLAMATION_END = {
    "啊",
    "呀",
    "哇",
    "哦",
    "啦",
    "咧",
    "喽",
    "呵",
    "哈",
    "嘿",
    "唉",
    "哼",
    "呸",
    "呐",
    "哟",
    "喔",
}

EXCLAMATION_START = {
    "哎呀",
    "哎哟",
    "唉",
    "哼",
    "呸",
    "哈哈",
    "呵呵",
    "嘿嘿",
    "喂",
    "嗨",
    "哦",
}


def ends_with_question_word(part):
    """判断是否以疑问词结尾"""
    for w in QUESTION_END_WORDS:
        if part.endswith(w):
            return True
    return False


def has_question_marker(part):
    """判断是否包含疑问标记"""
    for m in QUESTION_MARKERS:
        if m in part:
            return True
    return False


def starts_sentence(part):
    """判断是否为新句子的开始"""
    for m in SENTENCE_START_MARKERS:
        if part.startswith(m):
            return True
    # 以人称代词/指示代词开头
    if part.startswith(
        (
            "他",
            "她",
            "它",
            "他们",
            "她们",
            "它们",
            "我",
            "我们",
            "你",
            "您",
            "你们",
            "这",
            "那",
            "这些",
            "那些",
            "此",
            "彼",
        )
    ):
        # 但排除一些特殊情况
        if len(part) > 1:
            return True
    return False


def detect_dialogue_prefix(part):
    """检测是否为对话前缀（如：段誉说）"""
    for v in QUOTE_VERBS:
        if part.endswith(v):
            return True
        # 也匹配 "XXX说" 这种模式
        if v in part:
            idx = part.find(v)
            # 动词在末尾或接近末尾
            if idx > 0 and idx >= len(part) - len(v) - 2:
                return True
    return False


def detect_exclamation(part):
    """检测是否为感叹句"""
    for w in EXCLAMATION_END:
        if part.endswith(w):
            return True
    for s in EXCLAMATION_START:
        if part.startswith(s):
            return True
    # 含 太/真/好/多么 等 + 了/啊
    if re.search(r"(太|真|好|多么|何等).+(了|啊|呀|哇)", part):
        return True
    return False


def determine_punctuation(part, next_part, prev_part):
    """
    根据上下文决定当前部分后面的标点。

    参数:
        part: 当前部分文本
        next_part: 下一部分文本（可能为None）
        prev_part: 上一部分文本（可能为None）

    返回:
        tuple: (标点符号, 是否添加引号前缀)
    """
    # 如果当前部分已以标点结尾，返回空（不添加额外标点）
    if part and part[-1] in ("，", "。", "？", "！", "；", "：", "……", "—", "」", '"'):
        return "", False

    # 引号检测 - 前一部分以"说/道/问/答"结尾
    add_quote = False

    # 引号前缀检测
    if prev_part and detect_dialogue_prefix(prev_part):
        add_quote = True

    # 如果没有下一部分（最后一部分）
    if next_part is None:
        if ends_with_question_word(part) or has_question_marker(part):
            return "？", add_quote
        if detect_exclamation(part):
            return "！", add_quote
        return "。", add_quote

    # 检测下一部分是否为引号内容（以引号开头）
    next_is_quote = False
    if next_part and detect_dialogue_prefix(part):
        next_is_quote = True

    # 如果当前部分是对话前缀（说/道/问/答结尾）
    if detect_dialogue_prefix(part):
        return "：", add_quote

    # 如果下一部分是对话前缀
    if detect_dialogue_prefix(next_part):
        # 当前部分可能是引语内容
        if has_question_marker(part) or ends_with_question_word(part):
            return "？", add_quote
        if detect_exclamation(part):
            return "！", True
        # 短引语用逗号，长引语用句号
        if len(part) < 20:
            return "，", add_quote
        return "。", add_quote

    # 疑问句检测
    if ends_with_question_word(part) or has_question_marker(part):
        return "？", add_quote

    # 感叹句检测
    if detect_exclamation(part):
        return "！", add_quote

    # 新句子开始
    if starts_sentence(next_part):
        # 当前部分以"了/的/的。等"结束可以加句号
        if part.endswith(
            ("了", "的", "着", "过", "啦", "啊", "呀", "呢", "嘛", "而已", "罢了")
        ):
            return "。", add_quote
        # 当前部分比较长（>30字），加句号
        if len(part) > 30:
            return "。", add_quote
        return "。", add_quote

    # 如果当前部分以"是/为/包括/有/如/分为"（引出解释/列举）
    if part.endswith(
        (
            "是",
            "为",
            "包括",
            "有",
            "如",
            "分为",
            "如下",
            "以下几种",
            "几种",
            "几类",
            "三个方面",
        )
    ):
        return "：", add_quote

    # 分句连接（逗号）
    # 当前部分较短，且下一部分不是新句子
    return "，", add_quote


def add_punctuation_to_paragraph(para_text):
    """为一段文本添加中文标点"""
    # 按空格切分
    parts = para_text.split(" ")
    parts = [p.strip() for p in parts if p.strip()]

    if not parts:
        return para_text

    result = []
    prev_part = None

    for i, part in enumerate(parts):
        next_part = parts[i + 1] if i + 1 < len(parts) else None

        punct, add_left_quote = determine_punctuation(part, next_part, prev_part)

        # 构建输出
        out = part

        # 如果前一部分是引语前缀，当前部分加左引号
        if add_left_quote and not out.startswith("「") and not out.startswith('"'):
            out = "「" + out

        # 检查是否需要加右引号
        # 如果当前部分以引号内容结尾（如句号前是引语结束）
        if punct in ("。", "？", "！") and i > 0:
            prev_part_text = parts[i - 1] if i > 0 else ""
            if detect_dialogue_prefix(prev_part_text):
                # 检查引语是否已关闭
                if "」" not in out and '"' not in out:
                    out = out + "」"

        # 如果punct为空（部分已有标点结尾），不添加
        if punct:
            result.append(out + punct)
        else:
            result.append(out)
        prev_part = part

    text = "".join(result)

    # 后处理：修复一些常见问题
    # 1. 确保引号配对
    text = fix_quotes(text)

    # 2. 修复连续标点
    text = re.sub(r"[，、]+[。]", "。", text)
    text = re.sub(r"[，]+[？]", "？", text)
    text = re.sub(r"[，]+[！]", "！", text)

    # 3. 修复标点后紧跟标点的问题（如。。、？！连用中多余的）
    text = re.sub(r"[，、；：]+([。？！])", r"\1", text)
    text = re.sub(r"([。？！])[，]+", r"\1", text)

    return text


def fix_quotes(text):
    """修复引号配对问题"""
    # 确保左引号和右引号数量一致
    left_count = text.count("「")
    right_count = text.count("」")

    if left_count > right_count:
        # 补充右引号
        text += "」" * (left_count - right_count)
    elif right_count > left_count:
        # 移除多余的右引号（从末尾开始）
        text = text.rstrip("」")

    return text


def process_md_file(filepath):
    """处理单个MD文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified_lines = []
    modified_count = 0

    for line in lines:
        stripped = line.strip()

        # 跳过空行
        if not stripped:
            modified_lines.append(line)
            continue

        # 跳过标题行
        if stripped.startswith("#"):
            modified_lines.append(line)
            continue

        # 跳过分割线
        if stripped == "---":
            modified_lines.append(line)
            continue

        # 跳过引用块
        if stripped.startswith(">"):
            modified_lines.append(line)
            continue

        # 跳过列表
        if stripped.startswith("- ") or stripped.startswith("* "):
            modified_lines.append(line)
            continue

        # 跳过表格
        if stripped.startswith("|"):
            modified_lines.append(line)
            continue

        # 跳过HTML标签行
        if stripped.startswith("<") and stripped.endswith(">"):
            modified_lines.append(line)
            continue

        # 检查是否已包含中文标点
        already_has_punct = has_chinese_punctuation(stripped)

        # 检查是否包含中文字符（需要处理的）
        chinese_chars = re.findall(r"[\u4e00-\u9fff]", stripped)
        if len(chinese_chars) < 3:
            modified_lines.append(line)
            continue

        # 如果已有标点，检查是否仍有大量空格分隔的中文需要处理
        if already_has_punct:
            # 计算空格分隔的中文片段数量
            spaces = stripped.count(" ")
            # 如果空格数很少(<3)，说明标点基本完整，跳过
            if spaces < 3:
                modified_lines.append(line)
                continue
            # 如果空格数较多，但仍然有标点，需要处理
            # 这种情况是段落中已有部分标点但仍有空格需要替换
            # fall through to process

        # 如果是第一次检测到有标点但仍有空格，也处理

        # 添加标点
        new_text = add_punctuation_to_paragraph(stripped)

        # 保留原始缩进
        indent = line[: len(line) - len(line.lstrip())]
        modified_lines.append(indent + new_text + "\n")
        modified_count += 1

    # 写回文件
    content = "".join(modified_lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return modified_count


def main():
    print("=" * 60)
    print("天龙八部深度解析 - 标点添加工具")
    print("=" * 60)

    total_modified = 0
    for fname in FILE_NAMES:
        filepath = PROJECT / fname
        if not filepath.exists():
            print(f"  ❌ 未找到: {fname}")
            continue

        count = process_md_file(filepath)
        print(f"  ✅ {fname} -> 修改了 {count} 行")
        total_modified += count

    print("-" * 60)
    print(f"共处理 {len(FILE_NAMES)} 个文件，修改了 {total_modified} 行")

    # 验证修改效果
    print("\n" + "=" * 60)
    print("验证抽样（每个文件前5个段落）")
    print("=" * 60)
    for fname in FILE_NAMES:
        filepath = PROJECT / fname
        if not filepath.exists():
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        para_count = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("#")
                and not stripped.startswith("-")
                and not stripped.startswith(">")
                and not stripped.startswith("|")
                and not stripped == "---"
            ):
                if has_chinese_punctuation(stripped) and not stripped.startswith("<"):
                    print(f"\n📄 {fname} - 第{i + 1}行:")
                    print(f"   {stripped[:120]}...")
                    para_count += 1
                    if para_count >= 3:
                        break


if __name__ == "__main__":
    main()

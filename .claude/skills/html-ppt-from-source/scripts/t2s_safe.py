#!/usr/bin/env python3
"""
t2s_safe.py — 安全的繁体 → 简体转换

为 html-ppt-from-source skill 设计。在 zhconv 的基础上做两层保护：

1. 保留「」直角引号 — 中国风主题的视觉签名，zhconv 默认会转成弯引号
2. 保留壹贰叁肆伍陆柒捌玖 大写数字 — 章序号 / 印章用，zhconv 会转成简体一二三

用法:
    python3 t2s_safe.py path/to/index.html
    python3 t2s_safe.py path/to/index.html --no-quotes-preserve   # 关闭引号保护
    python3 t2s_safe.py path/to/index.html --no-numerals-preserve # 关闭大写数字保护
    python3 t2s_safe.py path/to/index.html --dry-run              # 只报告,不写文件

退出码:
    0 - 成功（含 "已是纯简体" 的情形）
    1 - 文件读取失败
    2 - zhconv 库不可用且无法自动安装
    3 - 输出验证失败（写入后内容异常）
"""

from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path


# 大写数字保护表：键是源字符（可繁可简），值是要还原成的简体大写
# zhconv 默认会把"壹贰叁..."转成"一二三..."，破坏章序号 / 印章效果
# 这里同时收录繁体形式（貳/參/陸），让源文档不论繁简都能正确归一到简体大写
NUMERAL_PROTECTION_MAP = {
    # 简体大写本身
    "壹": "壹", "贰": "贰", "叁": "叁", "肆": "肆", "伍": "伍",
    "陆": "陆", "柒": "柒", "捌": "捌", "玖": "玖", "拾": "拾",
    # 繁体大写 → 归一到简体大写
    "貳": "贰", "參": "叁", "陸": "陆",
}


def ensure_zhconv() -> None:
    """尝试 import zhconv，如不可用则尝试 pip --user install。"""
    try:
        import zhconv  # noqa: F401
        return
    except ImportError:
        pass

    print("zhconv 库未安装，尝试 pip install --user zhconv ...", file=sys.stderr)
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "--quiet", "zhconv"],
            check=True,
            timeout=60,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"自动安装失败: {e}", file=sys.stderr)
        print("请手动运行: pip3 install --user zhconv", file=sys.stderr)
        sys.exit(2)

    try:
        import zhconv  # noqa: F401
    except ImportError:
        print("安装后仍无法 import zhconv，请检查 Python 环境", file=sys.stderr)
        sys.exit(2)


def protect_corner_quotes(text):
    """把「」用唯一占位符替换，返回 (new_text, mapping)。"""
    open_placeholder = "HPPT_OQ"
    close_placeholder = "HPPT_CQ"
    new = text.replace("「", open_placeholder).replace("」", close_placeholder)
    mapping = {open_placeholder: "「", close_placeholder: "」"}
    return new, mapping


def protect_numerals(text):
    """把大写数字（繁/简两种写法）替换为占位符，还原时统一回写为简体大写。"""
    mapping = {}
    new = text
    for i, (src, target) in enumerate(NUMERAL_PROTECTION_MAP.items()):
        placeholder = f"HPPT_N{i:02d}"
        if src in new:
            new = new.replace(src, placeholder)
            mapping[placeholder] = target  # 还原成目标简体大写
    return new, mapping


def restore(text, *mappings):
    """按所有 mapping 还原占位符。"""
    for m in mappings:
        for placeholder, original in m.items():
            text = text.replace(placeholder, original)
    return text


def convert_file(
    path,
    preserve_quotes=True,
    preserve_numerals=True,
    dry_run=False,
):
    """转换文件，返回统计信息字典。"""
    if not path.exists():
        print(f"文件不存在: {path}", file=sys.stderr)
        sys.exit(1)

    original_text = path.read_text(encoding="utf-8")
    original_len = len(original_text)
    text = original_text

    # 阶段 1：保护
    mappings = []
    if preserve_quotes:
        text, m = protect_corner_quotes(text)
        mappings.append(m)
    if preserve_numerals:
        text, m = protect_numerals(text)
        mappings.append(m)

    # 阶段 2：转换
    from zhconv import convert
    converted = convert(text, "zh-cn")

    # 阶段 3：还原
    final = restore(converted, *mappings)

    # 统计
    diff_count = sum(1 for a, b in zip(original_text, final) if a != b)
    stats = {
        "original_size": original_len,
        "final_size": len(final),
        "chars_changed": diff_count,
        "preserved_quotes": preserve_quotes,
        "preserved_numerals": preserve_numerals,
    }

    # 二次验证：转完后再过一遍 zhconv，应只剩被保护的字符不同
    if preserve_quotes or preserve_numerals:
        again = convert(final, "zh-cn")
        residual = set()
        for a, b in zip(final, again):
            if a != b:
                residual.add(a)
        allowed = set()
        if preserve_quotes:
            allowed.update({"「", "」"})
        if preserve_numerals:
            allowed.update(NUMERAL_PROTECTION_MAP.values())
        unexpected = residual - allowed
        if unexpected:
            print(
                f"⚠ 验证警告：仍有未预料的繁体残留 {len(unexpected)} 个: "
                f"{''.join(sorted(unexpected))}",
                file=sys.stderr,
            )
            stats["unexpected_residual"] = sorted(unexpected)

    # 写入
    if not dry_run:
        path.write_text(final, encoding="utf-8")

    return stats


def main():
    parser = argparse.ArgumentParser(description="安全繁→简转换（保留「」和大写数字）")
    parser.add_argument("path", help="目标 HTML/MD/TXT 文件路径")
    parser.add_argument(
        "--no-quotes-preserve",
        action="store_true",
        help="关闭「」保护，按 zhconv 默认转成弯引号",
    )
    parser.add_argument(
        "--no-numerals-preserve",
        action="store_true",
        help="关闭壹贰叁保护，按 zhconv 默认转成一二三",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只报告统计，不写文件",
    )
    args = parser.parse_args()

    ensure_zhconv()

    stats = convert_file(
        Path(args.path),
        preserve_quotes=not args.no_quotes_preserve,
        preserve_numerals=not args.no_numerals_preserve,
        dry_run=args.dry_run,
    )

    print(f"✓ 转换{'（dry-run）' if args.dry_run else ''}完成")
    print(f"  文件:        {args.path}")
    print(f"  原始字符数:   {stats['original_size']}")
    print(f"  改变字符数:   {stats['chars_changed']}")
    print(f"  保留「」:    {stats['preserved_quotes']}")
    print(f"  保留壹贰叁:   {stats['preserved_numerals']}")
    if "unexpected_residual" in stats:
        print(f"  ⚠ 意外残留: {''.join(stats['unexpected_residual'])}")
        sys.exit(3)


if __name__ == "__main__":
    main()

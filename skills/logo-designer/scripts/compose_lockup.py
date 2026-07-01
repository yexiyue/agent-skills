#!/usr/bin/env python3
"""把图标 SVG 和一段文字拼成横向的"图标+文字"组合标（combination mark lockup）。

对齐逻辑：文字用字体的 Cap Height（大写字母视觉高度，从 OS/2.sCapHeight 读取，
不是简单的 ascent/descent 包围盒）跟图标的竖直中线对齐——这是专业 lockup 最常见
的对齐基准（design-principles-guide.md 第二章"锁定网格 Lockup Grid"提到的
"确定 logomark 与 wordmark 间距和层级"）。图标与文字的间距按图标高度的比例给
（--gap-ratio，对应 clear space 用 X 单位表达的惯例，默认 0.6X）。

用法：
    python3 compose_lockup.py --icon logo-color.svg --text "SwarmDrop" \\
        --font "/System/Library/Fonts/Avenir Next.ttc" --face 2 \\
        --color "#12233F" -o lockup.svg
"""
import argparse
import re
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTCollection, TTFont


def load_font(font_path: Path, face: int):
    if font_path.suffix.lower() == ".ttc":
        return TTCollection(str(font_path)).fonts[face]
    return TTFont(str(font_path))


def read_icon(icon_path: Path):
    text = icon_path.read_text(encoding="utf-8")
    svg_tag_match = re.search(r"<svg\b[^>]*>", text, flags=re.S)
    header = svg_tag_match.group(0)
    w = float(re.search(r'width="([\d.]+)', header).group(1))
    h = float(re.search(r'height="([\d.]+)', header).group(1))
    inner = text[svg_tag_match.end() : text.rindex("</svg>")]
    inner = re.sub(r"<!--.*?-->", "", inner, flags=re.S)
    return inner.strip(), w, h


def build_wordmark_paths(text: str, font, scale: float, color: str, tracking: float):
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    cursor = 0.0
    parts = []
    for ch in text:
        glyph_name = cmap.get(ord(ch))
        if glyph_name is None:
            raise SystemExit(f"字体里没有字符 {ch!r} 对应的字形")
        pen = SVGPathPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        d = pen.getCommands()
        if d:
            parts.append(f'<g transform="translate({cursor},0)"><path d="{d}"/></g>')
        cursor += hmtx[glyph_name][0] + tracking
    total_advance = cursor
    return (
        f'<g fill="{color}" transform="scale({scale:.6f},{-scale:.6f})">' + "".join(parts) + "</g>",
        total_advance,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--icon", type=Path, required=True, help="图标 SVG 路径")
    ap.add_argument("--text", required=True, help="wordmark 文字内容")
    ap.add_argument("--font", type=Path, required=True)
    ap.add_argument("--face", type=int, default=0)
    ap.add_argument("--color", default="#000000", help="wordmark 文字颜色")
    ap.add_argument("--cap-ratio", type=float, default=0.68,
                     help="文字 Cap Height 相对图标高度的比例（默认0.68，是常见的图标偏大、文字偏小的组合标比例）")
    ap.add_argument("--gap-ratio", type=float, default=0.6,
                     help="图标与文字之间的间距，单位是图标高度的倍数（X单位，默认0.6X）")
    ap.add_argument("--tracking", type=float, default=0, help="字符间距微调（字体内部unit）")
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    icon_inner, icon_w, icon_h = read_icon(args.icon)
    font = load_font(args.font, args.face)
    upm = font["head"].unitsPerEm
    os2 = font["OS/2"]
    cap_height_units = getattr(os2, "sCapHeight", None) or round(upm * 0.7)
    descent_units = -font["hhea"].descent  # 正值

    target_cap_height_px = args.cap_ratio * icon_h
    scale = target_cap_height_px / cap_height_units

    wordmark_group, total_advance_units = build_wordmark_paths(
        args.text, font, scale, args.color, args.tracking
    )
    wordmark_width_px = total_advance_units * scale
    descent_px = descent_units * scale

    gap_px = args.gap_ratio * icon_h
    baseline_y = icon_h / 2 + target_cap_height_px / 2
    wordmark_x = icon_w + gap_px

    canvas_w = wordmark_x + wordmark_width_px
    canvas_h = max(icon_h, baseline_y + descent_px)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w:.1f}" height="{canvas_h:.1f}" '
        f'viewBox="0 0 {canvas_w:.1f} {canvas_h:.1f}">'
        f"{icon_inner}"
        f'<g transform="translate({wordmark_x:.2f},{baseline_y:.2f})">{wordmark_group}</g>'
        f"</svg>"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")
    print(f"[compose_lockup] 已生成: {args.output}  ({canvas_w:.0f}x{canvas_h:.0f})")


if __name__ == "__main__":
    main()

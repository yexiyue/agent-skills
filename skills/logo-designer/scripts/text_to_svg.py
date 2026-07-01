#!/usr/bin/env python3
"""把一段文字用字体的真实轮廓转成矢量 SVG 路径（wordmark 转曲）。

对应 design-principles-guide.md 5.6 节的行业惯例：wordmark 定稿后应该把文字轮廓
转成矢量路径再交付，而不是依赖字体文件本身——这样拿到 logo 的人不需要安装同一款
字体也能正常显示/编辑。比起"生成位图再描摹"，直接读字体的矢量轮廓不会有描摹误差、
笔画干净，更适合专业交付。

用法：
    python3 text_to_svg.py "SwarmDrop" -o wordmark.svg \\
        --font "/System/Library/Fonts/Avenir Next.ttc" --face 2 \\
        --size 200 --tracking 0 --color "#12233F"

--face 用于 .ttc 字体合集，指定具体字重/字型（不传就用 --list-faces 先看看有哪些）。
"""
import argparse
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTCollection, TTFont


def load_font(font_path: Path, face: int):
    if font_path.suffix.lower() == ".ttc":
        collection = TTCollection(str(font_path))
        return collection.fonts[face]
    return TTFont(str(font_path))


def list_faces(font_path: Path) -> None:
    collection = TTCollection(str(font_path))
    for i, f in enumerate(collection.fonts):
        name = f["name"]
        print(i, name.getDebugName(1), "|", name.getDebugName(2))


def text_to_svg(text: str, font, size: float, tracking: float, color: str) -> str:
    upm = font["head"].unitsPerEm
    scale = size / upm
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]

    cursor = 0.0
    path_d_parts = []

    for ch in text:
        codepoint = ord(ch)
        glyph_name = cmap.get(codepoint)
        if glyph_name is None:
            raise SystemExit(f"字体里没有字符 {ch!r} 对应的字形")
        glyph = glyph_set[glyph_name]

        pen = SVGPathPen(glyph_set)
        glyph.draw(pen)
        d = pen.getCommands()
        if d:
            path_d_parts.append(f'<g transform="translate({cursor},0)">' f'<path d="{d}"/></g>')

        advance = hmtx[glyph_name][0]
        cursor += advance + tracking

    inner = "".join(path_d_parts)
    # 字体坐标系 Y 轴向上，SVG 是向下，用 scale(1,-1) 翻转；translate 把翻转后的内容挪回可见区域
    ascent = font["hhea"].ascent
    descent = font["hhea"].descent
    total_width = cursor * scale
    total_height = (ascent - descent) * scale

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_width:.2f}" height="{total_height:.2f}" '
        f'viewBox="0 0 {total_width:.2f} {total_height:.2f}">'
        f'<g fill="{color}" transform="translate(0,{ascent * scale:.2f}) scale({scale:.6f},{-scale:.6f})">'
        f"{inner}"
        f"</g></svg>"
    )
    return svg


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?", help="要转换的文字")
    ap.add_argument("-o", "--output", type=Path, help="输出 SVG 路径")
    ap.add_argument("--font", type=Path, required=True, help="字体文件路径（.ttf/.otf/.ttc）")
    ap.add_argument("--face", type=int, default=0, help=".ttc 合集里的第几个字型（默认0）")
    ap.add_argument("--size", type=float, default=200, help="字号（字体单位换算后的像素高度，默认200）")
    ap.add_argument("--tracking", type=float, default=0, help="字符间距微调，单位是字体内部unit（默认0）")
    ap.add_argument("--color", default="#000000", help="文字填充色")
    ap.add_argument("--list-faces", action="store_true", help="列出.ttc里所有字型后退出")
    args = ap.parse_args()

    if args.list_faces:
        list_faces(args.font)
        return

    if not args.text or not args.output:
        raise SystemExit("需要提供文字内容和 -o 输出路径（或用 --list-faces 查看字型列表）")

    font = load_font(args.font, args.face)
    svg = text_to_svg(args.text, font, args.size, args.tracking, args.color)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")
    print(f"[text_to_svg] 已生成: {args.output}")


if __name__ == "__main__":
    main()

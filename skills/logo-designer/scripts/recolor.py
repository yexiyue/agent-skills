#!/usr/bin/env python3
"""把一个 logo 资产整体重新填色成单一实色，用来从彩色/黑色版本快速派生出
纯黑版、纯白反白版（design-principles-guide.md 4.4：单色版本不是简单去饱和度，
而是整体替换成纯色填充）。

支持两种输入：
- .svg：正则替换所有 fill="..." 为目标色（vtracer/potrace 产出的 SVG 结构简单，
  这个做法足够可靠；复杂的手工 SVG 可能需要人工检查结果）
- 位图(.png 等)：按 alpha 通道当作形状蒙版，可见区域整体填成目标色，透明区域保持透明

用法：
    python3 recolor.py mono-black.svg -o mono-white.svg --color "#FFFFFF"
    python3 recolor.py source.png -o silhouette.png --color "#FFFFFF" --alpha-threshold 16
"""
import argparse
import re
from pathlib import Path

from PIL import Image, ImageColor


def recolor_svg(path: Path, color_hex: str) -> str:
    text = path.read_text(encoding="utf-8")
    return re.sub(r'fill="#?[0-9a-fA-F]{3,8}"', f'fill="{color_hex}"', text)


def recolor_raster(path: Path, color_hex: str, alpha_threshold: int) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    r, g, b, a = img.split()
    solid_rgb = Image.new("RGB", img.size, ImageColor.getrgb(color_hex))
    # alpha 低于阈值的地方视为背景，直接清零，避免半透明边缘留下原色残影
    a = a.point(lambda v: v if v >= alpha_threshold else 0)
    out = Image.new("RGBA", img.size)
    out.paste(solid_rgb, (0, 0))
    out.putalpha(a)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--color", required=True, help='目标填充色，如 "#FFFFFF"')
    ap.add_argument("--alpha-threshold", type=int, default=16, help="位图模式下，alpha 低于此值视为背景（0-255）")
    args = ap.parse_args()

    if not args.input.exists():
        raise SystemExit(f"输入文件不存在: {args.input}")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.input.suffix.lower() == ".svg":
        svg_text = recolor_svg(args.input, args.color)
        args.output.write_text(svg_text, encoding="utf-8")
    else:
        img = recolor_raster(args.input, args.color, args.alpha_threshold)
        img.save(args.output)

    print(f"[recolor] 已生成: {args.output}")


if __name__ == "__main__":
    main()

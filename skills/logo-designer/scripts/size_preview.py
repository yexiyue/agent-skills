#!/usr/bin/env python3
"""生成"多尺寸 x 多背景"预览联系表，用于第五阶段可用性测试。

对应 references/design-principles-guide.md 3.x 节（最小尺寸）和
references/ai-generation-guide.md 4.4/5.3 节（缩小到 favicon/App 图标尺寸后
细节糊成一团 -> 必须在 16/32/48/128/512px 等尺寸下逐一检查；黑白/反白/多背景
分别测试）里总结的验收方法：每个尺寸都按"实际渲染出的像素"缩略图检查，而不是
拿大图直接肉眼缩小看。

用法：
    python3 size_preview.py -o contact_sheet.png \\
        --variant "全彩版:color.svg:#FFFFFF" \\
        --variant "全彩版-灰底:color.svg:#9A9A9A" \\
        --variant "纯黑版:black.svg:#FFFFFF" \\
        --variant "反白版:white.svg:#111111"

--variant 可重复传入多次，每个格式为 "标签:图片路径(svg/png均可):十六进制背景色"。
每个 variant 会渲染成一行，每行按 --sizes 里的每个像素尺寸各生成一列。
"""
import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageColor

DISPLAY_CELL = 140  # 每个格子在联系表里的显示尺寸（像素），小尺寸会被放大方便肉眼查看
LABEL_W = 160
HEADER_H = 36
PAD = 12

# PIL 的 ImageFont.load_default() 不含中文字形，标签是中文时会变成方块。
# 按常见系统路径找一个能显示中文的字体，找不到就退回默认字体（英文标签仍可用）。
_CJK_FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",  # macOS
    "/System/Library/Fonts/STHeiti Medium.ttc",  # macOS 备选
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # 常见 Linux 发行版
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "C:\\Windows\\Fonts\\msyh.ttc",  # Windows 微软雅黑
]


def load_label_font(size: int = 16) -> ImageFont.FreeTypeFont:
    for path in _CJK_FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def rasterize(path: Path, size: int) -> Image.Image:
    """把 svg 或位图渲染成恰好 size x size、带 alpha 的正方形画布（内容居中等比缩放）。"""
    if path.suffix.lower() == ".svg":
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        subprocess.run(
            ["magick", "-background", "none", str(path), "-resize", f"{size}x{size}", str(tmp_path)],
            check=True,
        )
        img = Image.open(tmp_path).convert("RGBA")
        tmp_path.unlink(missing_ok=True)
    else:
        img = Image.open(path).convert("RGBA")

    # 等比缩放到 size 内，居中贴到 size x size 透明画布上
    img.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
    return canvas


def composite_on_bg(img: Image.Image, bg_hex: str) -> Image.Image:
    bg = Image.new("RGBA", img.size, ImageColor.getrgb(bg_hex) + (255,))
    bg.alpha_composite(img)
    return bg.convert("RGB")


def render_cell(path: Path, size: int, bg_hex: str) -> Image.Image:
    small = rasterize(path, size)
    flat = composite_on_bg(small, bg_hex)
    # 用最近邻放大到统一的展示尺寸，刻意保留像素颗粒感——这才是 size px 下的真实观感
    return flat.resize((DISPLAY_CELL, DISPLAY_CELL), Image.NEAREST)


def parse_variant(spec: str):
    label, path, bg = spec.split(":", 2)
    return label, Path(path), bg


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", type=Path, required=True, help="输出联系表 PNG 路径")
    ap.add_argument("--variant", action="append", required=True,
                     help='重复传入，格式 "标签:图片路径:十六进制背景色"，例如 "反白版:white.svg:#111111"')
    ap.add_argument("--sizes", default="16,32,48,128,512", help="逗号分隔的像素尺寸列表")
    args = ap.parse_args()

    sizes = [int(s) for s in args.sizes.split(",")]
    variants = [parse_variant(v) for v in args.variant]

    for _, path, _ in variants:
        if not path.exists():
            raise SystemExit(f"找不到文件: {path}")

    sheet_w = LABEL_W + PAD + len(sizes) * (DISPLAY_CELL + PAD)
    sheet_h = HEADER_H + PAD + len(variants) * (DISPLAY_CELL + PAD)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    font = load_label_font(16)

    for col, size in enumerate(sizes):
        x = LABEL_W + PAD + col * (DISPLAY_CELL + PAD)
        draw.text((x + DISPLAY_CELL // 2 - 12, 10), f"{size}px", fill=(0, 0, 0), font=font)

    for row, (label, path, bg_hex) in enumerate(variants):
        y = HEADER_H + PAD + row * (DISPLAY_CELL + PAD)
        draw.text((8, y + DISPLAY_CELL // 2 - 6), label, fill=(0, 0, 0), font=font)
        for col, size in enumerate(sizes):
            x = LABEL_W + PAD + col * (DISPLAY_CELL + PAD)
            cell = render_cell(path, size, bg_hex)
            sheet.paste(cell, (x, y))
            draw.rectangle([x, y, x + DISPLAY_CELL, y + DISPLAY_CELL], outline=(200, 200, 200))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    print(f"[size_preview] 联系表已生成: {args.output}  ({sheet_w}x{sheet_h})")
    print("[size_preview] 检查要点：16/32px 格子里的图形轮廓是否还能一眼认出；细线条/小间隙是否已经糊成一团。")


if __name__ == "__main__":
    main()

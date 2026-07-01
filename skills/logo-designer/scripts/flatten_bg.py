#!/usr/bin/env python3
"""把 AI 生图工具输出的纯色背景（通常是白底，因为提示词里建议写
"pure white background" 而不是 "transparent"——见 ai-generation-guide.md
3.2 节的原因说明）转成真正的 alpha 透明背景，供后续 vectorize.py /
size_preview.py 使用，避免矢量化时把背景色描成一个实色矩形。

用法：
    python3 flatten_bg.py input.png -o input-transparent.png
    python3 flatten_bg.py input.png -o out.png --bg-color "#FFFFFF" --threshold 245 --feather 35
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageColor


def flatten(img: Image.Image, bg_hex: str, threshold: int, feather: int) -> Image.Image:
    rgba = np.asarray(img.convert("RGBA"), dtype=np.int16)
    bg = np.array(ImageColor.getrgb(bg_hex), dtype=np.int16)

    # 与背景色的 RMS 距离：用欧氏距离而不是单通道最大差值，避免像青绿这种
    # 「某个通道本来就接近白色」的彩色前景被误判成半透明背景
    dist = np.sqrt(np.mean((rgba[:, :, :3].astype(np.float32) - bg) ** 2, axis=2))
    new_alpha = np.clip((dist.astype(np.float32) - (threshold - feather)) / feather * 255, 0, 255)
    new_alpha = new_alpha.astype(np.uint8)

    rgba[:, :, 3] = np.minimum(rgba[:, :, 3], new_alpha)
    return Image.fromarray(rgba.astype(np.uint8))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--bg-color", default="#FFFFFF", help="要抠掉的背景色（默认纯白）")
    ap.add_argument("--threshold", type=int, default=40,
                     help="与背景色的RMS距离达到这个阈值即视为100%%前景（默认40，值越小越激进，"
                          "浅色/低饱和度前景需要调小）")
    ap.add_argument("--feather", type=int, default=25,
                     help="threshold往下feather这么多算羽化过渡区，避免边缘出现硬锯齿（默认25）")
    args = ap.parse_args()

    if not args.input.exists():
        raise SystemExit(f"输入文件不存在: {args.input}")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(args.input)
    out = flatten(img, args.bg_color, args.threshold, args.feather)
    out.save(args.output)
    print(f"[flatten_bg] 已生成透明背景版本: {args.output}")


if __name__ == "__main__":
    main()

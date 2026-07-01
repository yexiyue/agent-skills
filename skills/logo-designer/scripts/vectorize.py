#!/usr/bin/env python3
"""AI 生成的位图 logo -> 清理后的矢量 SVG。

背景（详见 references/ai-generation-guide.md 第五章）：AI 绘图工具输出的都是位图，
边缘/渐变里混杂大量近似色的杂色像素；如果直接拿去描摹，会产出几千个锚点的臃肿路径。
这个脚本先用 Pillow 把颜色收敛成少数几个纯色色块（消掉杂色），再交给 vtracer（彩色）
或 potrace（黑白单色）描摹，最后粗略统计一下路径复杂度，方便判断要不要继续手动简化。

用法：
    python3 vectorize.py input.png -o output.svg
    python3 vectorize.py input.png -o output.svg --mode mono --threshold 0.55
    python3 vectorize.py input.png -o output.svg --mode color --colors 4

依赖：本机需已安装 vtracer（color 模式）和/或 potrace（mono 模式），以及 Pillow。
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def quantize_color(src: Image.Image, colors: int) -> Image.Image:
    """把杂色/渐变收敛成 <=colors 个纯色色块，减少描摹后的锚点数量。"""
    rgba = src.convert("RGBA")
    alpha = rgba.getchannel("A")
    rgb = rgba.convert("RGB")

    # 调色板只从完全不透明的像素里选取，避免海量透明背景/半透明羽化边缘像素
    # 把稀有的前景色"稀释"进同一个调色板格子（例如把靛蓝和青绿错误合并成一种颜色）。
    alpha_arr = np.array(alpha)
    rgb_arr = np.array(rgb)
    opaque_pixels = rgb_arr[alpha_arr >= 250]
    if len(opaque_pixels) == 0:
        opaque_pixels = rgb_arr.reshape(-1, 3)

    side = max(1, int(np.ceil(np.sqrt(len(opaque_pixels)))))
    padded = np.zeros((side * side, 3), dtype=np.uint8)
    padded[: len(opaque_pixels)] = opaque_pixels
    palette_source = Image.fromarray(padded.reshape(side, side, 3)).quantize(
        colors=colors, method=Image.Quantize.MEDIANCUT
    )

    quantized = rgb.quantize(colors=colors, palette=palette_source, dither=Image.Dither.NONE)
    result = quantized.convert("RGBA")
    result.putalpha(alpha)
    return result


def to_bitmap_pbm(src: Image.Image, threshold: float, out_path: Path) -> None:
    """转成 potrace 能读的 1-bit PBM 位图（potrace 只认 pnm/bmp，不吃 PNG）。"""
    rgba = src.convert("RGBA")
    alpha = np.array(rgba.getchannel("A"))

    if alpha.min() < 250:
        # 有真正的透明通道时，前景/背景直接按 alpha 判断，不要按亮度判断——
        # 亮度阈值对青绿这类"本身就偏亮"的前景色会误判成背景（见 vectorize.py
        # changelog：反白版曾经把整个青绿鸟头判没了）。
        bw_arr = np.where(alpha > threshold * 255, 0, 255).astype(np.uint8)
        bw = Image.fromarray(bw_arr).convert("1")
    else:
        # 没有 alpha 信息（比如整张图本来就不透明）时，退回按亮度二值化
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.getchannel("A"))
        gray = bg.convert("L")
        bw = gray.point(lambda p: 255 if p > threshold * 255 else 0, mode="1")

    bw.save(out_path)


def run_vtracer(input_png: Path, output_svg: Path, args) -> None:
    cmd = [
        "vtracer",
        "--input", str(input_png),
        "--output", str(output_svg),
        "--mode", "spline",
        "--colormode", "color",
        "--filter_speckle", str(args.filter_speckle),
        "--corner_threshold", str(args.corner_threshold),
        "--color_precision", str(args.color_precision),
        "--path_precision", "3",
    ]
    subprocess.run(cmd, check=True)


def run_potrace(input_pbm: Path, output_svg: Path, args) -> None:
    cmd = [
        "potrace",
        str(input_pbm),
        "--svg",
        "-o", str(output_svg),
        "--turdsize", str(args.turdsize),
        "--alphamax", str(args.alphamax),
        "--opttolerance", str(args.opttolerance),
    ]
    subprocess.run(cmd, check=True)


def report_complexity(svg_path: Path) -> None:
    text = svg_path.read_text(encoding="utf-8", errors="ignore")
    path_count = len(re.findall(r"<path\b", text))
    # 粗略统计所有 path 的 d 属性里贝塞尔/直线/移动指令的数量，近似锚点数
    d_attrs = re.findall(r'\sd="([^"]+)"', text)
    command_count = sum(len(re.findall(r"[MLCQZmlcqz]", d)) for d in d_attrs)
    size_kb = svg_path.stat().st_size / 1024
    print(f"[vectorize] 输出: {svg_path}  ({size_kb:.1f} KB)")
    print(f"[vectorize] path 数量: {path_count}，估算锚点/指令数: {command_count}")
    if command_count > 800:
        print(
            "[vectorize] 提醒：锚点数偏高（>800），logo 通常应在几十到几百个锚点内。"
            "可以尝试调低 --colors、调高 --filter_speckle，或者在 Illustrator 里"
            "对 path 执行「对象 > 路径 > 简化」（参见 design-principles-guide.md"
            " 第二章 2.3 与 ai-generation-guide.md 5.3 节的清理清单）。"
        )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path, help="输入位图路径（PNG/JPG）")
    ap.add_argument("-o", "--output", type=Path, required=True, help="输出 SVG 路径")
    ap.add_argument("--mode", choices=["color", "mono"], default="color",
                     help="color=多色扁平图形（用 vtracer），mono=单色线稿/文字标（用 potrace）")
    ap.add_argument("--colors", type=int, default=6, help="color 模式下量化的颜色数（默认 6，对应设计规范里\"主色不超过3种\"外加中间过渡色）")
    ap.add_argument("--threshold", type=float, default=0.5, help="mono 模式下的黑白分界阈值 0-1（默认 0.5）")
    ap.add_argument("--filter_speckle", type=int, default=4, help="vtracer: 丢弃小于此像素数的杂色斑点")
    ap.add_argument("--corner_threshold", type=int, default=60, help="vtracer: 判定为拐角的最小角度")
    ap.add_argument("--color_precision", type=int, default=6, help="vtracer: RGB 每通道有效位数")
    ap.add_argument("--turdsize", type=int, default=2, help="potrace: 抑制小于此尺寸的斑点")
    ap.add_argument("--alphamax", type=float, default=1.0, help="potrace: 拐角判定阈值")
    ap.add_argument("--opttolerance", type=float, default=0.2, help="potrace: 曲线优化容差")
    ap.add_argument("--keep-temp", action="store_true", help="保留中间清理后的位图，便于检查量化效果")
    args = ap.parse_args()

    if not args.input.exists():
        sys.exit(f"输入文件不存在: {args.input}")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    src = Image.open(args.input)

    if args.mode == "color":
        cleaned = quantize_color(src, args.colors)
        tmp_png = args.output.with_suffix(".cleaned.png")
        cleaned.save(tmp_png)
        run_vtracer(tmp_png, args.output, args)
        if not args.keep_temp:
            tmp_png.unlink(missing_ok=True)
    else:
        tmp_pbm = args.output.with_suffix(".cleaned.pbm")
        to_bitmap_pbm(src, args.threshold, tmp_pbm)
        run_potrace(tmp_pbm, args.output, args)
        if not args.keep_temp:
            tmp_pbm.unlink(missing_ok=True)

    report_complexity(args.output)


if __name__ == "__main__":
    main()

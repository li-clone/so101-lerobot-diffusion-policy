#!/usr/bin/env python3
"""Render ACT versus Diffusion hardware success rates from summary CSV."""

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    with args.csv.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    width, height = 820, 460
    left, right, top, bottom = 90, 35, 45, 85
    plot_height = height - top - bottom
    colors = ("#2563eb", "#7c3aed")
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:system-ui,sans-serif;fill:#111827}.grid{stroke:#e5e7eb}.axis{stroke:#111827;stroke-width:1.5}</style>',
    ]
    for index in range(6):
        value = index * 20
        y = top + plot_height * (1 - value / 100)
        svg.append(f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}"/>')
        svg.append(f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" font-size="13">{value}%</text>')
    slot = (width - left - right) / len(rows)
    bar_width = min(180, slot * 0.52)
    for index, row in enumerate(rows):
        rate = float(row["success_rate"])
        x = left + slot * (index + 0.5) - bar_width / 2
        y = top + plot_height * (1 - rate)
        bar_height = plot_height * rate
        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" rx="5" fill="{colors[index % len(colors)]}"/>')
        svg.append(f'<text x="{x+bar_width/2:.1f}" y="{y-10:.1f}" text-anchor="middle" font-size="16" font-weight="700">{int(row["total_successes"])}/{int(row["total_trials"])} ({rate*100:.1f}%)</text>')
        svg.append(f'<text x="{x+bar_width/2:.1f}" y="{height-bottom+30}" text-anchor="middle" font-size="15">{row["policy"]}</text>')
    svg.append(f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}"/>')
    svg.append(f'<line class="axis" x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}"/>')
    svg.append(f'<text transform="translate(24 {height/2}) rotate(-90)" text-anchor="middle" font-size="14">hardware success rate</text>')
    svg.append("</svg>")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(svg) + "\n")


if __name__ == "__main__":
    main()

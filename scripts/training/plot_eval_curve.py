#!/usr/bin/env python3
"""Render an eval-curve CSV as a dependency-free SVG."""

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
    points = [(int(row["step"]), float(row["eval_loss"])) for row in rows]
    if len(points) < 2:
        raise ValueError("At least two points are required")
    min_step, max_step = min(s for s, _ in points), max(s for s, _ in points)
    min_loss, max_loss = min(v for _, v in points), max(v for _, v in points)
    width, height = 900, 520
    left, right, top, bottom = 80, 30, 35, 70

    def x(step: int) -> float:
        return left + (step - min_step) / (max_step - min_step) * (width - left - right)

    def y(loss: float) -> float:
        return top + (max_loss - loss) / (max_loss - min_loss) * (height - top - bottom)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:system-ui,sans-serif;fill:#111827;font-size:13px}.grid{stroke:#e5e7eb}.axis{stroke:#111827;stroke-width:1.5}</style>',
    ]
    for index in range(6):
        loss = min_loss + (max_loss - min_loss) * index / 5
        yy = y(loss)
        svg.append(f'<line class="grid" x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}"/>')
        svg.append(f'<text x="{left-10}" y="{yy+4:.1f}" text-anchor="end">{loss:.3f}</text>')
    for step in range(10000, 50001, 10000):
        xx = x(step)
        svg.append(f'<line class="grid" x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{height-bottom}"/>')
        svg.append(f'<text x="{xx:.1f}" y="{height-bottom+24}" text-anchor="middle">{step//1000}k</text>')
    svg.extend([
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}"/>',
        f'<line class="axis" x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}"/>',
        f'<text x="{width/2}" y="{height-18}" text-anchor="middle">training step</text>',
        f'<text transform="translate(20 {height/2}) rotate(-90)" text-anchor="middle">eval loss</text>',
    ])
    polyline = " ".join(f"{x(step):.1f},{y(loss):.1f}" for step, loss in points)
    svg.append(f'<polyline points="{polyline}" fill="none" stroke="#7c3aed" stroke-width="2.5"/>')
    best_step, best_loss = min(points, key=lambda item: item[1])
    svg.append(f'<circle cx="{x(best_step):.1f}" cy="{y(best_loss):.1f}" r="5" fill="#dc2626"/>')
    svg.append(f'<text x="{x(best_step)+10:.1f}" y="{y(best_loss)-9:.1f}">best: {best_step//1000}k / {best_loss:.4f}</text>')
    svg.append("</svg>")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(svg) + "\n")


if __name__ == "__main__":
    main()

"""Render each ```mermaid block in examples/*.md to the PNG referenced just above it.

For every mermaid block, the nearest preceding `![...](images/<name>.png)` line in
the same file names the output. Uses the repo's Pele renderer + build_epub's
flatten_svg_vars (white background), then cairosvg -> PNG (~1200px wide).
"""

import logging
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent  # run: python3 tools/render_examples.py
sys.path.insert(0, str(REPO / "scripts"))

import cairosvg
from build_epub import flatten_svg_vars
from pele_renderer import render_diagrams

EX = REPO / "11-visualization" / "examples"
BLOCK = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
IMG = re.compile(r"(?:!\[[^\]]*\]\(|<!-- render: )(images/[^) ]+\.png)")

jobs = []
for md in sorted(EX.glob("*.md")):
    text = md.read_text(encoding="utf-8")
    for m in BLOCK.finditer(text):
        imgs = IMG.findall(text[: m.start()])
        if not imgs:
            sys.exit(f"{md.name}: mermaid block without preceding image")
        jobs.append((md.name, imgs[-1], m.group(1)))

results = render_diagrams([j[2] for j in jobs], logging.getLogger("r"))
seen = {}
for (name, img, src), res in zip(jobs, results):
    if res.error:
        sys.exit(f"{name} -> {img}: {res.error.describe()}")
    if img in seen and seen[img] != src:
        sys.exit(f"{img} used by two different diagrams")
    seen[img] = src
    svg = flatten_svg_vars(res.svg)
    # cairosvg renders nothing with Pele's root style (max-width/height:auto);
    # replace it with plain font attributes (+ CJK fallback for Korean text).
    svg = re.sub(
        r' style="[^"]*"',
        ' font-size="16" font-family="Arial, \'Liberation Sans\', '
        "'Noto Sans CJK KR', sans-serif\"",
        svg,
        count=1,
    )
    w = float(re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ', svg).group(1))
    scale = min(1200 / w, 3.0)
    out = EX / img
    out.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(
        bytestring=svg.encode(),
        write_to=str(out),
        scale=scale,
        background_color="white",
    )
    print(f"{name:40s} -> {img}  (svg {w:.0f}px, x{scale:.2f})")

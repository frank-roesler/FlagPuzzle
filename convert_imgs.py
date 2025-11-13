#!/usr/bin/env python3
from pathlib import Path

try:
    import cairosvg
except Exception:
    raise SystemExit("Install cairosvg first: pip install cairosvg")

SRC = Path("country-flags-main") / "svg"
OUT = Path("country-flags-main") / "png"
OUT.mkdir(parents=True, exist_ok=True)

for svg in sorted(SRC.glob("*.svg")):
    out = OUT / (svg.stem + ".png")
    cairosvg.svg2png(url=str(svg), write_to=str(out), output_height=512)
    print("Converted:", svg.name)

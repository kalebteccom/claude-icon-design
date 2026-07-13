#!/usr/bin/env python3
"""Render a numbered comparison sheet from monochrome concept SVGs."""

from __future__ import annotations

import argparse
import io
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

try:
    import cairosvg
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError as error:
    missing = error.name or "rendering dependency"
    raise SystemExit(
        f"Missing {missing}. Install the packages listed in requirements.txt."
    ) from error

from render_suite import svg_parts


PAGE_WIDTH = 1800
PAGE_MARGIN = 64
HEADER_HEIGHT = 150
FOOTER_HEIGHT = 70
GRID_GAP = 20
TILE_HEIGHT = 300
COLORS = {
    "page": "#EEEDE8",
    "tile": "#FBFAF7",
    "preview": "#F2F1EC",
    "ink": "#171815",
    "muted": "#6B6C66",
    "line": "#D7D6D0",
    "dark": "#202220",
    "paper": "#FFFFFF",
}
STAGE_PREFIX = {"discovery": "D", "refinement": "R"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a numbered icon concept sheet.")
    parser.add_argument("manifest", help="Path to concepts.json")
    parser.add_argument("--output", required=True, help="Destination PNG path")
    return parser.parse_args()


def read_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Manifest not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError("Concept manifest must contain one JSON object")
    return payload


def require_text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Concept manifest requires a non-empty {key!r}")
    return value.strip()


def validate_manifest(path: Path) -> dict[str, Any]:
    payload = read_manifest(path)
    payload["project"] = require_text(payload, "project")
    stage = payload.get("stage")
    if stage not in STAGE_PREFIX:
        raise ValueError("stage must be 'discovery' or 'refinement'")
    round_number = payload.get("round")
    if not isinstance(round_number, int) or round_number < 1:
        raise ValueError("round must be a positive integer")
    count = payload.get("count")
    if not isinstance(count, int) or not 1 <= count <= 40:
        raise ValueError("count must be an integer between 1 and 40")
    concepts = payload.get("concepts")
    if not isinstance(concepts, list) or len(concepts) != count:
        raise ValueError(f"concepts must contain exactly {count} entries")
    parent = payload.get("selected_parent")
    if stage == "discovery" and parent is not None:
        raise ValueError("selected_parent must be null for discovery")
    if stage == "refinement" and (
        not isinstance(parent, str) or not parent.strip()
    ):
        raise ValueError("selected_parent is required for refinement")
    if stage == "refinement":
        parent_match = re.fullmatch(r"([DR])([1-9]\d*)-(\d{2})", parent)
        if parent_match is None or not 1 <= int(parent_match.group(3)) <= 40:
            raise ValueError("selected_parent must be a valid discovery or refinement ID")
        if parent_match.group(1) == "R" and int(parent_match.group(2)) >= round_number:
            raise ValueError("a refinement parent must come from an earlier round")

    root = path.parent.resolve()
    expected_prefix = STAGE_PREFIX[stage]
    normalized: list[dict[str, str]] = []
    for index, raw in enumerate(concepts, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"concept {index} must be an object")
        expected_id = f"{expected_prefix}{round_number}-{index:02d}"
        concept_id = require_text(raw, "id")
        if concept_id != expected_id:
            raise ValueError(f"concept {index} id must be {expected_id!r}")
        filename = require_text(raw, "file")
        if filename != f"{concept_id}.svg":
            raise ValueError(f"concept {concept_id} file must be {concept_id!r} plus .svg")
        relative = Path(filename)
        if relative.is_absolute() or ".." in relative.parts or relative.suffix != ".svg":
            raise ValueError(f"concept {concept_id} file must be a relative .svg path")
        svg_path = (root / relative).resolve()
        if root not in svg_path.parents or not svg_path.is_file():
            raise ValueError(f"concept {concept_id} SVG not found: {filename}")
        svg_parts(svg_path)
        normalized.append(
            {
                "id": concept_id,
                "title": require_text(raw, "title"),
                "territory": require_text(raw, "territory"),
                "note": require_text(raw, "note"),
                "path": str(svg_path),
            }
        )
    payload["concepts"] = normalized
    return payload


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def truncate(draw: ImageDraw.ImageDraw, value: str, typeface: ImageFont.ImageFont, width: int) -> str:
    if draw.textbbox((0, 0), value, font=typeface)[2] <= width:
        return value
    suffix = "…"
    candidate = value
    while candidate and draw.textbbox((0, 0), candidate + suffix, font=typeface)[2] > width:
        candidate = candidate[:-1]
    return candidate.rstrip() + suffix


def render_svg(path: Path, size: int, color: str) -> Image.Image:
    raw = path.read_text(encoding="utf-8").replace("currentColor", color)
    png = cairosvg.svg2png(
        bytestring=raw.encode("utf-8"),
        output_width=size,
        output_height=size,
    )
    return Image.open(io.BytesIO(png)).convert("RGBA")


def paste_center(canvas: Image.Image, icon: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    x = x0 + (x1 - x0 - icon.width) // 2
    y = y0 + (y1 - y0 - icon.height) // 2
    canvas.paste(icon, (x, y), icon)


def render(manifest_path: Path, output_path: Path) -> Path:
    manifest_path = manifest_path.resolve()
    manifest = validate_manifest(manifest_path)
    concepts = manifest["concepts"]
    columns = 5 if len(concepts) > 8 else 4
    rows = math.ceil(len(concepts) / columns)
    tile_width = (
        PAGE_WIDTH - 2 * PAGE_MARGIN - (columns - 1) * GRID_GAP
    ) // columns
    page_height = (
        HEADER_HEIGHT + rows * TILE_HEIGHT + (rows - 1) * GRID_GAP + FOOTER_HEIGHT
    )
    canvas = Image.new("RGB", (PAGE_WIDTH, page_height), COLORS["page"])
    draw = ImageDraw.Draw(canvas)
    title_font = font(42, bold=True)
    meta_font = font(20)
    id_font = font(24, bold=True)
    name_font = font(18, bold=True)
    small_font = font(14)

    stage_label = manifest["stage"].capitalize()
    draw.text((PAGE_MARGIN, 44), manifest["project"], fill=COLORS["ink"], font=title_font)
    header_meta = f"{stage_label} · round {manifest['round']} · {len(concepts)} directions"
    if manifest["stage"] == "refinement":
        header_meta += f" · from {manifest['selected_parent']}"
    draw.text((PAGE_MARGIN, 102), header_meta, fill=COLORS["muted"], font=meta_font)

    for index, concept in enumerate(concepts):
        row, column = divmod(index, columns)
        x = PAGE_MARGIN + column * (tile_width + GRID_GAP)
        y = HEADER_HEIGHT + row * (TILE_HEIGHT + GRID_GAP)
        draw.rounded_rectangle(
            (x, y, x + tile_width, y + TILE_HEIGHT),
            radius=18,
            fill=COLORS["tile"],
            outline=COLORS["line"],
            width=1,
        )

        main_box = (x + 18, y + 18, x + 190, y + 190)
        draw.rounded_rectangle(main_box, radius=12, fill=COLORS["preview"])
        icon_path = Path(concept["path"])
        paste_center(canvas, render_svg(icon_path, 126, COLORS["ink"]), main_box)

        dark_box = (x + tile_width - 108, y + 18, x + tile_width - 18, y + 108)
        draw.rounded_rectangle(dark_box, radius=12, fill=COLORS["dark"])
        paste_center(canvas, render_svg(icon_path, 56, COLORS["paper"]), dark_box)

        draw.text((x + tile_width - 108, y + 128), "native", fill=COLORS["muted"], font=small_font)
        icon_24 = render_svg(icon_path, 24, COLORS["ink"])
        icon_16 = render_svg(icon_path, 16, COLORS["ink"])
        canvas.paste(icon_24, (x + tile_width - 108, y + 153), icon_24)
        canvas.paste(icon_16, (x + tile_width - 66, y + 157), icon_16)

        draw.text((x + 18, y + 210), concept["id"], fill=COLORS["ink"], font=id_font)
        max_text = tile_width - 36
        name = truncate(draw, concept["title"], name_font, max_text)
        territory = truncate(draw, concept["territory"], small_font, max_text)
        draw.text((x + 18, y + 244), name, fill=COLORS["ink"], font=name_font)
        draw.text((x + 18, y + 270), territory, fill=COLORS["muted"], font=small_font)

    example_number = min(7 if manifest["stage"] == "discovery" else 4, len(concepts))
    example_id = f"{STAGE_PREFIX[manifest['stage']]}{manifest['round']}-{example_number:02d}"
    if manifest["stage"] == "discovery":
        instruction = f"Select with: Refine {example_id} · Continue discovery from {example_id} · Change the brief"
    else:
        instruction = f"Select with: Finalize {example_id} · Refine {example_id} further · Back to discovery"
    draw.text(
        (PAGE_MARGIN, page_height - 43),
        instruction,
        fill=COLORS["muted"],
        font=meta_font,
    )

    output_path = output_path.resolve()
    if output_path.suffix.lower() != ".png":
        raise ValueError("Output path must end in .png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=False)
    return output_path


def main() -> None:
    args = parse_args()
    output = render(Path(args.manifest), Path(args.output))
    print(f"Rendered concept sheet: {output}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 - CLI should print one clear error.
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error

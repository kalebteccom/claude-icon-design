#!/usr/bin/env python3
"""Render matching PNG and standalone HTML review sheets for icon rounds."""

from __future__ import annotations

import argparse
import base64
import html
import io
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

_DEPENDENCY_ERROR: ModuleNotFoundError | None = None
cairosvg: Any = None
Image: Any = None
ImageDraw: Any = None
ImageFont: Any = None
svg_parts: Any = None
try:
    import cairosvg
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError as error:
    _DEPENDENCY_ERROR = error
else:
    from render_suite import svg_parts


SCHEMA_V2 = "kalebtec.icon-round.v2"
PAGE_WIDTH = 1800
PAGE_MARGIN = 64
HEADER_HEIGHT = 176
FOOTER_HEIGHT = 82
GRID_GAP = 20
GROUP_HEADER_HEIGHT = 64
REFERENCE_HEADER_HEIGHT = 52
REFERENCE_TILE_HEIGHT = 190
CONCEPT_TILE_HEIGHT = 374
COLORS = {
    "page": "#F1F0E4",
    "tile": "#FAFAF5",
    "tile_alt": "#E9E7DC",
    "preview": "#EEEDE5",
    "ink": "#080F11",
    "muted": "#626661",
    "line": "#D6D3C8",
    "line_strong": "#AAA79D",
    "dark": "#080F11",
    "paper": "#FAFAF5",
    "accent": "#8000FF",
    "accent_soft": "#E8D7FF",
}
STAGE_PREFIX = {"discovery": "D", "refinement": "R"}
MODES = {
    "discovery": {"territory", "open"},
    "refinement": {"shortlist", "controlled", "exploratory", "optical"},
}
MODE_LABELS = {
    "territory": "Territory discovery",
    "open": "Open discovery",
    "shortlist": "Shortlist refinement",
    "controlled": "Controlled refinement",
    "exploratory": "Exploratory refinement",
    "optical": "Optical refinement",
}
REFERENCE_ROLES = {"parent", "control", "benchmark"}
ID_PATTERN = re.compile(r"([DR])([1-9]\d*)-(\d{2})")


def ensure_dependencies() -> None:
    if _DEPENDENCY_ERROR is None:
        return
    missing = _DEPENDENCY_ERROR.name or "rendering dependency"
    requirements = Path(__file__).with_name("requirements.txt").resolve()
    raise RuntimeError(
        f"Missing {missing}. Install the bundled rendering dependencies with: "
        f'python3 -m pip install -r "{requirements}"'
    ) from _DEPENDENCY_ERROR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render matching PNG and HTML icon review sheets."
    )
    parser.add_argument("manifest", help="Path to concepts.json")
    parser.add_argument("--output", required=True, help="Destination PNG path")
    parser.add_argument(
        "--html-output",
        help="Destination HTML path; defaults to the PNG path with .html",
    )
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


def optional_text(payload: dict[str, Any], key: str, fallback: str = "") -> str:
    value = payload.get(key, fallback)
    if value is None:
        return fallback
    if not isinstance(value, str):
        raise ValueError(f"{key} must be text")
    return value.strip()


def parse_id(value: str, label: str) -> tuple[str, int, int]:
    match = ID_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError(f"{label} must use an ID such as D1-07 or R2-04")
    number = int(match.group(3))
    if not 1 <= number <= 99:
        raise ValueError(f"{label} number must be between 01 and 99")
    return match.group(1), int(match.group(2)), number


def resolve_svg(
    root: Path,
    filename: str,
    label: str,
    *,
    expected_id: str | None = None,
    allow_id_suffix: bool = False,
    allow_parent_path: bool = False,
) -> Path:
    relative = Path(filename)
    if relative.is_absolute() or relative.suffix.lower() != ".svg":
        raise ValueError(f"{label} file must be a relative .svg path")
    if expected_id is not None:
        matches_id = relative.stem == expected_id or (
            allow_id_suffix and relative.stem.startswith(f"{expected_id}-")
        )
        if not matches_id:
            if allow_id_suffix:
                raise ValueError(
                    f"{label} file name must begin with {expected_id!r} and end in .svg"
                )
            raise ValueError(f"{label} file name must be {expected_id!r} plus .svg")
    path = (root / relative).resolve()
    if not allow_parent_path and root != path.parent and root not in path.parents:
        raise ValueError(f"{label} file must stay inside the round directory")
    if not path.is_file():
        raise ValueError(f"{label} SVG not found: {filename}")
    svg_parts(path)
    return path


def validate_rating(raw: Any, label: str) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError(f"{label} rating must be an object")
    value = raw.get("value")
    out_of = raw.get("out_of", 10)
    attributed_to = raw.get("attributed_to")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{label} rating.value must be numeric")
    if not isinstance(out_of, (int, float)) or isinstance(out_of, bool) or out_of <= 0:
        raise ValueError(f"{label} rating.out_of must be positive")
    if value < 0 or value > out_of:
        raise ValueError(f"{label} rating.value must be between 0 and rating.out_of")
    if not isinstance(attributed_to, str) or not attributed_to.strip():
        raise ValueError(
            f"{label} rating.attributed_to is required; omit ratings not supplied by a reviewer"
        )
    return {
        "value": value,
        "out_of": out_of,
        "attributed_to": attributed_to.strip(),
    }


def validate_reference(root: Path, raw: Any, index: int) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError(f"reference {index} must be an object")
    reference_id = require_text(raw, "id")
    parse_id(reference_id, f"reference {index} id")
    role = raw.get("role")
    if role not in REFERENCE_ROLES:
        raise ValueError(
            f"reference {reference_id} role must be parent, control, or benchmark"
        )
    filename = require_text(raw, "file")
    path = resolve_svg(
        root,
        filename,
        f"reference {reference_id}",
        expected_id=reference_id,
        allow_id_suffix=True,
        allow_parent_path=True,
    )
    return {
        "id": reference_id,
        "title": require_text(raw, "title"),
        "file": filename,
        "path": str(path),
        "role": role,
        "note": optional_text(raw, "note"),
        "rating": validate_rating(raw.get("rating"), f"reference {reference_id}"),
    }


def validate_v2(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    payload["project"] = require_text(payload, "project")
    stage = payload.get("stage")
    if stage not in STAGE_PREFIX:
        raise ValueError("stage must be 'discovery' or 'refinement'")
    round_number = payload.get("round")
    if not isinstance(round_number, int) or round_number < 1:
        raise ValueError("round must be a positive integer")
    mode = payload.get("mode")
    if mode not in MODES[stage]:
        allowed = ", ".join(sorted(MODES[stage]))
        raise ValueError(f"mode for {stage} must be one of: {allowed}")
    count = payload.get("count")
    if not isinstance(count, int) or not 1 <= count <= 40:
        raise ValueError("count must be an integer between 1 and 40")
    concepts = payload.get("concepts")
    if not isinstance(concepts, list) or len(concepts) != count:
        raise ValueError(f"concepts must contain exactly {count} entries")

    root = path.parent.resolve()
    references_raw = payload.get("references", [])
    if not isinstance(references_raw, list):
        raise ValueError("references must be an array")
    references = [
        validate_reference(root, raw, index)
        for index, raw in enumerate(references_raw, start=1)
    ]
    reference_ids = [reference["id"] for reference in references]
    if len(reference_ids) != len(set(reference_ids)):
        raise ValueError("reference IDs must be unique")
    if stage == "discovery" and references:
        raise ValueError("discovery rounds must not include references")
    if stage == "refinement" and not any(
        reference["role"] == "parent" for reference in references
    ):
        raise ValueError("v2 refinement rounds require at least one parent reference")

    retired = payload.get("retired", [])
    if not isinstance(retired, list) or any(
        not isinstance(item, str) for item in retired
    ):
        raise ValueError("retired must be an array of concept IDs")
    retired_parts = {item: parse_id(item, "retired concept") for item in retired}
    if len(retired) != len(set(retired)):
        raise ValueError("retired concept IDs must be unique")

    normalized: list[dict[str, Any]] = []
    concept_ids: list[str] = []
    expected_prefix = STAGE_PREFIX[stage]
    first_number: int | None = None
    for index, raw in enumerate(concepts, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"concept {index} must be an object")
        concept_id = require_text(raw, "id")
        prefix, concept_round, concept_number = parse_id(
            concept_id, f"concept {index} id"
        )
        if prefix != expected_prefix or concept_round != round_number:
            raise ValueError(
                f"concept {concept_id} must use prefix {expected_prefix}{round_number}-"
            )
        if first_number is None:
            first_number = concept_number
        expected_number = first_number + index - 1
        expected_id = f"{expected_prefix}{round_number}-{expected_number:02d}"
        if concept_id != expected_id:
            raise ValueError(f"concept {index} id must be {expected_id!r}")
        concept_ids.append(concept_id)
        filename = require_text(raw, "file")
        svg_path = resolve_svg(
            root,
            filename,
            f"concept {concept_id}",
            expected_id=concept_id,
        )

        parent = optional_text(raw, "parent")
        if stage == "refinement":
            if not parent:
                raise ValueError(f"concept {concept_id} requires a parent")
            parent_prefix, parent_round, _ = parse_id(
                parent, f"concept {concept_id} parent"
            )
            if parent_prefix == "R" and parent_round >= round_number:
                raise ValueError(
                    f"concept {concept_id} parent must come from an earlier refinement round"
                )
            if parent not in reference_ids:
                raise ValueError(
                    f"concept {concept_id} parent {parent!r} must appear in references"
                )
            parent_reference = next(
                reference for reference in references if reference["id"] == parent
            )
            if parent_reference["role"] != "parent":
                raise ValueError(
                    f"concept {concept_id} parent {parent!r} must use reference role 'parent'"
                )
        elif parent:
            raise ValueError(f"discovery concept {concept_id} must not have a parent")

        territory = optional_text(raw, "territory")
        if stage == "discovery" and not territory:
            raise ValueError(f"discovery concept {concept_id} requires a territory")
        move = optional_text(raw, "move") or optional_text(raw, "note")
        if not move:
            raise ValueError(f"concept {concept_id} requires a move")
        if "rating" in raw:
            raise ValueError(
                f"concept {concept_id} rating is not allowed; carry a reviewer-rated "
                "direction into the next round as a reference"
            )
        normalized.append(
            {
                "id": concept_id,
                "title": require_text(raw, "title"),
                "file": filename,
                "path": str(svg_path),
                "territory": territory or "Focused refinement",
                "move": move,
                "note": optional_text(raw, "note"),
                "watch": optional_text(raw, "watch"),
                "risk": optional_text(raw, "risk"),
                "parent": parent,
            }
        )

    duplicate_reference_ids = sorted(set(reference_ids) & set(concept_ids))
    if duplicate_reference_ids:
        raise ValueError(
            "reference and concept IDs must not overlap: "
            + ", ".join(duplicate_reference_ids)
        )
    retired_overlaps = sorted(set(retired) & (set(reference_ids) | set(concept_ids)))
    if retired_overlaps:
        raise ValueError(
            "retired IDs must not appear as references or concepts: "
            + ", ".join(retired_overlaps)
        )
    same_round_retired = {
        number
        for prefix, item_round, number in retired_parts.values()
        if prefix == expected_prefix and item_round == round_number
    }
    if first_number is not None:
        expected_prior = set(range(1, first_number))
        missing_prior = sorted(expected_prior - same_round_retired)
        if missing_prior:
            missing = ", ".join(
                f"{expected_prefix}{round_number}-{number:02d}"
                for number in missing_prior
            )
            raise ValueError(
                f"concept numbering starts at {first_number:02d}; "
                f"list prior IDs in retired: {missing}"
            )
        invalid_retired = sorted(
            number for number in same_round_retired if number >= first_number
        )
        if invalid_retired:
            invalid = ", ".join(
                f"{expected_prefix}{round_number}-{number:02d}"
                for number in invalid_retired
            )
            raise ValueError(
                f"same-round retired IDs must come before current concepts: {invalid}"
            )

    review = payload.get("review", {})
    if not isinstance(review, dict):
        raise ValueError("review must be an object")
    selection_max = review.get("selection_max", 5 if stage == "discovery" else 3)
    if not isinstance(selection_max, int) or not 1 <= selection_max <= 8:
        raise ValueError("review.selection_max must be an integer between 1 and 8")

    return {
        "schema": SCHEMA_V2,
        "project": payload["project"],
        "stage": stage,
        "round": round_number,
        "mode": mode,
        "count": count,
        "wordmark": optional_text(payload, "wordmark", payload["project"]),
        "subtitle": optional_text(payload, "subtitle"),
        "references": references,
        "retired": retired,
        "review": {"selection_max": selection_max},
        "concepts": normalized,
        "legacy": False,
    }


def validate_legacy(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
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
    if stage == "refinement":
        if not isinstance(parent, str) or not parent.strip():
            raise ValueError("selected_parent is required for refinement")
        try:
            parse_id(parent, "selected_parent")
        except ValueError as error:
            raise ValueError(
                "selected_parent must be a valid discovery or refinement ID"
            ) from error

    root = path.parent.resolve()
    normalized: list[dict[str, Any]] = []
    expected_prefix = STAGE_PREFIX[stage]
    for index, raw in enumerate(concepts, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"concept {index} must be an object")
        expected_id = f"{expected_prefix}{round_number}-{index:02d}"
        concept_id = require_text(raw, "id")
        if concept_id != expected_id:
            raise ValueError(f"concept {index} id must be {expected_id!r}")
        filename = require_text(raw, "file")
        svg_path = resolve_svg(
            root,
            filename,
            f"concept {concept_id}",
            expected_id=concept_id,
        )
        normalized.append(
            {
                "id": concept_id,
                "title": require_text(raw, "title"),
                "file": filename,
                "path": str(svg_path),
                "territory": require_text(raw, "territory"),
                "move": require_text(raw, "note"),
                "note": require_text(raw, "note"),
                "watch": "",
                "risk": "",
                "parent": parent.strip() if isinstance(parent, str) else "",
            }
        )
    return {
        "schema": "legacy",
        "project": payload["project"],
        "stage": stage,
        "round": round_number,
        "mode": "territory" if stage == "discovery" else "controlled",
        "count": count,
        "wordmark": payload["project"],
        "subtitle": "",
        "references": [],
        "retired": [],
        "review": {"selection_max": 5 if stage == "discovery" else 3},
        "concepts": normalized,
        "legacy": True,
    }


def validate_manifest(path: Path) -> dict[str, Any]:
    ensure_dependencies()
    payload = read_manifest(path)
    schema = payload.get("schema")
    if schema in (None, "kalebtec.icon-round.v1"):
        return validate_legacy(path, payload)
    if schema != SCHEMA_V2:
        raise ValueError(f"Unsupported round schema: {schema}")
    return validate_v2(path, payload)


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def truncate(
    draw: ImageDraw.ImageDraw,
    value: str,
    typeface: ImageFont.ImageFont,
    width: int,
) -> str:
    if draw.textbbox((0, 0), value, font=typeface)[2] <= width:
        return value
    suffix = "…"
    candidate = value
    while (
        candidate
        and draw.textbbox((0, 0), candidate + suffix, font=typeface)[2] > width
    ):
        candidate = candidate[:-1]
    return candidate.rstrip() + suffix


def wrapped_lines(
    draw: ImageDraw.ImageDraw,
    value: str,
    typeface: ImageFont.ImageFont,
    width: int,
    max_lines: int,
) -> list[str]:
    words = value.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=typeface)[2] > width:
            lines.append(current)
            current = word
            if len(lines) == max_lines:
                break
        else:
            current = candidate
    if len(lines) < max_lines and current:
        lines.append(current)
    consumed = " ".join(lines)
    if len(consumed) < len(value.strip()) and lines:
        lines[-1] = truncate(draw, lines[-1] + "…", typeface, width)
    return lines[:max_lines]


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    value: str,
    typeface: ImageFont.ImageFont,
    fill: str,
    width: int,
    max_lines: int,
    line_height: int,
) -> None:
    x, y = position
    for line in wrapped_lines(draw, value, typeface, width, max_lines):
        draw.text((x, y), line, fill=fill, font=typeface)
        y += line_height


def render_svg(path: Path, size: int, color: str) -> Image.Image:
    raw = path.read_text(encoding="utf-8").replace("currentColor", color)
    png = cairosvg.svg2png(
        bytestring=raw.encode("utf-8"),
        output_width=size,
        output_height=size,
    )
    return Image.open(io.BytesIO(png)).convert("RGBA")


def paste_center(
    canvas: Image.Image,
    icon: Image.Image,
    box: tuple[int, int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    x = x0 + (x1 - x0 - icon.width) // 2
    y = y0 + (y1 - y0 - icon.height) // 2
    canvas.paste(icon, (x, y), icon)


def concept_groups(manifest: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    concepts = manifest["concepts"]
    key = "territory" if manifest["stage"] == "discovery" else "parent"
    grouped: dict[str, list[dict[str, Any]]] = {}
    for concept in concepts:
        group = concept[key] or "Directions"
        grouped.setdefault(group, []).append(concept)
    if manifest["stage"] == "discovery" and (
        len(grouped) > 8 or all(len(items) == 1 for items in grouped.values())
    ):
        return [("Directions", concepts)]
    return list(grouped.items())


def calculate_height(manifest: dict[str, Any]) -> int:
    height = HEADER_HEIGHT
    references = manifest["references"]
    if references:
        rows = math.ceil(len(references) / 3)
        height += REFERENCE_HEADER_HEIGHT + rows * REFERENCE_TILE_HEIGHT
        height += max(0, rows - 1) * GRID_GAP + 28
    for _, concepts in concept_groups(manifest):
        rows = math.ceil(len(concepts) / 4)
        height += GROUP_HEADER_HEIGHT + rows * CONCEPT_TILE_HEIGHT
        height += max(0, rows - 1) * GRID_GAP + 28
    return height + FOOTER_HEIGHT


def draw_reference_card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    reference: dict[str, Any],
    box: tuple[int, int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    border = (
        COLORS["accent"]
        if reference["role"] in {"parent", "control"}
        else COLORS["line_strong"]
    )
    draw.rounded_rectangle(
        box,
        radius=17,
        fill=COLORS["tile_alt"],
        outline=border,
        width=3 if reference["role"] in {"parent", "control"} else 1,
    )
    preview = (x0 + 16, y0 + 16, x0 + 160, y1 - 16)
    draw.rounded_rectangle(preview, radius=12, fill=COLORS["tile"])
    paste_center(
        canvas,
        render_svg(Path(reference["path"]), 104, COLORS["ink"]),
        preview,
    )
    info_x = x0 + 178
    width = x1 - info_x - 18
    draw.text(
        (info_x, y0 + 18),
        f"{reference['role'].upper()} / {reference['id']}",
        fill=COLORS["accent"],
        font=font(15, bold=True),
    )
    draw.text(
        (info_x, y0 + 47),
        truncate(draw, reference["title"], font(23, bold=True), width),
        fill=COLORS["ink"],
        font=font(23, bold=True),
    )
    note = reference["note"] or "Keep this unchanged as a visible comparison point."
    draw_wrapped(
        draw,
        (info_x, y0 + 82),
        note,
        font(14),
        COLORS["muted"],
        width,
        3,
        19,
    )
    rating = reference["rating"]
    if rating:
        label = f"{rating['value']:g}/{rating['out_of']:g} · {rating['attributed_to']}"
        draw.text(
            (info_x, y1 - 31),
            label,
            fill=COLORS["accent"],
            font=font(14, bold=True),
        )


def draw_context_strip(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    path: Path,
    x: int,
    y: int,
) -> None:
    specs = [
        ("16", 16, COLORS["tile"], COLORS["ink"]),
        ("24", 24, COLORS["tile"], COLORS["ink"]),
        ("32", 32, COLORS["tile"], COLORS["ink"]),
        ("DARK", 27, COLORS["dark"], COLORS["paper"]),
        ("APP", 27, COLORS["accent"], COLORS["paper"]),
    ]
    for index, (label, size, background, color) in enumerate(specs):
        left = x + index * 59
        box = (left, y, left + 49, y + 49)
        draw.rounded_rectangle(box, radius=10, fill=background, outline=COLORS["line"])
        paste_center(canvas, render_svg(path, size, color), box)
        draw.text(
            (left + 24, y + 54),
            label,
            anchor="ma",
            fill=COLORS["muted"],
            font=font(10, bold=True),
        )


def draw_concept_card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    concept: dict[str, Any],
    wordmark: str,
    box: tuple[int, int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        box,
        radius=18,
        fill=COLORS["tile"],
        outline=COLORS["line"],
        width=1,
    )
    width = x1 - x0
    draw.text(
        (x0 + 17, y0 + 16),
        concept["id"],
        fill=COLORS["accent"],
        font=font(15, bold=True),
    )
    draw.text(
        (x0 + 17, y0 + 39),
        truncate(draw, concept["title"], font(23, bold=True), width - 34),
        fill=COLORS["ink"],
        font=font(23, bold=True),
    )
    preview = (x0 + 17, y0 + 76, x0 + 169, y0 + 220)
    draw.rounded_rectangle(preview, radius=12, fill=COLORS["preview"])
    path = Path(concept["path"])
    paste_center(canvas, render_svg(path, 112, COLORS["ink"]), preview)

    info_x = x0 + 185
    info_width = x1 - info_x - 16
    draw.text(
        (info_x, y0 + 78),
        "DELIBERATE MOVE",
        fill=COLORS["muted"],
        font=font(11, bold=True),
    )
    draw_wrapped(
        draw,
        (info_x, y0 + 99),
        concept["move"],
        font(14),
        COLORS["ink"],
        info_width,
        4,
        19,
    )
    caution_parts = []
    if concept["watch"]:
        caution_parts.append(f"Watch — {concept['watch']}")
    if concept["risk"]:
        caution_parts.append(f"Risk — {concept['risk']}")
    if caution_parts:
        caution_label = (
            "WATCH / RISK"
            if len(caution_parts) > 1
            else caution_parts[0].split(" —", 1)[0].upper()
        )
        draw.text(
            (info_x, y0 + 180),
            caution_label,
            fill=COLORS["muted"],
            font=font(11, bold=True),
        )
        draw_wrapped(
            draw,
            (info_x, y0 + 199),
            " ".join(caution_parts),
            font(12),
            COLORS["muted"],
            info_width,
            3,
            17,
        )

    draw.line(
        (x0 + 17, y0 + 243, x1 - 17, y0 + 243),
        fill=COLORS["line"],
        width=1,
    )
    icon = render_svg(path, 25, COLORS["ink"])
    canvas.paste(icon, (x0 + 18, y0 + 255), icon)
    draw.text(
        (x0 + 54, y0 + 255),
        truncate(draw, wordmark, font(20, bold=True), width - 72),
        fill=COLORS["ink"],
        font=font(20, bold=True),
    )
    draw.text(
        (x0 + 17, y0 + 292),
        "NATIVE SIZE / CONTEXT",
        fill=COLORS["muted"],
        font=font(10, bold=True),
    )
    draw_context_strip(canvas, draw, path, x0 + 17, y0 + 309)


def render_png(manifest: dict[str, Any], output_path: Path) -> Path:
    page_height = calculate_height(manifest)
    canvas = Image.new("RGB", (PAGE_WIDTH, page_height), COLORS["page"])
    draw = ImageDraw.Draw(canvas)
    stage_label = manifest["stage"].capitalize()
    title = manifest["project"]
    draw.text(
        (PAGE_MARGIN, 40),
        title,
        fill=COLORS["ink"],
        font=font(46, bold=True),
    )
    meta = (
        f"{stage_label} / Round {manifest['round']} / "
        f"{MODE_LABELS[manifest['mode']]} / {manifest['count']} directions"
    )
    draw.text(
        (PAGE_MARGIN, 101),
        meta,
        fill=COLORS["muted"],
        font=font(20),
    )
    subtitle = manifest["subtitle"] or (
        "Choose the idea and silhouette before polishing geometry."
        if manifest["stage"] == "discovery"
        else "The parent remains selectable; every candidate must clear that bar."
    )
    draw.text(
        (PAGE_MARGIN, 134),
        subtitle,
        fill=COLORS["muted"],
        font=font(16),
    )
    draw.text(
        (PAGE_WIDTH - PAGE_MARGIN, 48),
        "STANDARD PNG + HTML REVIEW",
        anchor="ra",
        fill=COLORS["accent"],
        font=font(14, bold=True),
    )

    y = HEADER_HEIGHT
    references = manifest["references"]
    if references:
        draw.text(
            (PAGE_MARGIN, y + 4),
            "References and benchmarks",
            fill=COLORS["ink"],
            font=font(24, bold=True),
        )
        draw.text(
            (PAGE_WIDTH - PAGE_MARGIN, y + 10),
            "References stay unchanged and remain selectable",
            anchor="ra",
            fill=COLORS["muted"],
            font=font(14),
        )
        y += REFERENCE_HEADER_HEIGHT
        columns = 3
        tile_width = (
            PAGE_WIDTH - 2 * PAGE_MARGIN - (columns - 1) * GRID_GAP
        ) // columns
        for index, reference in enumerate(references):
            row, column = divmod(index, columns)
            x = PAGE_MARGIN + column * (tile_width + GRID_GAP)
            card_y = y + row * (REFERENCE_TILE_HEIGHT + GRID_GAP)
            draw_reference_card(
                canvas,
                draw,
                reference,
                (x, card_y, x + tile_width, card_y + REFERENCE_TILE_HEIGHT),
            )
        rows = math.ceil(len(references) / columns)
        y += rows * REFERENCE_TILE_HEIGHT + max(0, rows - 1) * GRID_GAP + 28

    tile_width = (PAGE_WIDTH - 2 * PAGE_MARGIN - 3 * GRID_GAP) // 4
    reference_titles = {reference["id"]: reference["title"] for reference in references}
    groups = concept_groups(manifest)
    for group_index, (group_name, concepts) in enumerate(groups, start=1):
        if manifest["stage"] == "discovery":
            heading = group_name
            detail = (
                f"Territory {group_index:02d} · {len(concepts)} distinct constructions"
            )
        else:
            parent_title = reference_titles.get(group_name, "Selected parent")
            heading = (
                f"From {group_name} · {parent_title}" if group_name else parent_title
            )
            detail = f"{len(concepts)} {MODE_LABELS[manifest['mode']].lower()} moves"
        draw.text(
            (PAGE_MARGIN, y + 3),
            heading,
            fill=COLORS["ink"],
            font=font(25, bold=True),
        )
        draw.text(
            (PAGE_WIDTH - PAGE_MARGIN, y + 11),
            detail,
            anchor="ra",
            fill=COLORS["muted"],
            font=font(14),
        )
        y += GROUP_HEADER_HEIGHT
        for index, concept in enumerate(concepts):
            row, column = divmod(index, 4)
            x = PAGE_MARGIN + column * (tile_width + GRID_GAP)
            card_y = y + row * (CONCEPT_TILE_HEIGHT + GRID_GAP)
            draw_concept_card(
                canvas,
                draw,
                concept,
                manifest["wordmark"],
                (x, card_y, x + tile_width, card_y + CONCEPT_TILE_HEIGHT),
            )
        rows = math.ceil(len(concepts) / 4)
        y += rows * CONCEPT_TILE_HEIGHT + max(0, rows - 1) * GRID_GAP + 28

    instruction = (
        "Select 3–5 memorable IDs, then refine one or a deliberate shortlist."
        if manifest["stage"] == "discovery"
        else "The parent may win. Finalize one ID, refine further, or return to discovery."
    )
    if manifest["retired"]:
        instruction += " Retired: " + ", ".join(manifest["retired"]) + "."
    draw.text(
        (PAGE_MARGIN, page_height - 48),
        instruction,
        fill=COLORS["muted"],
        font=font(17),
    )
    draw.text(
        (PAGE_WIDTH - PAGE_MARGIN, page_height - 48),
        SCHEMA_V2,
        anchor="ra",
        fill=COLORS["muted"],
        font=font(13, bold=True),
    )

    output_path = output_path.resolve()
    if output_path.suffix.lower() != ".png":
        raise ValueError("Output path must end in .png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=False)
    return output_path


def svg_data_uri(path: Path, color: str) -> str:
    raw = path.read_text(encoding="utf-8").replace("currentColor", color)
    encoded = base64.b64encode(raw.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def html_contexts(path: Path) -> str:
    dark = svg_data_uri(path, COLORS["paper"])
    ink = svg_data_uri(path, COLORS["ink"])
    items = []
    for label, size, source, class_name in (
        ("16", 16, ink, "light"),
        ("24", 24, ink, "light"),
        ("32", 32, ink, "light"),
        ("dark", 27, dark, "dark"),
        ("app", 27, dark, "app"),
    ):
        items.append(
            f'<span class="context {class_name}"><span class="context-frame">'
            f'<img src="{source}" width="{size}" height="{size}" alt="">'
            f"</span><small>{label}</small></span>"
        )
    return "".join(items)


def html_reference_card(reference: dict[str, Any]) -> str:
    path = Path(reference["path"])
    rating = reference["rating"]
    rating_html = ""
    if rating:
        rating_html = (
            '<span class="rating">'
            f"{rating['value']:g}/{rating['out_of']:g} · "
            f"{html.escape(rating['attributed_to'])}</span>"
        )
    note = reference["note"] or "Keep unchanged as a visible comparison point."
    return (
        f'<label class="reference-card selectable {reference["role"]}" '
        f'data-selectable data-id="{html.escape(reference["id"])}">'
        '<input type="checkbox" aria-label="Select this reference">'
        '<span class="selection-order" aria-hidden="true"></span>'
        '<span class="reference-preview">'
        f'<img src="{svg_data_uri(path, COLORS["ink"])}" alt="">'
        '</span><span class="reference-copy">'
        f"<small>{html.escape(reference['role'].upper())} / {html.escape(reference['id'])}</small>"
        f"<strong>{html.escape(reference['title'])}</strong>"
        f"<span>{html.escape(note)}</span>{rating_html}</span></label>"
    )


def html_concept_card(concept: dict[str, Any], wordmark: str) -> str:
    path = Path(concept["path"])
    ink = svg_data_uri(path, COLORS["ink"])
    caution_html = ""
    if concept["watch"]:
        caution_html += (
            f'<p class="watch"><small>Watch</small>{html.escape(concept["watch"])}</p>'
        )
    if concept["risk"]:
        caution_html += (
            f'<p class="risk"><small>Risk</small>{html.escape(concept["risk"])}</p>'
        )
    return (
        f'<label class="concept-card selectable" data-selectable data-id="{html.escape(concept["id"])}">'
        '<input type="checkbox" aria-label="Select this direction">'
        '<span class="selection-order" aria-hidden="true"></span>'
        f'<small class="concept-id">{html.escape(concept["id"])}</small>'
        f"<h3>{html.escape(concept['title'])}</h3>"
        '<div class="concept-main">'
        f'<span class="large-preview"><img src="{ink}" alt=""></span>'
        '<div class="concept-copy"><p><small>Deliberate move</small>'
        f"{html.escape(concept['move'])}</p>{caution_html}</div></div>"
        '<div class="wordmark"><img src="'
        f'{ink}" alt=""><strong>{html.escape(wordmark)}</strong></div>'
        f'<div class="contexts">{html_contexts(path)}</div></label>'
    )


HTML_STYLE = """
<style>
:root { color-scheme: light; font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; --page:#F1F0E4; --tile:#FAFAF5; --tile-alt:#E9E7DC; --preview:#EEEDE5; --ink:#080F11; --muted:#626661; --line:#D6D3C8; --accent:#8000FF; --accent-soft:#E8D7FF; }
* { box-sizing:border-box; }
body { min-width:320px; margin:0; background:var(--page); color:var(--ink); line-height:1.45; }
button,input,textarea { font:inherit; }
main { width:min(1480px,100%); margin:0 auto; padding:52px 28px 180px; }
.page-head { display:grid; gap:12px; padding-bottom:36px; border-bottom:1px solid var(--line); }
.eyebrow,.concept-id,.reference-copy>small,.concept-copy small,.watch small,.risk small,.context small { color:var(--accent); font-size:.67rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }
h1 { max-width:1050px; margin:0; font-size:clamp(2.5rem,6vw,5.4rem); font-weight:590; letter-spacing:-.06em; line-height:.96; }
.meta,.subtitle,.section-head p { margin:0; color:var(--muted); }
.meta { font-size:.86rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; }
.subtitle { max-width:760px; }
.reference-section,.concept-section { margin-top:38px; }
.section-head { display:flex; align-items:end; justify-content:space-between; gap:24px; margin-bottom:14px; }
.section-head h2 { margin:0; font-size:1.3rem; letter-spacing:-.025em; }
.section-head p { font-size:.78rem; }
.reference-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }
.concept-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; }
.reference-card,.concept-card { position:relative; display:grid; border:1px solid var(--line); border-radius:17px; background:var(--tile); cursor:pointer; }
.reference-card { grid-template-columns:130px minmax(0,1fr); gap:16px; min-height:170px; padding:15px; background:var(--tile-alt); }
.reference-card.parent,.reference-card.control { border-width:2px; border-color:var(--accent); }
.reference-preview,.large-preview { display:grid; place-items:center; border-radius:12px; background:var(--tile); }
.reference-preview img { width:92px; height:92px; }
.reference-copy { display:flex; min-width:0; flex-direction:column; justify-content:center; gap:5px; }
.reference-copy strong { font-size:1.15rem; }
.reference-copy>span:not(.rating) { color:var(--muted); font-size:.78rem; }
.rating { color:var(--accent); font-size:.75rem; font-weight:750; }
.concept-card { padding:16px; }
.concept-card h3 { margin:3px 0 14px; font-size:1.1rem; letter-spacing:-.025em; }
.concept-main { display:grid; grid-template-columns:140px minmax(0,1fr); gap:14px; min-height:142px; }
.large-preview { background:var(--preview); }
.large-preview img { width:106px; height:106px; }
.concept-copy p { margin:0 0 11px; font-size:.78rem; }
.concept-copy small,.watch small,.risk small { display:block; margin-bottom:4px; color:var(--muted); }
.watch,.risk { color:var(--muted); }
.wordmark { display:flex; align-items:center; gap:9px; margin-top:14px; padding-top:12px; border-top:1px solid var(--line); }
.wordmark img { width:25px; height:25px; }
.wordmark strong { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.contexts { display:flex; gap:7px; margin-top:13px; }
.context { display:grid; gap:4px; justify-items:center; }
.context-frame { display:grid; width:42px; height:42px; place-items:center; border:1px solid var(--line); border-radius:9px; background:var(--tile); }
.context.dark .context-frame { background:#080F11; }
.context.app .context-frame { background:var(--accent); }
.context small { color:var(--muted); font-size:.53rem; }
.selectable>input { position:absolute; width:1px; height:1px; opacity:0; }
.selectable:hover { border-color:var(--accent); }
.selectable:has(input:focus-visible) { outline:3px solid #2563EB; outline-offset:3px; }
.selectable:has(input:checked) { border-color:var(--accent); box-shadow:inset 0 0 0 2px var(--accent); background:color-mix(in srgb,var(--accent-soft) 42%,var(--tile)); }
.selection-order { position:absolute; top:10px; right:10px; display:none; width:28px; height:28px; place-items:center; border-radius:50%; background:var(--accent); color:white; font-size:.72rem; font-weight:800; }
.selectable:has(input:checked) .selection-order { display:grid; }
.review-bar { position:fixed; z-index:20; right:18px; bottom:18px; left:18px; display:grid; grid-template-columns:minmax(180px,.7fr) minmax(260px,1.5fr) auto; gap:12px; align-items:end; max-width:1180px; margin:auto; padding:14px; border:1px solid var(--line); border-radius:16px; background:rgba(250,250,245,.96); box-shadow:0 18px 60px rgba(8,15,17,.18); backdrop-filter:blur(14px); }
.review-field { display:grid; gap:5px; color:var(--muted); font-size:.68rem; font-weight:750; text-transform:uppercase; letter-spacing:.06em; }
.review-field input,.review-field textarea,.review-output { width:100%; border:1px solid var(--line); border-radius:9px; background:white; color:var(--ink); }
.review-field input { min-height:40px; padding:0 10px; }
.review-field textarea { min-height:58px; padding:8px 10px; resize:vertical; }
.review-actions { display:flex; flex-wrap:wrap; gap:7px; justify-content:end; }
.review-actions button { min-height:40px; padding:0 12px; border:1px solid var(--line); border-radius:9px; background:white; color:var(--ink); cursor:pointer; font-size:.75rem; font-weight:750; }
.review-actions button.primary { border-color:var(--accent); background:var(--accent); color:white; }
.review-status { grid-column:1/-1; display:flex; justify-content:space-between; gap:10px; color:var(--muted); font-size:.7rem; }
.review-output { grid-column:1/-1; min-height:74px; padding:9px 10px; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.68rem; }
@media (max-width:1120px) { .concept-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } .reference-grid { grid-template-columns:1fr; } }
@media (max-width:760px) { main { padding:30px 14px 300px; } .concept-grid { grid-template-columns:1fr; } .section-head { display:grid; gap:3px; } .review-bar { grid-template-columns:1fr; } .review-actions { justify-content:stretch; } .review-actions button { flex:1; } .concept-main { grid-template-columns:110px minmax(0,1fr); } .contexts { overflow-x:auto; } }
</style>
"""


HTML_SCRIPT = """
<script>
(() => {
  const stage = __STAGE__;
  const max = __MAX__;
  const selected = [];
  const cards = [...document.querySelectorAll('[data-selectable]')];
  const count = document.querySelector('#selection-count');
  const status = document.querySelector('#review-message');
  const output = document.querySelector('#review-output');
  const reviewer = document.querySelector('#reviewer');
  const notes = document.querySelector('#review-notes');

  function refresh() {
    cards.forEach((card) => {
      const index = selected.indexOf(card.dataset.id);
      const input = card.querySelector('input');
      const badge = card.querySelector('.selection-order');
      input.checked = index !== -1;
      badge.textContent = index === -1 ? '' : String(index + 1);
    });
    count.textContent = `${selected.length}/${max} selected`;
  }

  cards.forEach((card) => {
    card.querySelector('input').addEventListener('change', (event) => {
      const id = card.dataset.id;
      const index = selected.indexOf(id);
      if (event.target.checked && index === -1) {
        if (selected.length >= max) {
          event.target.checked = false;
          status.textContent = `Choose no more than ${max}.`;
          return;
        }
        selected.push(id);
      } else if (!event.target.checked && index !== -1) {
        selected.splice(index, 1);
      }
      status.textContent = '';
      refresh();
    });
  });

  function contextSuffix() {
    const parts = [];
    if (reviewer.value.trim()) parts.push(`Reviewer: ${reviewer.value.trim()}.`);
    if (notes.value.trim()) parts.push(`Feedback: ${notes.value.trim()}`);
    return parts.length ? `\n${parts.join('\n')}` : '';
  }

  function request(action) {
    if (!selected.length) {
      status.textContent = 'Select at least one ID first.';
      return '';
    }
    if (action === 'finalize' && selected.length !== 1) {
      status.textContent = 'Choose exactly one ID to finalize.';
      return '';
    }
    let text;
    if (action === 'finalize') {
      text = `Finalize ${selected[0]}. Use that exact geometry as the production parent unless optical correction is required.`;
    } else if (stage === 'discovery' && action === 'refine') {
      text = selected.length === 1
        ? `Refine ${selected[0]}. Keep it visible as the parent control and generate eight focused variants.`
        : `Refine the shortlist ${selected.join(', ')} as a multi-parent shortlist round. Keep every selected source visible in the reference bar and group variants by parent.`;
    } else if (stage === 'discovery') {
      text = `Continue discovery from ${selected.join(', ')} while keeping the new directions genuinely distinct.`;
    } else {
      text = selected.length === 1
        ? `Refine ${selected[0]} further. Keep it visible as the parent control and change one deliberate variable per candidate.`
        : `Continue refinement from ${selected.join(', ')} as fixed references. Group new candidates by parent and keep benchmarks unchanged.`;
    }
    return `${text}\nOutput the standard matching PNG and standalone HTML review sheets, then stop.${contextSuffix()}`;
  }

  async function copy(value) {
    output.value = value;
    try {
      await navigator.clipboard.writeText(value);
      status.textContent = 'Request copied.';
    } catch {
      output.hidden = false;
      output.focus();
      output.select();
      document.execCommand('copy');
      status.textContent = 'Request selected and copied.';
    }
  }

  document.querySelectorAll('[data-action]').forEach((button) => {
    button.addEventListener('click', () => {
      const value = request(button.dataset.action);
      if (value) copy(value);
    });
  });
  refresh();
})();
</script>
"""


def render_html(manifest: dict[str, Any], output_path: Path) -> Path:
    output_path = output_path.resolve()
    if output_path.suffix.lower() != ".html":
        raise ValueError("HTML output path must end in .html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    stage_label = manifest["stage"].capitalize()
    meta = (
        f"{stage_label} / Round {manifest['round']} / "
        f"{MODE_LABELS[manifest['mode']]} / {manifest['count']} directions"
    )
    subtitle = manifest["subtitle"] or (
        "Choose the idea and silhouette before polishing geometry."
        if manifest["stage"] == "discovery"
        else "The parent remains selectable; every candidate must clear that bar."
    )
    sections: list[str] = []
    if manifest["references"]:
        cards = "".join(html_reference_card(item) for item in manifest["references"])
        sections.append(
            '<section class="reference-section"><div class="section-head">'
            '<div><span class="eyebrow">Comparison bar</span><h2>References and benchmarks</h2></div>'
            "<p>References stay unchanged and remain selectable.</p></div>"
            f'<div class="reference-grid">{cards}</div></section>'
        )
    reference_titles = {
        reference["id"]: reference["title"] for reference in manifest["references"]
    }
    for index, (group_name, concepts) in enumerate(concept_groups(manifest), start=1):
        if manifest["stage"] == "discovery":
            heading = group_name
            detail = f"Territory {index:02d} · {len(concepts)} distinct constructions"
        else:
            parent_title = reference_titles.get(group_name, "Selected parent")
            heading = (
                f"From {group_name} · {parent_title}" if group_name else parent_title
            )
            detail = f"{len(concepts)} {MODE_LABELS[manifest['mode']].lower()} moves"
        cards = "".join(
            html_concept_card(concept, manifest["wordmark"]) for concept in concepts
        )
        sections.append(
            '<section class="concept-section"><div class="section-head">'
            f'<div><span class="eyebrow">{html.escape(detail)}</span><h2>{html.escape(heading)}</h2></div>'
            "<p>Large, lockup, native-size, reverse, and app contexts.</p></div>"
            f'<div class="concept-grid">{cards}</div></section>'
        )

    actions = (
        '<button type="button" class="primary" data-action="refine">Copy refinement request</button>'
        '<button type="button" data-action="continue">Copy discovery continuation</button>'
        if manifest["stage"] == "discovery"
        else '<button type="button" class="primary" data-action="finalize">Copy final choice</button>'
        '<button type="button" data-action="continue">Copy another refinement</button>'
    )
    retired = ""
    if manifest["retired"]:
        retired = " Retired: " + ", ".join(manifest["retired"]) + "."
    review = (
        '<aside class="review-bar" aria-label="Review selections">'
        '<label class="review-field">Reviewer<input id="reviewer" placeholder="Optional name"></label>'
        '<label class="review-field">Notes<textarea id="review-notes" placeholder="What should stay, change, or be avoided?"></textarea></label>'
        f'<div class="review-actions">{actions}</div>'
        '<div class="review-status"><span id="selection-count"></span>'
        f'<span id="review-message" role="status">{html.escape(retired.strip())}</span></div>'
        '<textarea id="review-output" class="review-output" readonly hidden aria-label="Generated continuation request"></textarea>'
        "</aside>"
    )
    script = HTML_SCRIPT.replace("__STAGE__", json.dumps(manifest["stage"])).replace(
        "__MAX__", str(manifest["review"]["selection_max"])
    )
    document = (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f"<title>{html.escape(manifest['project'])} — {stage_label} review</title>\n"
        f'{HTML_STYLE}</head>\n<body><main><header class="page-head">'
        f'<span class="eyebrow">{html.escape(SCHEMA_V2)}</span>'
        f"<h1>{html.escape(manifest['project'])}</h1>"
        f'<p class="meta">{html.escape(meta)}</p>'
        f'<p class="subtitle">{html.escape(subtitle)}</p></header>'
        f"{''.join(sections)}</main>{review}{script}</body>\n</html>\n"
    )
    output_path.write_text(document, encoding="utf-8")
    return output_path


def render(
    manifest_path: Path,
    output_path: Path,
    html_output_path: Path | None = None,
) -> Path:
    manifest_path = manifest_path.resolve()
    manifest = validate_manifest(manifest_path)
    png_path = render_png(manifest, output_path)
    html_path = html_output_path or png_path.with_suffix(".html")
    render_html(manifest, html_path)
    return png_path


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    html_output = Path(args.html_output) if args.html_output else None
    png_path = render(Path(args.manifest), output, html_output)
    html_path = html_output.resolve() if html_output else png_path.with_suffix(".html")
    print(f"Rendered PNG review sheet: {png_path}")
    print(f"Rendered HTML review page: {html_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 - CLI should print one clear error.
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error

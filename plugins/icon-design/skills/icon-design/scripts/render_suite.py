#!/usr/bin/env python3
"""Render a reproducible icon and compact brand-mark asset suite."""

from __future__ import annotations

import argparse
import html
import io
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from xml.etree import ElementTree as ET

try:
    import cairosvg
    from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFilter
except ModuleNotFoundError as error:
    missing = error.name or "rendering dependency"
    raise SystemExit(
        f"Missing {missing}. Install the packages listed in requirements.txt."
    ) from error


PALETTE_KEYS = (
    "ink",
    "paper",
    "paper_bright",
    "paper_shadow",
    "background_top",
    "background_bottom",
    "accent",
)
GEOMETRY_DEFAULTS = {
    "tile_radius_ratio": 0.22,
    "favicon_mark_scale": 0.78,
    "app_mark_scale": 0.78,
    "avatar_mark_scale": 0.86,
    "preview_margin_ratio": 0.098,
    "preview_radius_ratio": 0.181,
}
DISALLOWED_SVG_TAGS = {
    "animate",
    "audio",
    "foreignObject",
    "iframe",
    "image",
    "script",
    "set",
    "text",
    "video",
}
PRESENTATION_ATTRIBUTES = (
    "fill",
    "stroke",
    "stroke-width",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-miterlimit",
    "fill-rule",
    "clip-rule",
)
RESAMPLE = getattr(Image, "Resampling", Image).LANCZOS
NEAREST = getattr(Image, "Resampling", Image).NEAREST


def local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1]


def format_number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def read_json(path: Path) -> Dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Missing design spec: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError("design.json must contain one JSON object")
    return value


def validate_color(value: object, key: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        raise ValueError(f"palette.{key} must be a six-digit hex color")
    return value.upper()


def load_design(path: Path) -> Dict:
    design = read_json(path)
    for key in ("name", "slug", "aria_label", "description", "story", "source_svg"):
        if not isinstance(design.get(key), str) or not design[key].strip():
            raise ValueError(f"design.json requires a non-empty {key!r}")

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", design["slug"]):
        raise ValueError("slug must use lowercase kebab-case")
    source_svg = Path(design["source_svg"])
    if source_svg.is_absolute() or ".." in source_svg.parts:
        raise ValueError("source_svg must stay inside the source directory")

    palette = design.get("palette")
    if not isinstance(palette, dict):
        raise ValueError("design.json requires a palette object")
    unexpected_palette = sorted(set(palette) - set(PALETTE_KEYS))
    if unexpected_palette:
        raise ValueError("Unknown palette keys: " + ", ".join(unexpected_palette))
    design["palette"] = {
        key: validate_color(palette.get(key), key) for key in PALETTE_KEYS
    }

    geometry = design.get("geometry", {})
    if not isinstance(geometry, dict):
        raise ValueError("geometry must be an object")
    unexpected_geometry = sorted(set(geometry) - set(GEOMETRY_DEFAULTS))
    if unexpected_geometry:
        raise ValueError("Unknown geometry keys: " + ", ".join(unexpected_geometry))
    normalized_geometry = dict(GEOMETRY_DEFAULTS)
    normalized_geometry.update(geometry)
    for key, value in normalized_geometry.items():
        if not isinstance(value, (int, float)):
            raise ValueError(f"geometry.{key} must be numeric")
        if not 0 < float(value) < 1:
            raise ValueError(f"geometry.{key} must be between 0 and 1")
        normalized_geometry[key] = float(value)
    if normalized_geometry["preview_margin_ratio"] * 2 >= 1:
        raise ValueError("preview_margin_ratio leaves no visible tile")
    design["geometry"] = normalized_geometry

    material = design.get("material", "glass")
    if material not in ("flat", "glass"):
        raise ValueError("material must be either 'flat' or 'glass'")
    design["material"] = material

    license_spec = design.get("license")
    if not isinstance(license_spec, dict):
        raise ValueError("design.json requires a license object")
    mode = license_spec.get("mode")
    if mode == "all-rights-reserved":
        holder = license_spec.get("holder")
        year = license_spec.get("year")
        if not isinstance(holder, str) or not holder.strip():
            raise ValueError("license.holder is required")
        if not isinstance(year, int) or not 1900 <= year <= 9999:
            raise ValueError("license.year must be a four-digit integer")
    elif mode == "custom":
        if (
            not isinstance(license_spec.get("text"), str)
            or not license_spec["text"].strip()
        ):
            raise ValueError("custom licenses require license.text")
    else:
        raise ValueError("license.mode must be 'all-rights-reserved' or 'custom'")

    return design


def svg_parts(path: Path) -> Tuple[str, float]:
    try:
        raw = path.read_text(encoding="utf-8")
        if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", raw, flags=re.IGNORECASE):
            raise ValueError("DOCTYPE and ENTITY declarations are not allowed")
        root = ET.fromstring(raw)
    except FileNotFoundError as error:
        raise ValueError(f"Missing source SVG: {path}") from error
    except (UnicodeDecodeError, ET.ParseError) as error:
        raise ValueError(f"Invalid SVG in {path}: {error}") from error

    if local_name(root.tag) != "svg":
        raise ValueError("The source root element must be <svg>")

    view_box = root.attrib.get("viewBox")
    if not view_box:
        raise ValueError("The source SVG requires a viewBox")
    try:
        x, y, width, height = [
            float(part) for part in view_box.replace(",", " ").split()
        ]
    except (TypeError, ValueError) as error:
        raise ValueError("viewBox must contain four numeric values") from error
    if x != 0 or y != 0 or width <= 0 or abs(width - height) > 1e-9:
        raise ValueError("The source SVG viewBox must be square and begin at 0 0")

    if "currentColor" not in raw:
        raise ValueError("The source SVG must use currentColor")

    for element in root.iter():
        tag = local_name(element.tag)
        if tag in DISALLOWED_SVG_TAGS:
            raise ValueError(f"Disallowed SVG element: <{tag}>")
        for attribute, value in element.attrib.items():
            name = local_name(attribute)
            lower = value.strip().lower()
            if name == "style":
                raise ValueError(
                    "Use explicit SVG presentation attributes, not style attributes"
                )
            if "javascript:" in lower or "data:" in lower:
                raise ValueError(f"Unsafe SVG attribute on <{tag}>")
            if name == "href" and value and not value.startswith("#"):
                raise ValueError("SVG references must stay inside the document")
            if "url(" in lower and not re.fullmatch(
                r"url\(#[A-Za-z_][\w:.-]*\)", value
            ):
                raise ValueError("SVG url() references must stay inside the document")
            if name in (
                "color",
                "fill",
                "flood-color",
                "lighting-color",
                "stop-color",
                "stroke",
            ):
                allowed = value in (
                    "currentColor",
                    "none",
                    "inherit",
                ) or value.startswith("url(#")
                if not allowed:
                    raise ValueError(
                        f"Visible {name} values must be currentColor, none, inherit, or an internal paint"
                    )

    opening = re.search(r"<svg\b[^>]*>", raw, flags=re.IGNORECASE)
    opening_end = opening.end() - 1 if opening else -1
    closing_start = raw.rfind("</svg")
    if opening_end < 0 or closing_start < opening_end:
        raise ValueError("Could not isolate the SVG body")
    body = raw[opening_end + 1 : closing_start].strip()
    if not body:
        raise ValueError("The source SVG has no visible content")

    root_attributes = []
    for key in PRESENTATION_ATTRIBUTES:
        if key in root.attrib:
            root_attributes.append(
                f'{key}="{html.escape(root.attrib[key], quote=True)}"'
            )
    if root_attributes:
        body = f"<g {' '.join(root_attributes)}>{body}</g>"
    return body, width


def svg_document(
    body: str,
    canvas: float,
    label: str,
    color: Optional[str] = None,
    accessible: bool = True,
) -> str:
    rendered_body = body if color is None else body.replace("currentColor", color)
    accessibility = (
        f' role="img" aria-label="{html.escape(label, quote=True)}"'
        if accessible
        else ' aria-hidden="true"'
    )
    size = format_number(canvas)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}"'
        f"{accessibility}>{rendered_body}</svg>\n"
    )


def transformed_body(body: str, canvas: float, scale: float, paint: str) -> str:
    offset = canvas * (1 - scale) / 2
    transformed = body.replace("currentColor", paint)
    return (
        f'<g transform="translate({format_number(offset)} {format_number(offset)}) '
        f'scale({format_number(scale)})">{transformed}</g>'
    )


def paint_defs(design: Dict, canvas: float) -> str:
    palette = design["palette"]
    size = format_number(canvas)
    return f"""<defs>
  <linearGradient id="icon-suite-tile" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{palette["background_top"]}"/>
    <stop offset="1" stop-color="{palette["background_bottom"]}"/>
  </linearGradient>
  <radialGradient id="icon-suite-accent" cx="0.78" cy="0.14" r="0.82">
    <stop offset="0" stop-color="{palette["accent"]}" stop-opacity="0.36"/>
    <stop offset="1" stop-color="{palette["accent"]}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="icon-suite-paper" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{size}">
    <stop offset="0" stop-color="{palette["paper_bright"]}"/>
    <stop offset="1" stop-color="{palette["paper_shadow"]}"/>
  </linearGradient>
</defs>"""


def background_body(design: Dict, canvas: float, rounded: bool = False) -> str:
    radius = canvas * design["geometry"]["tile_radius_ratio"] if rounded else 0
    size = format_number(canvas)
    rx = f' rx="{format_number(radius)}"' if rounded else ""
    return (
        f'<rect width="{size}" height="{size}"{rx} fill="url(#icon-suite-tile)"/>'
        f'<rect width="{size}" height="{size}"{rx} fill="url(#icon-suite-accent)"/>'
    )


def favicon_svg(design: Dict, body: str, canvas: float) -> str:
    inner = (
        paint_defs(design, canvas)
        + background_body(design, canvas, rounded=True)
        + transformed_body(
            body,
            canvas,
            design["geometry"]["favicon_mark_scale"],
            design["palette"]["paper"],
        )
    )
    return svg_document(inner, canvas, design["aria_label"])


def background_svg(design: Dict, canvas: float) -> str:
    inner = paint_defs(design, canvas) + background_body(design, canvas)
    return svg_document(inner, canvas, design["aria_label"], accessible=False)


def mark_layer_svg(
    design: Dict, body: str, canvas: float, scale: float, glass: bool
) -> str:
    defs = paint_defs(design, canvas) if glass else ""
    paint = "url(#icon-suite-paper)" if glass else design["palette"]["paper"]
    inner = defs + transformed_body(body, canvas, scale, paint)
    return svg_document(inner, canvas, design["aria_label"], accessible=False)


def png_from_svg(value: str, size: int) -> Image.Image:
    data = cairosvg.svg2png(
        bytestring=value.encode("utf-8"), output_width=size, output_height=size
    )
    image = Image.open(io.BytesIO(data)).convert("RGBA")
    image.load()
    return image


def shifted_alpha(alpha: Image.Image, dx: int, dy: int) -> Image.Image:
    shifted = Image.new("L", alpha.size, 0)
    shifted.paste(alpha, (dx, dy))
    return shifted


def shadow_layer(mask: Image.Image) -> Image.Image:
    size = mask.width
    blur = max(2, round(15 * size / 1024))
    offset = max(1, round(12 * size / 1024))
    alpha = mask.point(lambda value: int(value * 0.30))
    shadow = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    shadow.putalpha(alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    moved = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    moved.paste(shadow, (0, offset), shadow)
    return moved


def directional_edges(mask: Image.Image) -> Tuple[Image.Image, Image.Image]:
    size = mask.width
    kernel = max(3, round(9 * size / 1024))
    if kernel % 2 == 0:
        kernel += 1
    dx = max(1, round(3 * size / 1024))
    dy = max(1, round(4 * size / 1024))
    eroded = mask.filter(ImageFilter.MinFilter(kernel))
    edge = ImageChops.subtract(mask, eroded)
    top_left = ImageChops.subtract(mask, shifted_alpha(mask, dx, dy))
    bottom_right = ImageChops.subtract(mask, shifted_alpha(mask, -dx, -dy))
    spec_alpha = ImageChops.multiply(edge, top_left).point(
        lambda value: int(value * 0.72)
    )
    refr_alpha = ImageChops.multiply(edge, bottom_right).point(
        lambda value: int(value * 0.26)
    )
    spec = Image.new("RGBA", mask.size, (255, 255, 255, 0))
    spec.putalpha(spec_alpha)
    refraction = Image.new("RGBA", mask.size, (64, 34, 30, 0))
    refraction.putalpha(refr_alpha)
    return spec, refraction


def compose(
    design: Dict, body: str, canvas: float, size: int, scale: float
) -> Image.Image:
    glass = design["material"] == "glass"
    base = png_from_svg(background_svg(design, canvas), size)
    mark = png_from_svg(mark_layer_svg(design, body, canvas, scale, glass), size)
    mask = mark.getchannel("A")
    base.alpha_composite(shadow_layer(mask))
    base.alpha_composite(mark)
    if glass:
        spec, refraction = directional_edges(mask)
        base.alpha_composite(refraction)
        base.alpha_composite(spec)
    return base


def rounded_preview(design: Dict, body: str, canvas: float, size: int) -> Image.Image:
    geometry = design["geometry"]
    margin = round(size * geometry["preview_margin_ratio"])
    visible = size - margin * 2
    radius = round(size * geometry["preview_radius_ratio"])
    scale = geometry["app_mark_scale"] * visible / size
    tile = compose(design, body, canvas, size, scale)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (margin, margin, size - margin, size - margin), radius=radius, fill=255
    )
    preview = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    preview.paste(tile, (0, 0), mask)
    edge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(edge)
    draw.rounded_rectangle(
        (margin + 3, margin + 3, size - margin - 3, size - margin - 3),
        radius=max(1, radius - 3),
        outline=(0, 0, 0, 86),
        width=max(1, round(size * 6 / 1024)),
    )
    draw.rounded_rectangle(
        (margin + 5, margin + 5, size - margin - 5, size - margin - 5),
        radius=max(1, radius - 5),
        outline=(255, 255, 255, 56),
        width=max(1, round(size * 2 / 1024)),
    )
    preview.alpha_composite(edge)
    return preview


def flat_panel(design: Dict, body: str, canvas: float, size: int) -> Image.Image:
    background = Image.new(
        "RGBA", (size, size), ImageColor.getrgb(design["palette"]["paper"]) + (255,)
    )
    mark = png_from_svg(
        svg_document(
            transformed_body(
                body,
                canvas,
                design["geometry"]["app_mark_scale"],
                design["palette"]["ink"],
            ),
            canvas,
            design["aria_label"],
            accessible=False,
        ),
        size,
    )
    background.alpha_composite(mark)
    return background


def write_text(path: Path, value: str, generated: List[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    generated.append(path)


def save_image(
    image: Image.Image, path: Path, generated: List[Path], **options: object
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, **options)
    generated.append(path)


def readme_text(design: Dict) -> str:
    slug = design["slug"]
    palette = design["palette"]
    material = "subtle glass" if design["material"] == "glass" else "flat"
    return f"""# {design["name"]} brand assets

{design["description"]}

## The mark

{design["story"]}

The canonical mark remains monochrome. Color and the {material} tile treatment
belong to derived assets, never to the core SVG.

## Palette

| Token | Hex |
| --- | --- |
| Ink | `{palette["ink"]}` |
| Paper | `{palette["paper"]}` |
| Paper bright | `{palette["paper_bright"]}` |
| Paper shadow | `{palette["paper_shadow"]}` |
| Background top | `{palette["background_top"]}` |
| Background bottom | `{palette["background_bottom"]}` |
| Accent | `{palette["accent"]}` |

## Files

| File | What it is |
| --- | --- |
| `{slug}-mark.svg` | Canonical mark using `currentColor`. |
| `{slug}-mark-black.svg` / `-white.svg` | Fixed ink and reverse variants. |
| `{slug}-favicon.svg` | Rounded tile favicon. |
| `favicon.ico` | Multi-resolution 16/32/48 px favicon. |
| `favicon-16.png` / `-32.png` / `-48.png` | Exact raster favicon sizes. |
| `apple-touch-icon.png` | 180 px touch icon. |
| `{slug}-app-icon-1024.png` | Opaque full-bleed app-icon master. |
| `{slug}-app-icon-preview-1024.png` | Transparent rounded-square preview. |
| `{slug}-avatar-512.png` | Social avatar with circle-safe placement. |
| `icon-composer-layers/` | Flat background and mark layers. |
| `{slug}-app-icon-preview.png` | App-icon comparison sheet. |
| `favicon-preview.png` | Native-size favicon inspection sheet. |
| `design.json` | Palette, placement, story, and export settings. |
| `render.py` | Rebuilds all derived assets. |

## Regenerating

```sh
python3 -m pip install -r requirements.txt
python3 render.py --source . --output .
```

The full-bleed app icon and avatar are opaque. The rounded preview and flat mark
layer retain transparency.
"""


def license_text(design: Dict) -> str:
    spec = design["license"]
    if spec["mode"] == "custom":
        return spec["text"].rstrip() + "\n"
    return f"""{design["name"]} brand assets - All rights reserved

Copyright (c) {spec["year"]} {spec["holder"]}.

The logos, icons, favicons, and related artwork in this package are brand
assets, not open-source software. No permission is granted to copy, modify,
redistribute, or use them without the rights holder's written authorization.
"""


def deterministic_zip(paths: Iterable[Path], root: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    unique = sorted(
        {path.resolve() for path in paths},
        key=lambda p: p.relative_to(root.resolve()).as_posix(),
    )
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in unique:
            relative = path.relative_to(root.resolve()).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            mode = 0o755 if relative == "render.py" else 0o644
            info.external_attr = mode << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())


def render(
    source: Path, output: Path, zip_path: Optional[Path]
) -> Tuple[List[Path], Optional[Path]]:
    design = load_design(source / "design.json")
    source_svg = (source / design["source_svg"]).resolve()
    if source.resolve() not in source_svg.parents:
        raise ValueError("source_svg resolves outside the source directory")
    if zip_path is not None and output.resolve() in zip_path.resolve().parents:
        raise ValueError("Write the zip beside the suite, not inside it")
    body, canvas = svg_parts(source_svg)
    output.mkdir(parents=True, exist_ok=True)
    generated: List[Path] = []
    slug = design["slug"]
    palette = design["palette"]

    canonical = svg_document(body, canvas, design["aria_label"])
    write_text(output / f"{slug}-mark.svg", canonical, generated)
    write_text(
        output / f"{slug}-mark-black.svg",
        svg_document(body, canvas, design["aria_label"], palette["ink"], False),
        generated,
    )
    write_text(
        output / f"{slug}-mark-white.svg",
        svg_document(body, canvas, design["aria_label"], palette["paper"], False),
        generated,
    )

    favicon_value = favicon_svg(design, body, canvas)
    write_text(output / f"{slug}-favicon.svg", favicon_value, generated)
    favicon_images: Dict[int, Image.Image] = {}
    for size in (16, 32, 48):
        image = png_from_svg(favicon_value, size)
        favicon_images[size] = image
        save_image(image, output / f"favicon-{size}.png", generated)
    save_image(
        png_from_svg(favicon_value, 180), output / "apple-touch-icon.png", generated
    )
    ico_path = output / "favicon.ico"
    favicon_images[48].save(
        ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)]
    )
    generated.append(ico_path)

    app_master = compose(
        design, body, canvas, 1024, design["geometry"]["app_mark_scale"]
    )
    save_image(
        app_master.convert("RGB"), output / f"{slug}-app-icon-1024.png", generated
    )
    app_preview = rounded_preview(design, body, canvas, 1024)
    save_image(app_preview, output / f"{slug}-app-icon-preview-1024.png", generated)
    avatar = compose(design, body, canvas, 512, design["geometry"]["avatar_mark_scale"])
    save_image(avatar.convert("RGB"), output / f"{slug}-avatar-512.png", generated)

    layers = output / "icon-composer-layers"
    background_layer = png_from_svg(background_svg(design, canvas), 1024)
    save_image(background_layer.convert("RGB"), layers / "background.png", generated)
    mark_layer = png_from_svg(
        mark_layer_svg(
            design,
            body,
            canvas,
            design["geometry"]["app_mark_scale"],
            False,
        ),
        1024,
    )
    save_image(mark_layer, layers / "mark.png", generated)

    app_sheet = Image.new(
        "RGBA", (1180, 420), ImageColor.getrgb(palette["paper"]) + (255,)
    )
    app_sheet.alpha_composite(app_master.resize((320, 320), RESAMPLE), (60, 50))
    app_sheet.alpha_composite(app_preview.resize((320, 320), RESAMPLE), (430, 50))
    app_sheet.alpha_composite(flat_panel(design, body, canvas, 320), (800, 50))
    save_image(app_sheet, output / f"{slug}-app-icon-preview.png", generated)

    favicon_sheet = Image.new(
        "RGBA", (560, 180), ImageColor.getrgb(palette["background_bottom"]) + (255,)
    )
    favicon_sheet.alpha_composite(png_from_svg(favicon_value, 128), (28, 26))
    favicon_sheet.alpha_composite(
        favicon_images[32].resize((64, 64), NEAREST), (232, 58)
    )
    favicon_sheet.alpha_composite(favicon_images[32], (248, 74))
    favicon_sheet.alpha_composite(
        favicon_images[16].resize((64, 64), NEAREST), (406, 58)
    )
    favicon_sheet.alpha_composite(favicon_images[16], (430, 82))
    save_image(favicon_sheet, output / "favicon-preview.png", generated)

    reproducible_design = json.loads(json.dumps(design))
    reproducible_design["source_svg"] = f"{slug}-mark.svg"
    write_text(
        output / "design.json",
        json.dumps(reproducible_design, indent=2, ensure_ascii=False) + "\n",
        generated,
    )
    write_text(output / "README.md", readme_text(design), generated)
    write_text(output / "LICENSE", license_text(design), generated)

    script_source = Path(__file__).resolve()
    script_destination = (output / "render.py").resolve()
    if script_source != script_destination:
        shutil.copy2(script_source, script_destination)
    generated.append(script_destination)

    requirements_source = Path(__file__).with_name("requirements.txt").resolve()
    requirements_destination = (output / "requirements.txt").resolve()
    if requirements_source != requirements_destination:
        shutil.copy2(requirements_source, requirements_destination)
    generated.append(requirements_destination)

    archive_path = zip_path
    if archive_path is not None:
        deterministic_zip(generated, output, archive_path)
    return generated, archive_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render SVG, favicon, app-icon, avatar, preview, and source assets."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path.cwd(),
        help="Directory containing design.json",
    )
    parser.add_argument(
        "--output", type=Path, default=Path.cwd(), help="Destination suite directory"
    )
    parser.add_argument(
        "--zip", dest="zip_path", type=Path, help="Archive path; defaults beside output"
    )
    parser.add_argument(
        "--no-zip", action="store_true", help="Skip creation of the neighboring zip"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    try:
        design = load_design(source / "design.json")
        archive = None
        if not args.no_zip:
            archive = (
                args.zip_path.resolve()
                if args.zip_path
                else output.parent / f"{design['slug']}-brand-suite.zip"
            )
        generated, archive = render(source, output, archive)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"Rendered {len(generated)} files in {output}")
    if archive:
        print(f"Wrote {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

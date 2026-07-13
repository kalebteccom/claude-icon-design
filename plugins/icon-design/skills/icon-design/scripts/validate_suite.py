#!/usr/bin/env python3
"""Validate the structure and machine-checkable properties of an icon suite."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple
from xml.etree import ElementTree as ET

try:
    from PIL import Image
except ModuleNotFoundError as error:
    raise SystemExit(
        "Missing Pillow. Install the packages listed in requirements.txt."
    ) from error

from render_suite import load_design, png_from_svg, svg_parts


def expected_files(slug: str) -> Set[str]:
    return {
        "LICENSE",
        "README.md",
        "apple-touch-icon.png",
        "design.json",
        "favicon-16.png",
        "favicon-32.png",
        "favicon-48.png",
        "favicon-preview.png",
        "favicon.ico",
        "icon-composer-layers/background.png",
        "icon-composer-layers/mark.png",
        "render.py",
        "requirements.txt",
        f"{slug}-app-icon-1024.png",
        f"{slug}-app-icon-preview-1024.png",
        f"{slug}-app-icon-preview.png",
        f"{slug}-avatar-512.png",
        f"{slug}-favicon.svg",
        f"{slug}-mark-black.svg",
        f"{slug}-mark-white.svg",
        f"{slug}-mark.svg",
    }


def relative_files(root: Path) -> Set[str]:
    return {
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    }


def parse_svg(path: Path) -> ET.Element:
    try:
        return ET.fromstring(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, ET.ParseError) as error:
        raise ValueError(f"Invalid SVG {path.name}: {error}") from error


def channel_luminance(channel: int) -> float:
    value = channel / 255
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    values = tuple(int(hex_color[index : index + 2], 16) for index in (1, 3, 5))
    red, green, blue = (channel_luminance(value) for value in values)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(first: str, second: str) -> float:
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def inspect_png(path: Path, size: Tuple[int, int], mode: str) -> Image.Image:
    try:
        image = Image.open(path)
        image.load()
    except Exception as error:  # Pillow exposes format-specific exception types.
        raise ValueError(f"Could not read {path.name}: {error}") from error
    if image.format != "PNG":
        raise ValueError(f"{path.name} is not a PNG")
    if image.size != size:
        raise ValueError(f"{path.name} is {image.size}, expected {size}")
    if image.mode != mode:
        raise ValueError(f"{path.name} is {image.mode}, expected {mode}")
    return image


def validate_text_files(root: Path, files: Iterable[str]) -> None:
    forbidden = ("/Users/", "file://", "C:\\Users\\")
    for relative in files:
        path = root / relative
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                raise ValueError(f"{relative} contains a local absolute path")


def validate_suite(root: Path, archive: Optional[Path] = None) -> List[str]:
    if not root.is_dir():
        raise ValueError(f"Suite directory does not exist: {root}")
    design = load_design(root / "design.json")
    slug = design["slug"]
    expected = expected_files(slug)
    actual = relative_files(root)
    missing = sorted(expected - actual)
    extras = sorted(actual - expected)
    if missing:
        raise ValueError("Missing suite files: " + ", ".join(missing))
    if extras:
        raise ValueError("Unexpected suite files: " + ", ".join(extras))

    for relative in expected:
        if (root / relative).stat().st_size == 0:
            raise ValueError(f"Empty suite file: {relative}")

    canonical_path = root / f"{slug}-mark.svg"
    body, canvas = svg_parts(canonical_path)
    canonical_text = canonical_path.read_text(encoding="utf-8")
    if 'role="img"' not in canonical_text or "aria-label=" not in canonical_text:
        raise ValueError("The canonical SVG needs an accessible role and label")
    rendered = png_from_svg(canonical_text, 256)
    bounds = rendered.getchannel("A").getbbox()
    if not bounds:
        raise ValueError("The canonical SVG rendered empty")
    left, top, right, bottom = bounds
    if min(left, top, 256 - right, 256 - bottom) < 2:
        raise ValueError("The canonical mark touches its viewBox edge")
    if (right - left) < 52 or (bottom - top) < 52:
        raise ValueError("The canonical mark occupies too little of its viewBox")
    if canvas <= 0 or not body:
        raise ValueError("The canonical SVG geometry is invalid")

    for suffix in ("black", "white"):
        fixed_path = root / f"{slug}-mark-{suffix}.svg"
        fixed_text = fixed_path.read_text(encoding="utf-8")
        parse_svg(fixed_path)
        if "currentColor" in fixed_text:
            raise ValueError(f"{fixed_path.name} still contains currentColor")

    parse_svg(root / f"{slug}-favicon.svg")

    for size in (16, 32, 48):
        inspect_png(root / f"favicon-{size}.png", (size, size), "RGBA")
    inspect_png(root / "apple-touch-icon.png", (180, 180), "RGBA")
    inspect_png(root / f"{slug}-app-icon-1024.png", (1024, 1024), "RGB")
    rounded = inspect_png(
        root / f"{slug}-app-icon-preview-1024.png", (1024, 1024), "RGBA"
    )
    inspect_png(root / f"{slug}-avatar-512.png", (512, 512), "RGB")
    inspect_png(root / "icon-composer-layers/background.png", (1024, 1024), "RGB")
    mark_layer = inspect_png(
        root / "icon-composer-layers/mark.png", (1024, 1024), "RGBA"
    )
    inspect_png(root / f"{slug}-app-icon-preview.png", (1180, 420), "RGBA")
    inspect_png(root / "favicon-preview.png", (560, 180), "RGBA")

    if rounded.getpixel((0, 0))[3] != 0:
        raise ValueError("The rounded app preview should have transparent corners")
    mark_alpha = mark_layer.getchannel("A")
    if not mark_alpha.getbbox() or mark_layer.getpixel((0, 0))[3] != 0:
        raise ValueError("The Composer mark layer has invalid transparency")

    with Image.open(root / "favicon.ico") as icon:
        sizes = set(icon.ico.sizes()) if hasattr(icon, "ico") else {icon.size}
    required_ico_sizes = {(16, 16), (32, 32), (48, 48)}
    if not required_ico_sizes.issubset(sizes):
        raise ValueError(f"favicon.ico contains {sorted(sizes)}, expected 16/32/48 px")

    for mark_key in ("paper", "paper_bright", "paper_shadow"):
        for background_key in ("background_top", "background_bottom"):
            ratio = contrast(
                design["palette"][mark_key], design["palette"][background_key]
            )
            if ratio < 3:
                raise ValueError(
                    f"{mark_key} vs {background_key} contrast is only {ratio:.2f}:1"
                )

    validate_text_files(
        root,
        (
            "README.md",
            "LICENSE",
            "design.json",
            "render.py",
            "requirements.txt",
        ),
    )

    if archive is not None:
        if not archive.is_file():
            raise ValueError(f"Archive does not exist: {archive}")
        try:
            with zipfile.ZipFile(archive) as zipped:
                names = {name for name in zipped.namelist() if not name.endswith("/")}
                bad = zipped.testzip()
                if names == expected and bad is None:
                    for relative in sorted(expected):
                        if zipped.read(relative) != (root / relative).read_bytes():
                            raise ValueError(
                                f"Zip member differs from suite file: {relative}"
                            )
        except zipfile.BadZipFile as error:
            raise ValueError(f"Invalid zip: {archive}") from error
        if bad:
            raise ValueError(f"Corrupt zip member: {bad}")
        if names != expected:
            missing_zip = sorted(expected - names)
            extra_zip = sorted(names - expected)
            details = []
            if missing_zip:
                details.append("missing " + ", ".join(missing_zip))
            if extra_zip:
                details.append("extra " + ", ".join(extra_zip))
            raise ValueError(
                "Zip contents differ from the suite: " + "; ".join(details)
            )

    return sorted(expected)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a rendered icon suite")
    parser.add_argument("suite", type=Path, help="Rendered suite directory")
    parser.add_argument(
        "--zip", dest="archive", type=Path, help="Neighboring suite zip"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        files = validate_suite(
            args.suite.resolve(), args.archive.resolve() if args.archive else None
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(f"OK: {len(files)} suite files validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

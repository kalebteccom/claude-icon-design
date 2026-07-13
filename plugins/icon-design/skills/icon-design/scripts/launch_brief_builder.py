#!/usr/bin/env python3
"""Open the bundled icon brief builder in the default browser."""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path


def builder_path() -> Path:
    path = Path(__file__).resolve().parents[1] / "assets" / "icon-brief-builder.html"
    if not path.is_file():
        raise FileNotFoundError(f"Brief builder not found: {path}")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open the icon brief builder.")
    parser.add_argument(
        "--print-url",
        action="store_true",
        help="Print the local file URL without opening a browser.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    url = builder_path().as_uri()
    if args.print_url:
        print(url)
        return
    if not webbrowser.open(url, new=2):
        raise RuntimeError(f"Could not open a browser. Open this URL manually: {url}")
    print("Opened the icon brief builder in the default browser.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 - CLI should print one clear error.
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error

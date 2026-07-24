# Production suite

Use this contract for a full icon or compact brand-mark handoff. A narrower job
may omit irrelevant formats, but never pretend an untested format was verified.

## Source directory

Prepare two files:

- `mark.svg`: square viewBox, monochrome, visible fills and strokes expressed as
  `currentColor`, no external resources or scripts.
- `design.json`: name, slug, story, palette, placement, material, and asset
  license. Copy the bundled example and replace every example value.
- `mark-small.svg` (optional): a dedicated small-size drawing referenced as
  `source_small_svg` in `design.json`. When present, the 16 and 32 px favicons
  and the matching `favicon.ico` layers render from it at
  `geometry.favicon_small_mark_scale` (default `1.0`, allowing a full-bleed
  plate that avoids tile-in-tile double framing). Larger assets keep using the
  primary master. Use it when the master's fine details seal or smear below
  48 px.

Keep the source SVG optically centered in its own viewBox. Placement scales in
`design.json` position that same master inside favicon, app, and avatar contexts.

## Standard files

The renderer writes a flat, zip-friendly directory:

| File | Purpose |
| --- | --- |
| `<slug>-mark.svg` | Canonical `currentColor` vector. |
| `<slug>-mark-black.svg` | Fixed primary-ink vector. |
| `<slug>-mark-white.svg` | Fixed reverse/paper vector. |
| `<slug>-favicon.svg` | Rounded tile favicon. |
| `favicon.ico` | Multi-size 16/32/48 px favicon; every layer uses its own native render. |
| `<slug>-mark-small.svg` | Only with `source_small_svg`: the small-size mark. |
| `favicon-16.png`, `-32.png`, `-48.png` | Exact raster favicon sizes. |
| `apple-touch-icon.png` | 180 px touch icon. |
| `<slug>-app-icon-1024.png` | Opaque full-bleed app-icon master. |
| `<slug>-app-icon-preview-1024.png` | Transparent rounded-square preview. |
| `<slug>-avatar-512.png` | Opaque, circle-crop-safe avatar. |
| `icon-composer-layers/background.png` | Flat 1024 px RGB background layer. |
| `icon-composer-layers/mark.png` | Flat 1024 px RGBA mark layer. |
| `<slug>-app-icon-preview.png` | Full-bleed, rounded, and flat comparison. |
| `favicon-preview.png` | Large and native-size favicon inspection. |
| `design.json` | Reproducible design and export settings. |
| `render.py` | Renderer copied into the suite. |
| `requirements.txt` | Pinned dependency ranges. |
| `README.md` | Design story, palette, file map, and regeneration notes. |
| `LICENSE` | Explicit terms for the generated brand assets. |

The neighboring `<slug>-brand-suite.zip` must contain the same files without an
extra top-level directory, matching the shape of a conventional handoff zip.

## Visual checks

`favicon-preview.png` shows the large favicon plus the native 48, 32, and
16 px renders, each drawn once on its own.

Open the comparison sheets after rendering. Also inspect the 16 and 32 px PNGs
at native size. Confirm:

- the metaphor and silhouette survive;
- counters remain open;
- the mark is optically centered in square and circular crops;
- the tile radius and mark scale feel related;
- the light mark has at least 3:1 contrast against both background endpoints;
- the app master is opaque and the rounded preview has transparent corners;
- the Composer mark layer is flat and transparent outside the mark;
- fixed SVG variants contain no `currentColor` token;
- the canonical SVG contains no embedded image, script, or external reference.

Run `validate_suite.py` after the visual pass. Automated validation catches
structure and format errors; it cannot decide whether the icon is good.

## Iterations and cleanup

Keep rejected concepts and exploratory renders outside the final suite. The zip
contains only production files and their regeneration source. Do not include
prompts, chat transcripts, screenshots of design tools, local absolute paths,
temporary environments, or attribution to the tool used to make the files.

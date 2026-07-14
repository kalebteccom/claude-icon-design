<p align="center">
  <img src=".github/icon-design-mark.svg" width="112" height="112" alt="Kalebtec logo">
</p>

<h1 align="center">Icon Design</h1>

<p align="center">
  A deliberate path from a loose idea to a production-ready icon.<br>
  Built for Claude Code, Codex, and the browser.
</p>

<p align="center">
  <a href="https://icons.kalebtec.com/"><strong>Open the brief builder</strong></a>
  ·
  <a href="https://icons.kalebtec.com/llms.txt">Read the agent guide</a>
  ·
  <a href="https://github.com/kalebteccom/claude-icon-design">GitHub</a>
</p>

---

Icon Design separates exploration from decision-making. It starts wide, keeps
every direction addressable by ID, and pauses for a human choice before it
refines or packages anything.

The same repository contains:

- a plugin for Claude Code and Codex;
- a visual brief builder at [icons.kalebtec.com](https://icons.kalebtec.com/);
- a standard PNG and standalone HTML format for discovery and refinement;
- a reproducible renderer for the complete final asset package.

## Install

### Codex

```sh
codex plugin marketplace add kalebteccom/claude-icon-design
codex plugin add icon-design@kalebtec-icon-design
```

Start a new conversation after installation, then use:

```text
Use $icon-design to open the guided brief builder.
```

### Claude Code

```sh
claude plugin marketplace add kalebteccom/claude-icon-design
claude plugin install icon-design@kalebtec-icon-design
```

Restart Claude Code or run `/reload-plugins`, then use:

```text
/icon-design:icon-design
```

Ordinary requests work too. Ask for icon discovery, a numbered refinement, an
SVG audit, favicon cleanup, or a complete brand-suite export.

## The workflow

| Stage | What happens | Review output |
| --- | --- | --- |
| **1 · Discovery** | 20 distinct ideas, normally arranged as five territories with four constructions each | Matching numbered PNG and HTML sheets |
| **2 · Refinement** | One parent or a shortlist is developed while the source controls stay visible | Matching PNG and HTML sheets with lineage and ordered selection |
| **3 · Final** | One explicit choice is corrected, verified, and packaged | Complete SVG, favicon, app-icon, source, comparison-sheet, and zip package |

The HTML review page is self-contained. It embeds the concept SVGs, opens
without a server, lets a reviewer select IDs in order, and copies a compact
request for the next round. The PNG is the stable record for sharing or
archiving. Both come from the same `concepts.json`.

### Discovery

The default discovery round creates `D1-01` through `D1-20`. A useful first
round changes the metaphor, silhouette, construction logic, negative space,
and rhythm—not just the corner radius or line weight.

After reviewing the sheets, continue with a precise instruction:

```text
Refine D1-07.
```

```text
Refine the shortlist D1-07, D1-12, and D1-18.
```

```text
Continue discovery from D1-07 and D1-12, but make the next round quieter and
more geometric.
```

### Refinement

Refinement can be controlled, exploratory, optical, or based on several
parents. Selected parents, controls, and benchmarks stay unchanged and visible
above the new candidates, so a new variant has to beat the source. Any visible
reference can still be the final choice.

```text
Finalize R1-04.
```

```text
Refine R1-04 further. Keep the topology, open the counter, and reduce the
lower-right weight.
```

IDs are never recycled. If a round is rejected, its sources and manifest are
archived and the replacement starts at the next unused number.

### Final

Final delivery begins only after a numbered choice. The selected geometry is
kept intact unless an optical correction is necessary, checked at its required
native sizes and backgrounds, then rendered into the complete package.

If the mark is already approved, discovery and refinement can be skipped:

```text
Use $icon-design to clean up assets/mark.svg and prepare the complete final
suite. Keep the canonical master monochrome and verify 16, 20, 24, and 32 px.
```

## What the final package contains

- canonical `currentColor`, fixed-black, and fixed-white SVGs;
- SVG, PNG, ICO, and Apple touch favicon assets;
- 1024 px app-icon masters and a 512 px social avatar;
- flat layers for Apple Icon Composer;
- native-size favicon and app-icon comparison sheets;
- `design.json`, the renderer, requirements, README, and asset license;
- a reproducible zip that exactly matches the uncompressed suite.

Discovery and refinement stay in the working project, outside the production
zip.

## Use the visual brief builder

The builder turns purpose, visual references, and character into a compact
discovery prompt. Guided mode offers coherent presets; Custom mode exposes six
axes and a 64-cell reference matrix. Original specimens show the choices
without asking anyone to interpret style adjectives blindly.

The complete package is the default. Smaller delivery choices live under
`Customize delivery` and stay out of the main flow.

The builder can copy a prompt, save text, save JSON, and import a prior brief.
It has no account, server, or upload step; unfinished work remains in the
browser.

From a clone:

```sh
python3 plugins/icon-design/skills/icon-design/scripts/launch_brief_builder.py
```

## Render a standard review round

Install the bundled rendering requirements before the first round:

```sh
python3 -m pip install -r \
  plugins/icon-design/skills/icon-design/scripts/requirements.txt
```

Create square monochrome `currentColor` SVGs and a v2 round manifest, then run:

```sh
python3 plugins/icon-design/skills/icon-design/scripts/render_concept_sheet.py \
  path/to/concepts.json \
  --output path/to/discovery-d1.png
```

The command writes both `discovery-d1.png` and `discovery-d1.html`. Use
`--html-output` only when the HTML file needs a different name.

The manifest contract and examples live in
[`round-manifest.md`](plugins/icon-design/skills/icon-design/references/round-manifest.md).

## Run the website

```sh
npm install
npm run dev
```

Build the static site and sync the same single-file builder into the plugin:

```sh
npm run build:plugin
```

The social preview is generated from [`assets/og-card.svg`](assets/og-card.svg).
After changing the artwork or site icon, regenerate the Open Graph card,
favicons, touch icon, and install icons with:

```sh
npm run generate:assets
```

Generated assets are committed and deployed as-is. Regeneration stays explicit
because the card deliberately uses the same native system type as the site.

The canonical metadata, structured data, manifest, crawler rules, and sitemap
are kept in `index.html` and `public/` so they remain available before the app
loads.

Netlify reads its build and response headers from `netlify.toml`. The linked
production site can be deployed with:

```sh
netlify deploy --build --prod
```

## Requirements

- Codex with plugin support, or Claude Code 2.1.143 or newer;
- Python 3.9 or newer;
- CairoSVG 2.7 or newer and Pillow 10 or newer;
- Node 20.19+ on the 20.x line, or Node 22.12+.

On Apple Silicon, Homebrew Cairo may need its library path made explicit:

```sh
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib python3 path/to/render_script.py
```

## Development

Validate both plugin formats:

```sh
claude plugin validate plugins/icon-design --strict
claude plugin validate . --strict

uv run --with pyyaml python \
  "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" \
  plugins/icon-design
```

Run the renderers and workflow tests:

```sh
uv run --with cairosvg --with pillow python -m unittest discover -s tests -v
```

Run the browser-side tests, production build, and bundled-builder sync:

```sh
npm run check
```

## Method and license

The design method combines brand discovery, geometric construction, optical
correction, pixel-grid checks, accessibility, and production handoff. The
reading notes are in
[`design-method.md`](plugins/icon-design/skills/icon-design/references/design-method.md).

The plugin and website code are MIT licensed. Brand assets made with the tool
belong to their respective owners and use the license selected for that suite.

The Kalebtec name, logo, and mark shown in this repository are the exclusive
property of Kalebtec. Copyright © 2026 Kalebtec. All rights reserved. They are
not included in the MIT License. See
[`BRAND-ASSETS.md`](BRAND-ASSETS.md) for the full notice.

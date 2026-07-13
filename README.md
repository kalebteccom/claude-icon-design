# Icon Design for Claude Code and Codex

Icon Design turns a loose idea into a finished icon through three deliberate
stages: discovery, refinement, and final delivery. It keeps exploration broad at
the start, makes every option easy to reference by number, and waits for a choice
before polishing or exporting anything.

The same skill runs in Claude Code and Codex. It can also audit an icon family,
clean up an existing SVG, or take an approved mark straight to a reproducible
brand asset suite.

## Install in Codex

You need a Codex build that includes the `codex plugin` command.

```sh
codex plugin marketplace add kalebteccom/claude-icon-design
codex plugin add icon-design@kalebtec-icon-design
```

Start a new Codex conversation after installation, then use `$icon-design`:

```text
Use $icon-design to open the guided brief builder.
```

## Install in Claude Code

```sh
claude plugin marketplace add kalebteccom/claude-icon-design
claude plugin install icon-design@kalebtec-icon-design
```

Restart Claude Code or run `/reload-plugins`, then use:

```text
/icon-design:icon-design
```

Both runtimes also select the skill from an ordinary request about icon design,
concept exploration, SVG refinement, favicons, app icons, or a brand-suite
export.

## Start with the guided brief

Ask the skill to open the brief builder when you want help choosing a direction.
It walks through purpose, style references, and character. Guided mode offers
six ready-made character presets with useful style pairings. Custom mode exposes
the six axes and a 64-cell matrix. Every matrix cell uses the same 2/4 values it
applies to the live specimen, so its preview and selected result match exactly.
The style specimens are original reference shapes, not logos to imitate.

The complete asset package is the default. Small-size, background, palette, and
extra handoff constraints sit under an optional `Customize delivery` section
instead of taking up a separate step.

The builder produces a compact discovery prompt that can be:

- copied directly into Codex, Claude Code, or another chatbot;
- saved as a plain-text brief;
- saved as JSON and imported again later;
- adjusted without sending unfinished choices to a chat.

It is a single local file with no server, account, or network request. From a
repository clone, open it with:

```sh
python3 plugins/icon-design/skills/icon-design/scripts/launch_brief_builder.py
```

## Run the standalone web app

The brief builder is a Solid app at the repository root. It builds to one static
HTML file, so it can run on a file URL, GitHub Pages, or any static host without
a server or API.

```sh
npm install
npm run dev
```

Create the production site build in `dist/`:

```sh
npm run build
npm run preview
```

The plugin bundles the same app rather than maintaining a separate copy. After
changing the web app, rebuild and sync that single-file bundle with:

```sh
npm run build:plugin
```

## The three stages

### 1. Discovery

Discovery creates 20 genuinely different representations by default. Each one
gets an ID from `D1-01` to `D1-20`, its own monochrome SVG, a short concept note,
and a place on a standard comparison sheet. The sheet shows every direction at
large size, in reverse, and at native size.

The skill stops after the sheet. Continue with a precise instruction:

```text
Refine D1-07.
```

```text
Continue discovery from D1-07 and D1-12, but make the next round quieter and
more geometric.
```

```text
Change the brief: avoid enclosed badges and explore a more open silhouette.
```

Further discovery uses `D2-*`, `D3-*`, and so on, so a selection never becomes
ambiguous.

### 2. Refinement

Refinement starts from one selected discovery ID and produces eight variants by
default. It preserves the idea while testing proportion, topology, counter
shape, stroke or fill, corners, and optical balance. The variants use IDs such
as `R1-01` through `R1-08` and appear on the same standard sheet.

The skill stops again. You can finalize one, refine it further, or return to
discovery:

```text
Finalize R1-04.
```

```text
Refine R1-04 further with a larger counter and less visual weight on the lower
right.
```

### 3. Final

Final delivery starts only after a numbered choice. The chosen mark is corrected
optically, checked on its required backgrounds and native sizes, and packaged as
a reproducible asset suite.

If you already have an approved SVG, you can skip discovery and refinement:

```text
Use $icon-design to clean up assets/mark.svg and prepare the final suite. Keep
the master monochrome and verify it at 16, 20, 24, and 32 px.
```

## What a full export contains

The final zip includes:

- a canonical `currentColor` SVG and fixed dark and light variants;
- SVG, PNG, ICO, and Apple touch favicon assets;
- 1024 px app-icon masters and a 512 px social avatar;
- flat layers for Apple Icon Composer;
- native-size favicon and app-icon comparison sheets;
- the design spec and renderer needed to rebuild every derived asset;
- a concise README and an explicit asset license.

Discovery and refinement files stay in the working project and do not clutter
the production zip.

## Requirements

- Codex with plugin support, or Claude Code 2.1.143 or newer;
- Python 3.9 or newer for sheet and asset rendering;
- CairoSVG 2.7 or newer and Pillow 10 or newer;
- Node 20.19+ on the 20.x line, or Node 22.12+, for web development.

On Apple Silicon Macs, a Homebrew Cairo install may need its library path made
explicit when running either renderer:

```sh
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib python3 path/to/render_script.py
```

## Method

The workflow combines brand discovery, geometric construction, optical
correction, pixel-grid checks, accessibility, and production handoff. The
detailed design notes and reading list are in
[`design-method.md`](plugins/icon-design/skills/icon-design/references/design-method.md).
The round structure and file contract are in
[`three-stage-workflow.md`](plugins/icon-design/skills/icon-design/references/three-stage-workflow.md).

## Development

Validate the Claude Code packaging:

```sh
claude plugin validate plugins/icon-design --strict
claude plugin validate . --strict
```

Validate the Codex manifest:

```sh
uv run --with pyyaml python \
  "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" \
  plugins/icon-design
```

Run all renderer and workflow tests:

```sh
uv run --with cairosvg --with pillow python -m unittest discover -s tests -v
```

Run the web tests, production build, and plugin bundle sync:

```sh
npm run check
```

## License

The plugin code is released under the MIT License. Brand assets made with it
belong to their respective owners and use the license selected for that asset
suite.

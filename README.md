# Icon Design for Claude Code and Codex

Icon Design is a vector-first workflow for icons, favicons, app icons, and
compact brand marks. It covers the design brief, concept directions, geometric
construction, optical correction, native-size checks, and production export.

The same skill runs in Claude Code and Codex. It can start a mark from scratch,
refine an existing SVG, audit an icon family, or turn a finished mark into a
reproducible brand asset suite.

## Install in Codex

You need a Codex build that includes the `codex plugin` command.

```sh
codex plugin marketplace add kalebteccom/claude-icon-design
codex plugin add icon-design@kalebtec-icon-design
```

Start a new Codex conversation after installation. Call the skill directly:

```text
Use $icon-design to design a compact product mark for a privacy-first analytics
tool. It must remain clear at 16 px and work on light and dark backgrounds.
```

Codex can also select the skill from a normal request that mentions icon design,
SVG refinement, favicons, app icons, or a brand-suite export.

## Install in Claude Code

```sh
claude plugin marketplace add kalebteccom/claude-icon-design
claude plugin install icon-design@kalebtec-icon-design
```

Restart Claude Code or run `/reload-plugins`, then call:

```text
/icon-design:icon-design
```

You can put the brief in the same message or describe the job normally and let
Claude Code select the skill.

## Write a useful brief

A short brief is enough when it covers four things:

- what the product, company, or action does;
- the feeling the icon should carry;
- where it will appear and the smallest required size;
- any existing colors, shapes, or neighboring icons it must fit with.

For example:

```text
Design a geometric mark for a file-transfer tool. It should feel quick and
dependable without using a generic lightning bolt. Deliver a monochrome SVG,
favicons, app icons, and a circular social avatar.
```

```text
Use $icon-design to turn assets/mark.svg into a complete icon suite. Keep the
mark itself monochrome, use the palette in brand/colors.json, and verify the
favicon at 16, 24, and 32 px.
```

```text
Audit the icons in ui/icons for metaphor clarity, optical balance, stroke
consistency, and pixel alignment at 16, 20, and 24 px. Fix the SVGs and include
a before-and-after comparison sheet.
```

`$icon-design` is the Codex form. In Claude Code, use
`/icon-design:icon-design` or leave the prefix off and write the request in
plain language.

## What a full export contains

The export is a zip with:

- a canonical `currentColor` SVG and fixed dark and light variants;
- SVG, PNG, ICO, and Apple touch favicon assets;
- 1024 px app-icon masters and a 512 px social avatar;
- flat layers for Apple Icon Composer;
- native-size favicon and app-icon comparison sheets;
- the design spec and renderer needed to rebuild every derived asset;
- a concise README and an explicit asset license.

The renderer uses CairoSVG and Pillow. The source mark stays vector and
monochrome; color and material treatments belong to the derived tiles.

## Requirements

- Codex with plugin support, or Claude Code 2.1.143 or newer;
- Python 3.9 or newer for asset rendering;
- CairoSVG 2.7 or newer and Pillow 10 or newer.

The agent installs the Python packages in a project-local environment when they
are not already available.

## Method

The working method combines brand discovery, geometric construction, optical
correction, pixel-grid checks, accessibility, and production handoff. The full
design notes and reading list are in
[`design-method.md`](plugins/icon-design/skills/icon-design/references/design-method.md).

## Development

Validate the Claude Code packaging:

```sh
claude plugin validate plugins/icon-design --strict
claude plugin validate . --strict
```

Validate the Codex manifest with the plugin-creator validator included with
Codex:

```sh
uv run --with pyyaml python \
  "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" \
  plugins/icon-design
```

Run the renderer tests:

```sh
uv run --with cairosvg --with pillow python -m unittest discover -s tests -v
```

## License

The plugin code is released under the MIT License. Brand assets made with it
belong to their respective owners and use the license selected for that asset
suite.

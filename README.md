# Icon Design for Claude Code

A practical icon and brand-mark workflow for Claude Code. It starts with the
brief and metaphor, builds a disciplined vector master, checks the work at the
sizes people will actually see, and packages the result as a reproducible asset
suite.

The plugin is useful for a single favicon, a product icon, a compact brand mark,
or a related icon family. It can also take an existing SVG and prepare the full
handoff around it.

## Install

```sh
claude plugin marketplace add rowinbot/claude-icon-design
claude plugin install icon-design@kalebtec-icon-design
```

Restart Claude Code or run `/reload-plugins`, then use:

```text
/icon-design:icon-design
```

You can also describe the job normally. The skill is set up to trigger for icon,
favicon, app-icon, logo-mark, SVG cleanup, and icon-suite work.

## What it produces

For a complete handoff, the plugin builds a zip containing:

- a canonical `currentColor` SVG and fixed dark/light variants;
- SVG, PNG, ICO, and Apple touch favicon assets;
- 1024 px app-icon masters and a 512 px social avatar;
- flat layers for Apple Icon Composer;
- native-size favicon and app-icon comparison sheets;
- the design spec and renderer needed to regenerate every derived asset;
- a short README and explicit asset license.

The renderer uses CairoSVG and Pillow. The source mark stays vector and
monochrome; color and material treatments are applied only to derived tiles.

## Requirements

- Claude Code 2.1.143 or newer;
- Python 3.9 or newer for asset rendering;
- CairoSVG 2.7+ and Pillow 10+.

## Examples

```text
Design a compact geometric mark for a privacy-first analytics tool. It should
feel precise without looking cold, and it must survive at 16 px.
```

```text
Turn assets/mark.svg into a complete favicon, app-icon, and avatar suite. Keep
the mark itself monochrome and use the existing brand palette.
```

```text
Audit this toolbar icon family for metaphor clarity, optical balance, stroke
consistency, and pixel alignment at 16, 20, and 24 px.
```

## Method

The working method combines brand discovery, geometric construction, optical
correction, pixel-grid checks, accessibility, and production handoff. The
detailed design notes and reading list live in
[`design-method.md`](plugins/icon-design/skills/icon-design/references/design-method.md).

## Development

Validate the plugin and marketplace:

```sh
claude plugin validate plugins/icon-design --strict
claude plugin validate . --strict
```

Run the renderer tests:

```sh
uv run --with cairosvg --with pillow python -m unittest discover -s tests -v
```

## License

The plugin code is released under the MIT License. Brand assets created with it
belong to their respective owners and use the license selected for that asset
suite.

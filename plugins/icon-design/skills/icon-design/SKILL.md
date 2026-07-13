---
name: icon-design
description: Design, refine, audit, or package original icons and compact brand marks. Use for product and app icons, favicons, UI icon families, monograms, SVG cleanup, small-size optical correction, icon-system rules, export preparation, and reproducible brand-suite delivery.
---

# Icon design

Create original, vector-first icons that communicate quickly and still hold up
at their smallest production size. Treat the mark, its small-size variants, and
the export suite as one system.

## Load the right guidance

- Resolve bundled files relative to this `SKILL.md`, not the user's working
  directory. In the commands below, `<skill-directory>` means the absolute
  directory containing this file. Claude Code may resolve it from
  `${CLAUDE_PLUGIN_ROOT}/skills/icon-design`; Codex should use the installed
  skill path supplied with the skill.
- Read [references/design-method.md](references/design-method.md) before
  designing, refining, or auditing a mark.
- Read [references/delivery-contract.md](references/delivery-contract.md) when
  the request includes production exports, a handoff, or a zip.
- Start from
  [assets/design-spec.example.json](assets/design-spec.example.json) when using
  the bundled renderer.

## Work in this order

### 1. Frame the job

Identify the icon class before drawing:

- Brand mark: recognition and ownership matter most.
- App or product icon: platform context and tile behavior matter most.
- System icon: follow the platform's established metaphor when one exists.
- Workflow icon: task recognition and consistency with its family matter most.

Capture the audience, intended feeling, required metaphor, usage contexts,
smallest size, backgrounds, palette constraints, neighboring icons, and output
formats. If the brief is thin, state sensible assumptions and move forward. Ask
one focused question only when the missing answer would change the concept
substantially.

### 2. Find the concept before the geometry

Translate the brief into a short chain:

`brand or task -> useful metaphor -> basic shapes -> distinctive move`

Explore at least three genuinely different directions for a new mark. Describe
the story, silhouette, and likely small-size risk of each. Do not present tiny
variations of one idea as separate concepts.

Check obvious competitors and symbol conventions when web access is available.
Use that research to avoid collisions, not to trace or remix another mark. Do
not claim trademark clearance.

### 3. Build the vector master

Use a square coordinate system with a deliberate safe area. Prefer simple
primitives, repeated dimensions, and the fewest practical anchor points. Define
stroke weight, corner language, cap and join style, diagonal treatment, and
badge space before expanding the family.

Keep the canonical mark monochrome with `currentColor`. Keep gradients,
materials, shadows, and platform tiles in derived assets. Avoid embedded
bitmaps, external references, scripts, text objects, masks that can be expressed
as paths, and decorative filters in the master SVG.

Make optical corrections when strict centering or equal dimensions look wrong.
Record the reason in the design notes; do not hide arbitrary nudges behind a
claim of mathematical perfection.

### 4. Design at native size

Inspect the icon at every required native size, especially 16, 20, 24, 32, and
48 px. Use a nearest-neighbor enlargement only to inspect the raster decisions;
judge the actual icon at 100%.

At small sizes:

- snap critical edges and centers to the pixel grid;
- remove details that collapse into noise;
- preserve counters and negative space;
- adjust curved or diagonal weight optically;
- create a dedicated small-size variant when scaling the master is not enough.

Test light, dark, muted, selected, and disabled contexts when they apply. Pair
ambiguous workflow icons with text. Supply an accessible name for meaningful UI
icons and hide purely decorative icons from assistive technology.

### 5. Compare, refine, and audit

Review the work as a set, not only as isolated artboards. Check metaphor,
silhouette, proportions, visual center, stroke and corner consistency, spacing,
contrast, pixel fit, and similarity to existing marks.

Do not approve an export from source inspection alone. Render previews and look
at them. Iterate until the large construction, native-size favicon, app tile,
and circular avatar crop all read correctly.

### 6. Build the production suite

Create a source directory containing `design.json` and a square `mark.svg`.
The master must use `currentColor` for every visible fill or stroke.

Run the renderer with an environment that has CairoSVG and Pillow:

```sh
python3 "<skill-directory>/scripts/render_suite.py" \
  --source path/to/source \
  --output path/to/brand-suite
```

If the dependencies are unavailable, create a project-local virtual environment
outside the deliverable directory and install:

```sh
python3 -m pip install -r \
  "<skill-directory>/scripts/requirements.txt"
```

Validate both the directory and zip:

```sh
python3 "<skill-directory>/scripts/validate_suite.py" \
  path/to/brand-suite \
  --zip path/to/brand-suite.zip
```

Never write generated work into the plugin root. It is a versioned installation
cache. Put source, iterations, and final assets in the user's project.

## Handoff

Deliver the final zip, the uncompressed suite when useful, and a compact summary
of the concept, optical corrections, smallest verified size, and any remaining
limits. Keep process notes factual. Do not add tool attribution or invented
testimonials to the asset package.

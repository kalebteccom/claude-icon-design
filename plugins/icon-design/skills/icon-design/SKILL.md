---
name: icon-design
description: Design, discover, refine, audit, or package original icons and compact brand marks. Use for guided icon briefs and moodboards, 20-direction concept discovery, numbered icon sheets, selected-concept refinement, product and app icons, favicons, UI icon families, monograms, SVG cleanup, small-size optical correction, export preparation, and reproducible brand-suite delivery.
---

# Icon design

Run new icon work as three explicit stages: discovery, refinement, and final.
Keep the optional guided brief outside those stages. Stop after each visual
sheet so the user can steer by concept ID.

## Resolve bundled resources

Resolve bundled files relative to this `SKILL.md`, not the user's working
directory. In the commands below, `<skill-directory>` means the absolute
directory containing this file. Claude Code may resolve it from
`${CLAUDE_PLUGIN_ROOT}/skills/icon-design`; Codex should use the installed skill
path supplied with the skill.

- Read [references/three-stage-workflow.md](references/three-stage-workflow.md)
  for every new discovery or refinement project.
- Read [references/design-method.md](references/design-method.md) before drawing,
  refining, or auditing a mark.
- Read [references/delivery-contract.md](references/delivery-contract.md) for a
  final production handoff or zip.
- Start concept rounds from
  [assets/concept-sheet.example.json](assets/concept-sheet.example.json) and a
  final suite from
  [assets/design-spec.example.json](assets/design-spec.example.json).

## Route the request

- For a guided start, moodboard, or thin brief, open the local brief builder:

  ```sh
  python3 "<skill-directory>/scripts/launch_brief_builder.py"
  ```

  Ask the user to paste its compact export back into the chat. Treat that export
  as the brief and do not ask for the same information again.
- For a new mark with enough context, begin at discovery.
- For `Refine <ID>`, find that concept and begin or continue refinement.
- For `Finalize <ID>`, promote that concept to the final stage.
- For an existing SVG that only needs cleanup or exports, skip directly to the
  requested audit or final handoff.

## Stage 1: discovery

Generate 20 genuinely different representations by default. Use distinct
metaphors, silhouettes, construction logic, negative space, and rhythm; do not
pass off styling variations as separate ideas. Save square monochrome
`currentColor` SVGs with IDs `D1-01` through `D1-20` and write `concepts.json`.

Render the standard sheet:

```sh
python3 "<skill-directory>/scripts/render_concept_sheet.py" \
  path/to/discovery/d1/concepts.json \
  --output path/to/discovery/d1/discovery-d1.png
```

Open and inspect the sheet. Deliver it with a compact territory summary, then
stop. Let the user select an ID, request another discovery round, combine useful
properties, or change the brief. Continued discovery uses `D2-*`, normally with
another 20 directions.

## Stage 2: refinement

Take one numbered discovery concept and generate eight variants by default.
Hold the core idea steady while varying proportion, topology, counter shape,
stroke or fill strategy, corner language, and optical balance. Save `R1-01`
through `R1-08`, record the chosen parent in `concepts.json`, and render the same
standard sheet.

Show large, reverse, and native-size views. Explain only the meaningful
differences, then stop for a numbered choice. Continued refinement uses `R2-*`
and preserves its selected parent.

## Stage 3: final

Start only from an explicit user choice. Build a simple canonical vector master,
apply optical corrections, inspect all requested native sizes and backgrounds,
and prepare the production suite. Keep the master monochrome with
`currentColor`; apply color, depth, and materials only to derived contexts.

Create a source directory with `design.json` and a square `mark.svg`, then run:

```sh
python3 "<skill-directory>/scripts/render_suite.py" \
  --source path/to/final/source \
  --output path/to/final/brand-suite

python3 "<skill-directory>/scripts/validate_suite.py" \
  path/to/final/brand-suite \
  --zip path/to/final/<slug>-brand-suite.zip
```

If rendering dependencies are missing, create a project-local environment
outside the deliverable and install:

```sh
python3 -m pip install -r \
  "<skill-directory>/scripts/requirements.txt"
```

On Apple Silicon with Homebrew, if CairoSVG cannot find Cairo, rerun the
renderer with `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`.

## Drawing and review rules

- Translate the brief through
  `brand or task -> useful metaphor -> basic shapes -> distinctive move`.
- Check obvious competitors and conventions when web access is available. Use
  research to avoid collisions, never to trace or remix another mark. Do not
  claim trademark clearance.
- Prefer a square coordinate system, deliberate safe area, simple primitives,
  repeated dimensions, and few anchor points.
- Avoid embedded bitmaps, external references, scripts, text objects, and
  decorative filters in the master SVG.
- Judge the actual icon at 16, 20, 24, 32, and 48 px when relevant. Preserve
  counters, snap critical edges, and make dedicated small-size variants when
  simple scaling fails.
- Test light, dark, muted, selected, circular, and app-tile contexts as needed.
  Pair ambiguous workflow icons with text and provide accessible names for
  meaningful UI icons.
- Render and look at every comparison sheet. Source inspection alone is not a
  visual check.

## Handoff

Keep the working brief and all discovery and refinement rounds in the project,
but keep them out of the production zip. Deliver the final zip, the uncompressed
suite when useful, the chosen concept ID, smallest verified size, optical
corrections, and remaining limits. Keep notes factual and omit tool attribution
or invented testimonials.

Never write generated work into the plugin root; it is an installation cache.

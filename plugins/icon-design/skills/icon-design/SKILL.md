---
name: icon-design
description: Design, discover, refine, audit, or package original icons and compact brand marks. Use for guided icon briefs and moodboards, 20-direction concept discovery, numbered PNG and HTML review sheets, multi-parent or controlled refinement, product and app icons, favicons, UI icon families, monograms, SVG cleanup, small-size optical correction, and reproducible brand-suite delivery.
---

# Icon design

Run new icon work in three stages: discovery, refinement, and final. The guided
brief is preparation, not another production stage. Stop after every discovery
or refinement round so the user can steer by ID.

## Resolve bundled resources

Resolve bundled files relative to this `SKILL.md`, never from the user's current
directory. `<skill-directory>` below means the absolute directory containing
this file.

- Read [references/three-stage-workflow.md](references/three-stage-workflow.md)
  for every new discovery or refinement project.
- Read [references/round-manifest.md](references/round-manifest.md) before
  writing or rendering any `concepts.json`.
- Read [references/design-method.md](references/design-method.md) before drawing,
  refining, or auditing a mark.
- Read [references/delivery-contract.md](references/delivery-contract.md) before
  a final production handoff or zip.
- Start discovery from
  [assets/concept-sheet.example.json](assets/concept-sheet.example.json),
  refinement from
  [assets/refinement-sheet.example.json](assets/refinement-sheet.example.json),
  multi-parent refinement from
  [assets/shortlist-sheet.example.json](assets/shortlist-sheet.example.json),
  and final delivery from
  [assets/design-spec.example.json](assets/design-spec.example.json).

## Route the request

- For a guided start, moodboard, or thin brief, launch the local builder:

  ```sh
  python3 "<skill-directory>/scripts/launch_brief_builder.py"
  ```

  Ask the user to paste its compact export into the chat. Treat that export as
  the brief and do not ask for the same information again.
- For a new mark with enough context, begin at discovery.
- For `Refine <ID>` or a selected shortlist, locate those exact source SVGs and
  begin or continue refinement.
- For `Finalize <ID>`, promote that exact concept. A parent or control may win.
- For an approved SVG that only needs cleanup or exports, skip to the requested
  audit or final handoff.

## Rendering dependencies

Set up rendering before the first discovery sheet, not at final delivery:

```sh
python3 -m pip install -r \
  "<skill-directory>/scripts/requirements.txt"
```

An isolated command is also valid:

```sh
uv run --with cairosvg --with pillow python \
  "<skill-directory>/scripts/render_concept_sheet.py" \
  path/to/concepts.json \
  --output path/to/review.png
```

On Apple Silicon with Homebrew, set
`DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` if CairoSVG cannot find Cairo.

## Stage 1: discovery

Generate 20 genuinely different representations by default. Use five useful
territories with four distinct constructions in each unless the brief calls for
open discovery. Change metaphor, silhouette, construction, negative space, and
rhythm; styling changes do not count as separate ideas.

Save square monochrome `currentColor` SVGs as `D1-01` through `D1-20`, write the
v2 `concepts.json`, and render the standard pair:

```sh
python3 "<skill-directory>/scripts/render_concept_sheet.py" \
  path/to/discovery/d1/concepts.json \
  --output path/to/discovery/d1/discovery-d1.png
```

This always writes `discovery-d1.png` and `discovery-d1.html`. Open and inspect
both. Deliver both with a compact territory summary, then stop. Continued
discovery uses `D2-*` and another broad set unless the user narrows the brief.

## Stage 2: refinement

Choose the refinement mode from the user's instruction:

- `shortlist` for several selected parents;
- `controlled` for focused, one-variable changes;
- `exploratory` for larger structural moves that preserve the idea;
- `optical` for weight, spacing, alignment, and small-size correction.

Keep every selected parent and useful control or benchmark visible and unchanged
above the new candidates. In the manifest, every source being developed uses
role `parent`; `control` is for an unchanged non-parent comparison and
`benchmark` is for an unchanged reviewed high-water mark. Generate eight
variants by default for one parent; for several parents, use enough candidates
to compare each fairly and group them by parent.
Record lineage in `concepts.json`, render the matching PNG and HTML sheets, open
both, and stop for a numbered choice.

Set `review.selection_max` to at least 3 when the user may carry a shortlist
forward; finalization still requires one ID. Do not assume a variant beats any
reference. Let the user finalize a parent, control, benchmark, or variant, run
another refinement, or return to discovery. Continued rounds use `R2-*`. Never
recycle an abandoned ID; continue at the next unused number and list every
skipped same-round ID in `retired`.

## Stage 3: final

Start only from an explicit user choice. Use the selected source geometry as the
canonical parent unless optical correction is necessary. Build a simple
`currentColor` SVG, check native sizes and backgrounds, and prepare the complete
production package by default. Delivery options only change the package when
the user explicitly asks.

Create `final/source/design.json` and `final/source/mark.svg`. If the mark's
fine details seal or smear at 16-32 px, also draw `final/source/mark-small.svg`
and reference it as `source_small_svg` in `design.json`; the suite then renders
the small favicons from it automatically. Then run:

```sh
python3 "<skill-directory>/scripts/render_suite.py" \
  --source path/to/final/source \
  --output path/to/final/brand-suite

python3 "<skill-directory>/scripts/validate_suite.py" \
  path/to/final/brand-suite \
  --zip path/to/final/<slug>-brand-suite.zip
```

Reuse the rendering environment prepared for the review sheets. Keep it outside
the deliverable.

## Drawing and review rules

- Translate `brand or task -> useful metaphor -> basic shapes -> distinctive
  move`.
- Check obvious competitors and category conventions when web access is
  available. Avoid collisions; never trace or claim trademark clearance.
- Prefer a square coordinate system, deliberate safe area, simple primitives,
  repeated dimensions, and few anchor points.
- Avoid embedded bitmaps, external references, scripts, text objects, and
  decorative filters in the master SVG.
- Judge the actual icon at 16, 20, 24, 32, and 48 px when relevant. Make a
  dedicated small-size variant when scaling fails.
- Test light, dark, muted, selected, circular, lockup, and app-tile contexts as
  needed.
- Render and look at every review sheet. Source inspection is not a visual
  check.
- Record ratings only on already reviewed references, only when the user
  supplied them, and name the reviewer. Never pre-rate a new concept or invent
  approval, testimonials, or scores.

## Project record and handoff

Keep the brief, source SVGs, manifests, and accepted round outputs addressable.
Archive abandoned source rounds and their manifests; generated PNG/HTML sheets
can be regenerated and need not be duplicated in an archive. Keep all working
rounds out of the production zip.

Deliver the final zip, uncompressed suite when useful, chosen concept ID,
smallest verified size, optical corrections, and remaining limits. Keep notes
factual and omit tool attribution.

Never write generated project work into the plugin root; it may be an
installation cache.

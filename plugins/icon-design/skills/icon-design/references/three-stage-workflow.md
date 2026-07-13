# Three-stage icon workflow

Use this workflow for a new icon or compact brand mark. The guided brief is
optional; discovery, refinement, and final delivery are the three production
stages.

## Contents

- [Optional guided brief](#optional-guided-brief)
- [Project structure](#project-structure)
- [Stage 1: discovery](#stage-1-discovery)
- [Stage 2: refinement](#stage-2-refinement)
- [Stage 3: final](#stage-3-final)
- [Changing direction](#changing-direction)

## Optional guided brief

Launch the bundled brief builder when the user asks for guidance, wants a
moodboard, or has not supplied enough direction to make useful concepts:

```sh
python3 "<skill-directory>/scripts/launch_brief_builder.py"
```

The builder uses original style specimens rather than existing logos. It saves
locally in the browser and can copy a compact discovery prompt or export the
same brief as text or JSON. Treat a pasted builder prompt as the agreed brief;
do not ask the user to repeat its fields.

## Project structure

Keep every round addressable and keep rejected work out of the final zip:

```text
icon-project/
  brief.json
  discovery/
    d1/concepts.json
    d1/D1-01.svg ... D1-20.svg
    d1/discovery-d1.png
  refinement/
    r1/concepts.json
    r1/R1-01.svg ... R1-08.svg
    r1/refinement-r1.png
  final/
    source/design.json
    source/mark.svg
    brand-suite/
    <slug>-brand-suite.zip
```

Use `D<round>-<two-digit number>` for discovery and
`R<round>-<two-digit number>` for refinement. Never recycle an ID within a
project.

## Stage 1: discovery

Generate 20 genuinely different representations by default. Vary the useful
metaphor, silhouette, construction logic, negative-space move, and visual
rhythm. Do not fill the sheet with small styling changes to one drawing.

For every concept, create a square monochrome SVG using `currentColor` and add
an entry to `concepts.json`:

```json
{
  "project": "Project name",
  "stage": "discovery",
  "round": 1,
  "count": 20,
  "selected_parent": null,
  "concepts": [
    {
      "id": "D1-01",
      "title": "Short direction name",
      "file": "D1-01.svg",
      "territory": "metaphor or construction territory",
      "note": "one sentence explaining the distinctive move"
    }
  ]
}
```

Render the standard numbered sheet:

```sh
python3 "<skill-directory>/scripts/render_concept_sheet.py" \
  path/to/discovery/d1/concepts.json \
  --output path/to/discovery/d1/discovery-d1.png
```

Open the sheet and inspect it before delivery. Send the sheet plus a compact
territory summary, then stop. Offer exactly useful next moves such as
`Refine D1-07`, `Continue discovery from D1-07 and D1-12`, or
`Change the brief: ...`.

A continued discovery round normally adds another 20 concepts as `D2-*`. It
may keep a promising territory, but must still explore distinct constructions.

## Stage 2: refinement

Start from one selected discovery ID. Create eight variants by default and
record that ID in `selected_parent`. Hold the concept constant while varying
proportion, topology, counter shape, stroke or fill strategy, corner language,
and optical balance. Use `R1-01` through `R1-08` and render the same standard
sheet with `stage` set to `refinement`.

Show large, dark-background, and native-size views. Send the sheet, name the
meaningful differences, then stop. Offer `Finalize R1-04`,
`Refine R1-04 with ...`, or `Back to discovery`.

Further refinement uses `R2-*` and sets `selected_parent` to the chosen prior
discovery or refinement ID.

## Stage 3: final

Start only after the user chooses one refinement ID or explicitly promotes a
discovery ID. Build the canonical `currentColor` SVG, make optical corrections,
and verify every requested native size and background. Then follow
`delivery-contract.md` to create and validate the production suite and zip.

Deliver the final files with the chosen ID, smallest verified size, optical
corrections, and any remaining limitation. The final zip contains production
assets only, not discovery or refinement rounds.

## Changing direction

Keep the current brief unless the user changes it. A style adjustment within a
selected idea belongs in refinement. A new metaphor or story returns to
discovery. If the user supplies an existing SVG and asks only for production
exports, skip discovery and refinement and go directly to final delivery.

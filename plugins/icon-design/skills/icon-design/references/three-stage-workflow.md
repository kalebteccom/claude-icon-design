# Three-stage icon workflow

The guided brief is optional preparation. Discovery, refinement, and final are
the three production stages. Every working round has stable IDs and two review
formats generated from one manifest.

## Optional guided brief

Launch the bundled builder when the user asks for guidance, wants a moodboard,
or has not supplied enough direction:

```sh
python3 "<skill-directory>/scripts/launch_brief_builder.py"
```

The builder uses original specimens rather than existing logos. It saves in the
browser and exports a compact prompt, text brief, or JSON. A pasted builder
export is the agreed brief; do not ask the user to repeat it.

## Project structure

```text
icon-project/
  brief.json
  discovery/
    d1/
      concepts.json
      D1-01.svg ... D1-20.svg
      discovery-d1.png
      discovery-d1.html
  refinement/
    r1/
      concepts.json
      R1-01.svg ... R1-08.svg
      refinement-r1.png
      refinement-r1.html
  archive/
    r4-rejected/
      concepts.json
      R4-01.svg ... R4-12.svg
  final/
    source/design.json
    source/mark.svg
    brand-suite/
    <slug>-brand-suite.zip
```

Use `D<round>-<two-digit number>` for discovery and
`R<round>-<two-digit number>` for refinement. Never recycle an ID. Keep source
SVGs and manifests for provenance; regenerate sheets rather than copying stale
ones into archives.

## Stage 1: discovery

The default round is a 5 × 4 exploration:

1. Derive five useful territories from the purpose, audience, promising
   metaphors, constraints, and category research.
2. Draw four structurally different representations in each territory.
3. Check that all 20 remain legible as monochrome silhouettes and at native
   sizes.
4. Describe the deliberate move and the main thing to watch for each concept.

Use `mode: "territory"` in the v2 manifest. Use `mode: "open"` only when the
brief benefits from a less structured search. Follow
`round-manifest.md` for the exact fields.

Render both review formats:

```sh
python3 "<skill-directory>/scripts/render_concept_sheet.py" \
  path/to/discovery/d1/concepts.json \
  --output path/to/discovery/d1/discovery-d1.png
```

The PNG and HTML must contain the same IDs and groups. Open both before
delivery. Send them with a short territory map, then stop. Useful continuations
include:

```text
Refine D1-07.
Refine the shortlist D1-07, D1-12, and D1-18.
Continue discovery from D1-07 and D1-12, but make the next round quieter.
Change the brief: avoid enclosed badges and explore an open silhouette.
```

Further discovery uses `D2-*`, `D3-*`, and so on. It may preserve useful
territories but must introduce genuinely different constructions.

## Stage 2: refinement

Choose a mode intentionally:

| Mode | Use it for | Keep fixed |
| --- | --- | --- |
| `shortlist` | Comparing several promising parents | Every parent shown unchanged in the reference bar |
| `controlled` | Focused proportion or construction decisions | Core idea and all untouched variables |
| `exploratory` | Larger structural alternatives within one idea | Recognizable premise and purpose |
| `optical` | Native-size and balance corrections | Topology and overall silhouette |

One parent normally gets eight candidates. A shortlist can use several parents;
give every source being developed role `parent`, group candidates by parent,
and keep every reference selectable. A parent, control, benchmark, or new
candidate can be the final winner.

In the v2 manifest:

- list source parents, unchanged controls, and useful benchmarks in
  `references`;
- set every candidate's `parent` to one listed reference whose role is
  `parent`;
- describe the deliberate `move`, plus `watch` and `risk` when useful;
- list abandoned IDs in `retired` and continue numbering from the next unused
  ID;
- set `review.selection_max` to at least 3 when a shortlist may continue;
- include ratings only on references and only when a named reviewer supplied
  them.

Render the matching PNG and HTML pages, inspect both, explain only the
meaningful differences, and stop. The user can finalize any candidate or
control, refine one or several further, or return to discovery.

## Stage 3: final

Begin only after an explicit choice or with an already approved source SVG. The
chosen path may be a discovery concept, refinement candidate, parent, or
control. Copy that exact geometry into `final/source/mark.svg`; only change it
for documented optical correction.

Check the canonical `currentColor` master at required native sizes and
backgrounds, then follow `delivery-contract.md`. The full production suite and
zip are the default. Working discovery and refinement files stay outside it.

Deliver the final files with the winning ID, lineage, smallest verified size,
optical corrections, and remaining limits.

## Changing direction

A proportion, spacing, corner, weight, or topology adjustment within a selected
idea belongs in refinement. A new story or metaphor returns to discovery. If a
round is rejected, archive its sources and manifest, retire its IDs, and start
the replacement at the next unused number.

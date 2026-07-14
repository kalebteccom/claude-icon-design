# Round manifest

`concepts.json` is the source for both review formats. The renderer writes a
fixed PNG and a self-contained HTML page with the same IDs, groups, references,
and review contexts.

## Discovery

Use `mode: "territory"` for the standard first round. Unless the brief clearly
calls for another structure, create five territories with four genuinely
different constructions in each.

```json
{
  "schema": "kalebtec.icon-round.v2",
  "project": "Northstar",
  "wordmark": "Northstar",
  "stage": "discovery",
  "round": 1,
  "mode": "territory",
  "count": 20,
  "subtitle": "Five territories, four distinct constructions in each.",
  "references": [],
  "retired": [],
  "review": { "selection_max": 5 },
  "concepts": [
    {
      "id": "D1-01",
      "title": "Signal Window",
      "file": "D1-01.svg",
      "territory": "Signal made legible",
      "move": "A narrow opening turns a noisy field into one clear bearing.",
      "watch": "The opening must survive at 16 px."
    }
  ]
}
```

`mode: "open"` is available when grouping would create false certainty. Every
discovery concept still needs a territory label so the review sheet remains
scannable.

## Refinement

References make lineage visible. A `parent` is source geometry being developed;
it stays unchanged and selectable in the comparison bar. A `control` is an
unchanged non-parent candidate kept in the race. A `benchmark` is an unchanged
reviewed high-water mark. Controls and benchmarks remain selectable and may
still win, but new concepts can name only a `parent` reference as their lineage.

```json
{
  "schema": "kalebtec.icon-round.v2",
  "project": "Northstar",
  "wordmark": "Northstar",
  "stage": "refinement",
  "round": 1,
  "mode": "controlled",
  "count": 8,
  "subtitle": "Eight focused moves against one unchanged parent.",
  "references": [
    {
      "id": "D1-07",
      "title": "Selected parent",
      "file": "../../discovery/d1/D1-07.svg",
      "role": "parent",
      "note": "Keep unchanged, selectable, and grouped with its variants."
    }
  ],
  "retired": [],
  "review": { "selection_max": 3 },
  "concepts": [
    {
      "id": "R1-01",
      "title": "Wider counter",
      "file": "R1-01.svg",
      "parent": "D1-07",
      "territory": "Counter proportion",
      "move": "Opens the internal counter without changing the silhouette.",
      "watch": "Check whether the junction feels too light.",
      "risk": "May lose the parent's compactness."
    }
  ]
}
```

Refinement modes:

- `shortlist`: develop several selected parents in one grouped round.
- `controlled`: hold the parent steady and change one deliberate variable per
  candidate.
- `exploratory`: preserve the idea while allowing larger structural moves.
- `optical`: keep topology fixed and tune weight, spacing, alignment, and
  native-size behavior.

The parent remains selectable. A new variant does not win merely because it is
new.

For several parents, give every selected source role `parent`, group candidates
by their `parent` field, and set `review.selection_max` high enough to carry a
shortlist forward. Use
`assets/shortlist-sheet.example.json` as the starting template. Finalization
still requires exactly one selected ID.

## IDs and abandoned rounds

Use `D<round>-<number>` for discovery and `R<round>-<number>` for refinement.
IDs in one manifest must be consecutive, but they do not need to begin at 01.
If `R4-01` through `R4-12` are abandoned, add them to `retired` and begin the
replacement sheet at `R4-13`. Never assign an old ID to new geometry.

Every current concept ID must be distinct from references and retired IDs. When
a manifest starts above `01`, every earlier ID from that same stage and round
must appear in `retired`. A reference SVG filename must begin with its ID, such
as `D1-07.svg` or `D1-07-signal-window.svg`, so the recorded lineage cannot point
at the wrong source geometry.

## Ratings

Only record a rating when a person supplied it. Ratings belong on `references`,
which represent already reviewed work; never pre-rate a new concept. Attribute
the rating in the manifest:

```json
{
  "value": 8.5,
  "out_of": 10,
  "attributed_to": "Rowin"
}
```

Never invent a score or imply user approval. Omit `rating` when none was given.

## Rendering

The HTML path is optional. Without it, the renderer places the page beside the
PNG with the same base name.

```sh
python3 "<skill-directory>/scripts/render_concept_sheet.py" \
  path/to/concepts.json \
  --output path/to/discovery-d1.png
```

The PNG is the stable shareable record. The HTML page embeds every SVG and all
styles, opens without a server, supports ordered selections, and copies a
compact continuation request. Open and inspect both before delivery.

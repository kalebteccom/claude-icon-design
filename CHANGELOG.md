# Changelog

## 1.6.0 - 2026-07-24

- Added optional dedicated small-size favicon support: `source_small_svg` in
  `design.json` (plus `geometry.favicon_small_mark_scale`, default 1.0) renders
  the 16 and 32 px favicons from their own drawing, ships the small mark in the
  suite as `<slug>-mark-small.svg`, and keeps reproduction and validation
  intact.
- Built every `favicon.ico` layer from its own native render instead of
  downsampling the 48 px image.
- Redrew `favicon-preview.png` to show the large favicon and each native size
  once, on its own, replacing the native-over-pixelated-upscale stacking that
  read as a rendering bug.
- Allowed `*_scale` geometry values to reach exactly 1.0 for full-bleed
  placement.

## 1.5.1 - 2026-07-14

- Replaced the binary theme toggle with a System, Light, and Dark selector.
- Made the selected preference visible, kept explicit choices persistent, and
  restored live operating-system tracking when System is selected.

## 1.5.0 - 2026-07-14

- Replaced the framed app icon with the standalone Kalebtec mark across the
  site, README, favicon set, and install assets.
- Added persistent light and dark themes with system preference support and
  adaptive browser chrome.
- Improved keyboard navigation, focus handling, control labels, contrast,
  forced-colors support, reduced-motion behavior, and dialog semantics.
- Added automated accessibility checks with axe, theme contrast tests, and
  broader coverage for metadata and install assets.
- Expanded search and social metadata while keeping canonical, sitemap,
  robots, manifest, and agent-readable guidance in sync.

## 1.4.0 - 2026-07-14

- Added a v2 round manifest with explicit territories, refinement modes,
  multi-parent lineage, visible controls and benchmarks, retired IDs, and
  reviewer-attributed ratings.
- Made every concept round render a matching fixed PNG and self-contained HTML
  review page with ordered selections and compact continuation requests.
- Standardized discovery as five territories with four distinct constructions
  each, while keeping open discovery available when the brief needs it.
- Added controlled, exploratory, shortlist, and optical refinement modes, and
  kept parent concepts eligible as final choices.
- Reworked the public site around the final Kalebtec logo and added a
  visual discovery-to-final walkthrough.
- Added a branded README hero, new manifest examples, expanded agent guidance,
  and renderer coverage for multi-parent rounds, fresh IDs, and attributed
  ratings.
- Added an explicit all-rights-reserved notice for the Kalebtec name, logo, and
  mark, separate from the MIT-licensed code.

## 1.3.1 - 2026-07-14

- Added the production Netlify build configuration and public-site metadata.
- Added a self-contained `llms.txt` with the complete agent workflow, install
  commands, production stages, validation rules, and release commands.
- Added the Kalebtec footer credit and linked plugin homepages to the live
  builder.
- Added release-oriented response headers for the static deployment.

## 1.3.0 - 2026-07-13

- Rebuilt the brief builder as a standalone Solid app with a single-file static
  production build shared by the plugin.
- Added Guided character presets with reference-style pairings and kept the six
  axes and 64-cell matrix in a separate Custom mode.
- Made matrix cells render the exact 2/4 values they apply to the live specimen.
- Reworked the step counter, onboarding, responsive layout, and how-it-works
  explanation.
- Added deterministic character and prompt tests for the web app.

## 1.2.0 - 2026-07-13

- Added an optional local brief builder with style references, design axes,
  compact prompt output, and text and JSON export.
- Added a live character specimen and 64-state permutation matrix, with complete
  final delivery as the default and optional constraints kept out of the main
  flow.
- Added explicit discovery, refinement, and final stages with stable concept
  IDs and stop-and-select handoffs.
- Added deterministic numbered concept-sheet rendering for 20-direction
  discovery rounds and selected-concept refinement rounds.
- Tightened canonical SVG paint checks and zip-to-suite parity validation.
- Added workflow tests and Codex skill metadata.

## 1.1.0 - 2026-07-13

- Added Codex plugin and marketplace manifests alongside the Claude Code
  packaging.
- Made bundled script instructions work from either runtime's installed skill
  path.
- Added separate installation and usage instructions for Codex and Claude Code.
- Updated repository and publisher links for the Kalebtec GitHub organization.

## 1.0.0 - 2026-07-13

- Initial public release.
- Added the icon-design skill, source notes, deterministic suite renderer, and
  structural validator.
- Added local marketplace packaging and renderer tests.

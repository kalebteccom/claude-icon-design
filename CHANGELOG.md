# Changelog

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

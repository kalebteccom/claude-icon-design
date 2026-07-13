# Design method

- [Start with meaning](#start-with-meaning)
- [Choose a geometry system](#choose-a-geometry-system)
- [Control the silhouette](#control-the-silhouette)
- [Make small sizes deliberately](#make-small-sizes-deliberately)
- [Keep the family coherent](#keep-the-family-coherent)
- [Check accessibility and production behavior](#check-accessibility-and-production-behavior)
- [Source reading](#source-reading)

## Start with meaning

Decide what the icon must help someone recognize or do before choosing its
shape. For interface work, prefer a learned, familiar metaphor over an
inventive but opaque one. For a brand mark, distill the brand's purpose,
audience, personality, and memorable tension into a compact visual idea.

Map the brief through four layers:

1. Message: the promise, task, or state.
2. Metaphor: the object, motion, relationship, or letterform that carries it.
3. Construction: the primitives, negative space, and repeated proportions.
4. Distinction: the one move that makes the silhouette ownable.

Research conventions and competitors early. Familiarity helps comprehension;
similarity damages distinction. A common metaphor still needs an original
silhouette and construction.

## Choose a geometry system

Start on a square grid and define the live area before drawing. A 24-unit grid
is useful for UI icons; a 48- or 96-unit grid gives a compact brand mark more
room for controlled curves. Pick one system and keep it stable across the set.

Define these tokens before scaling the family:

- canvas and safe area;
- keyshape proportions for circles, squares, rectangles, and triangles;
- primary and secondary stroke weight;
- corner radii;
- cap and join style;
- diagonal angle family;
- modifier or badge zone;
- optical offsets.

Material's 24-unit system is a useful reference, not a universal prescription.
Its familiar 20-unit live area, keyshapes, and consistent optical sizing show
how a grid can unify different silhouettes. Adapt the system to the product
rather than copying Material symbols.

Geometry is scaffolding. A circle often needs to overshoot a flat edge; curved
strokes may need more weight than straight ones; an asymmetric silhouette may
need a numerical offset to look centered. Prefer the visually balanced result
and document the correction.

Golden-ratio or modular constructions can help organize a concept, but they do
not make a weak idea good. Use ratios when they clarify relationships. Do not
reverse-engineer ornamental circles after the fact or present them as proof of
quality.

## Control the silhouette

Recognition starts at the outside edge and in the largest negative spaces.
Before polishing details:

- fill the mark solid and check whether it still reads;
- blur or reduce it and check whether its main mass remains distinct;
- compare it beside likely competitors and neighboring product icons;
- test it inside square, rounded-square, and circular crops;
- flip it to light-on-dark and dark-on-light.

Reuse primitives within a family. Repeating the same arrowhead, plus sign,
corner radius, or curve saves time and makes the set feel intentional.

Keep anchor points sparse. Smooth curves with fewer well-placed points scale and
edit more reliably than paths built from many corrective points. Preserve an
editable construction version before expanding strokes or merging paths.

## Make small sizes deliberately

Pixel-perfect does not mean every point must land on an integer at every size.
It means the raster result is deliberate.

Choose target sizes before finalizing detail. Common dense-interface sizes are
16, 20, and 24 px; favicons also need 16, 32, and 48 px. Examine each at native
size. Fractional edges and strokes can work when their antialiasing is balanced,
but critical outer edges should not become a one-sided blur.

Use strokes that resolve cleanly on the target grid. Even-numbered stroke widths
often rasterize predictably; odd widths need half-pixel placement when the
renderer centers the stroke. Expand production strokes only after the editable
source is safe.

Reduce perspective and internal detail as size falls. Protect counters, gaps,
and crossings first. If one master cannot serve both 16 px and display sizes,
draw an optical small-size variant and name it explicitly.

## Keep the family coherent

Judge visual weight, not only bounding boxes. Circles, diagonals, filled shapes,
and open shapes occupy space differently. Compare unlike keyshapes together and
adjust until their apparent size agrees.

Outline, filled, and duotone styles each carry different weight. Mixing them can
communicate state, but the transition should be intentional. Test the icons in
their real UI beside the actual type, controls, colors, and density.

Plan modifiers early. Reserve a consistent corner and enough clear space for a
badge or status mark. Keep the modifier simpler than the primary metaphor.

## Check accessibility and production behavior

Use at least 3:1 contrast for meaningful graphical objects against adjacent
colors. Do not use color as the only signal for a state. Give meaningful icons
an accessible name; hide decorative icons from the accessibility tree.

Export SVG for scalable interface and web use, and raster assets at exact target
sizes where the platform requires them. Remove scripts, external URLs, embedded
bitmaps, editor metadata, and unnecessary transforms from production SVGs.

Name assets by function, size, and state. Verify implementation with the
developer or in the real product so the icon is not stretched, recolored
incorrectly, or given an unintended hit area.

## Source reading

- [Material Design 3: Icons](https://m3.material.io/styles/icons/designing-icons)
- [Adobe: How to design effective icons, Part 1](https://adobe.design/ideas/how-to-design-effective-icons-part-1)
- [Adobe: How to design effective icons, Part 2](https://adobe.design/ideas/how-to-design-effective-icons-part-2)
- [Icons8: How to make pixel-perfect icons](https://icons8.com/blog/articles/make-pixel-perfect-icons/)
- [Figma: How to design a logo in five steps](https://www.figma.com/resource-library/how-to-design-a-logo/)
- [Supercharged Studio: Logo design math](https://www.supercharged.studio/blog/mathematical-logo-design)

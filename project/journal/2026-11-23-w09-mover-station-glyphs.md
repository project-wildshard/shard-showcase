# W09 Movers course: six station numbers, one housing

The W09 mockup shows the orange-rim and cream-disc marker family. The
[pinned Round 5 rows](https://github.com/Raynos/project-wildshard-singleplayer/blob/ce1cf050b3/art/showcase-template/round-5-blockout/layout.js#L213)
establish the route order: 1 Conveyors, 2 Jump Pads, 3 Sliding Platforms,
4 Spinner, 5 Lift and 6 Top Deck. The staged layouts are study lighting and
camera, not asserted station positions.

The original 148,080-byte WSC-PROP-038 GLB remains unchanged. It contains
six housing nodes and the independent modeled 2. The new 46,720-byte GLB
has only the relief meshes for 1, 3, 4, 5 and 6 (1,352 triangles); it
does not contain a housing, backdrop, textures, animation or scoring.
Use the original as-is for 2. For another number, remove or hide the
original `numeral` node and select one corresponding `Glyph N` from the
new pack, without moving it relative to the sign. All variant nodes
intentionally share that local origin; don't draw more than one.

The disc is 245 mm in radius; all verified number vertices stay 62.63 mm
or farther from its edge. Each numeral is 293 mm tall with 10 mm depth.
The rear sits 1 mm inside the cream face, matching the original detail.
The new 1 has a flag and foot to avoid looking like an uppercase I.
The front and oblique plates are visual checks, not native camera,
placement, gameplay/UI, or runtime readability validation.

Rebuild the pack, validation JSON and two preview images:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/mover_station_glyphs.py -- /tmp/w09-markers
```

# West Plaza market stock

Three interchangeable trays for WSC-PROP-005's stall: orchard fruit
(apples and pears), baked loaves and potted herbs. They are decorative,
with compact baked vertex colors, a single material each and no texture
files. The existing stall, canopy, scale, and collision stay unchanged.
Parent one tray at local Three.js position (0, 1.109, 0) without a
further rotation. The same offset scales with the original stall if
it is instanced at a different scale. The view is intentionally suitable
from either long side. No vending, inventory, pickups, or map placement.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/plaza-stall-stock/build.py -- /tmp/plaza-trays
```

Append `--proof-only` to skip review stills. Generation is seeded. Each
GLB is reimported, ray tested against the SHA-pinned slatted counter,
and checked for overlap at a 2 mm QA lift. At nominal height 715 of 819
samples under each continuous foot land on the closely spaced top
slats (the rest can hit their gaps). The feet span those gaps, not a
synthesized replacement surface.

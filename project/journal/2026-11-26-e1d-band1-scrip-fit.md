# E1d · Both original Band 1 Scrip chest anchors fit

Use the existing articulated payout chest without changing its mesh,
hinge or 0.90 s opening clip. This replaces the earlier staged cover-offset
comparison with the two exact Round 5 Band 1 coordinates in Three world X/Z:

| Anchor | X | Z | Minimum sampled lid/neighbor separation |
| --- | ---: | ---: | ---: |
| 1 · Tier 2 flank | 103.247632 | −89.056070 | 0.939 m |
| 2 · Tier 3 flank | 102.685461 | −103.456168 | 1.188 m |

Both face south (+Z), preserving the blockout proxy's zero yaw. Both
have a continuously clear 0.90 m-wide strip from 3.00 m to 0.98 m in
front of the origin. The lower-bound horizontal clearance to nearby
blockers uses conservative world-axis boxes. Reimported animation
has zero chest/blocker overlaps across 109 evaluated poses per
anchor, including both endpoints. No offsets were needed.

The checked-in coordinate extract includes nearby Round 5 crate-stack,
half-wall, breakable-crate and Mite spawn proxy records. Rendered
crate details stay inside those proxy bounds. The ground and materials
are review staging. Mite-size envelopes participate in checks but are
not rendered. This is not a native walking, actual enemy behavior,
final terrain or collision test. The plan says 15 Scrip once per chest;
no payout, trigger, claim persistence or live placement was implemented.

```sh
# Optional provenance re-extract: point to the archived Round 5 JS directory.
node scripts/blender/e1d-band1-fit/extract.mjs /path/to/round-5-blockout
# Reimport, validate and render using the stored coordinate extract.
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e1d-band1-fit/build.py -- /tmp/e1d-band1-fit
# Add --proof-only after the output directory for just the checks.
```

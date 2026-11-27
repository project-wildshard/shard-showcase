# E13 · Band 3 Scrip chests in the drone fields

Reuse the existing animated chest at the two original Round 5 anchors.
E13 plans 40 Scrip per Band 3 chest. The GLB, 0.90-second opening and
zero-yaw placement are unchanged. No new mesh or payout script.

| Anchor | Three X | Three Z | Lid separation | Front approach margin |
| --- | ---: | ---: | ---: | ---: |
| A | 174.250000 | −180.072355 | 2.663 m | 4.422 m |
| B | 223.750000 | −151.493516 | 2.663 m | 4.422 m |

At each anchor the full 0.90 m × 2.02 m front approach and 109 poses
clear the eleven local cover, crate and spawn proxy boxes. Distances
are lower bounds on separation along world or blocker axes, not
nearest-point distances. In particular, a world-axis bounding box for
a rotated wall overlaps the chest footprint, but the wall's own axes
separate it. The render-only wall ribs are not colliders.

Both stills are staged. This does not test the full approach route,
live enemies, touch input, currency, claim persistence or FINDS.

```sh
node scripts/blender/e1d-band1-fit/extract.mjs /path/to/round-5-blockout 3 \
  | cmp - project/layouts/e13-band3-scrip-anchors.json
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e1d-band1-fit/build.py -- /tmp/e13-band3 --band3
cmp /tmp/e13-band3/proof.json project/layouts/e13-band3-scrip-fit-proof.json
```

Use `--proof-only` to skip the stills. Both previous bands' pinned
extracts and proof files remain byte-identical.

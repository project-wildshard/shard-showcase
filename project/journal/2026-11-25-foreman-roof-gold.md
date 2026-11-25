# E13: Gold on the Foreman's office

Round 5 puts the existing Gold cube at map (181, 8.5, 151).
It sits flat on the existing C3 roof cap. No pedestal and no
changes to the cube or office. A small new GLB adds four marked
steel corners and two repair seams. Its origin is the exact Gold
marker, with glTF axes aligned to the original map.

The script checks 361 roof points beneath the Gold and all 864
dressing vertices after GLB reimport. The dressing never crosses
the sampled footprint. The Gold stays at the archived elevation.
From the sampled 1.70 m court eye the office masks all five Gold
centerline heights; from 1.70 m above the roof all five are
visible. Those are two specific camera positions, not a general
visibility or traversal claim. The court view deliberately shows
why the lower eye does not read the find.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/foreman_roof_gold.py -- /tmp/foreman-roof
```

See `project/layouts/foreman-roof-gold.json` for anchor, donor
hashes and samples. Three.js also parses the export as 456
triangles, 52,348 bytes, without textures, lights or animation.
Art study only; no encounter, climb route, pickup, colliders or
FINDS tracking added.

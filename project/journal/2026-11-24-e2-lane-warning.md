# E2 · Static red lane cue

The main E2 plan names a 0.9-second red ground cue before the Pallet Jack's charge. This art-only candidate uses continuous paired red rails with dark keylines, discrete dashes, and pale chevrons to indicate direction by shape as well as palette. The GLB is static: it contains no timing, actor, motion, behaviour or collision. The 1.70 × 8.40 m footprint is an illustrative review size, not a strike definition.

The start is the local origin and the chevrons point along glTF −Z. Marks range 3–4.8 mm above the staging ground. Reimported outline extents and chevron directions checked, along with 24 grade samples. The existing crate props, staged wall, floor, and lighting appear only in renders. No runtime or phone benchmark.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/band2_lane_warning.py -- /tmp/e2-lane
```

`WILDSHARD_VALIDATE_ONLY=1` skips renders. GLB and receipt rebuilt byte-identically, and exact Blender and Three reimports passed (16,196 B / 56 triangles).

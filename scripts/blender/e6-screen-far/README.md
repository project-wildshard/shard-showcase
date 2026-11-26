# E6 · Band 6 sight screen, far render mesh

Use at the original E6 sight-screen placement with its unchanged
near render and collision. The simplified mesh retains the six bays,
oxide kick plates, seven metal ribs, copper corner bumpers and four
cyan lenses. Three dark flats replace each set of sculpted vents;
bolts and small seam details are left out. It is textureless,
ground-origin, and retains the 12 × 3 × 0.6 m source envelope.

At 968 triangles and 76,784 bytes, this version is 66.8% lighter in
triangles and 60.0% lighter in bytes than the 2,916-triangle source.
Both use six material primitives. Reimported geometry matched at
least 99.71% of the projected silhouette by intersection-over-union
across six view angles (9,849 probes each). On the sampled front rays
the original and far art block all 73 probes at both 0.85 and 1.70 m
and clear all probes at 3.10 m. Both pictures share one camera about
30 m from the screen. No automatic selection, collision swap, frame
rate, Sentry encounter or game deployment is implied.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e6-screen-far/build.py -- /tmp/e6-screen-far
```

Set `WSC_METADATA_ONLY=1` to skip the renders. Two runs byte-matched
in the GLB and receipt. See `project/layouts/e6-sight-screen-far-proof.json`.

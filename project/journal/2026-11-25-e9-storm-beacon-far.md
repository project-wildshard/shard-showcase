# E9 · Far beacon tower

A manual lightweight alternative for the 104–106 m spacing of adjacent Band 5 corners. The near tower and charged lamp are byte-identical to their prior exports. The far version removes most rivets, halves the ladder rungs, simplifies the conduit and trims cylinder sides in the crown. It keeps the pedestal bands, open cage, socket and the original lamp. This is not an automatic LOD or a draw-call improvement; both towers have nine primitives. The far tower is 109,108 B / 2,116 triangles versus 244,772 B / 5,164 triangles, roughly 55% smaller and 59% fewer triangles.

The reimported bounds match to six decimal places in metres. The unchanged charged insert shares the mount and retains a conservative 83.3 mm radius margin above its seat. Sixteen matched low-resolution orthographic silhouette masks at 45° increments and 0°/8° elevations have at least 99.48% intersection over union. That measures occupied outlines on those grids, not material parity, performance, or a switching distance. The matched portrait shot places the stands roughly 104 m ahead at 1.70 m eye height. The stands are visual A/B aids, not new map locations. No weather, rewards, quest, collision, lights, scene deployment, or LOD selection changed.

```sh
d=/tmp/e9-far
WSC_BEACON_FAR=1 blender -b -t 4 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/storm_beacon.py -- "$d/far"
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/storm_beacon_far.py -- "$d"
cmp "$d/far/wsc-kit-007-storm-beacon-far.glb" public/assets/wildshard-art/wsc-kit-007-storm-beacon-far.glb
cmp "$d/e9-storm-beacon-far-proof.json" project/layouts/e9-storm-beacon-far-proof.json
```

Without the environment flag the editable source still rebuilds the original tower and lamp. Use `--no-render` on the verifier for numerical checks only. Keep the existing E9 charged insert transform, mounting seat, and placement coordinates unchanged if testing this swap.

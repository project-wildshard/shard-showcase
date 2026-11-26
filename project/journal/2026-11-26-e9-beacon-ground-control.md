# E9 · Ground control for the four Storm Hour beacons

The four existing lamps sit near 20 m on the Round 5 corner
pedestals. This optional control gives each a visible face at ground
level: cast petrol enamel, drip hood, amber status lens, separate
guarded toggle and bottom gland. Nothing changes on the tower, seat
or charged insert. The ground plate has its own art and is not tied
to the Warden reward.

The 56,680-byte GLB has 725 triangles and no textures. The authored
0.32 s clip turns the toggle 110°. Blender reimport checked 65 sampled
poses with no moving-grip collision with the housing or status lens.
The axle is the intended hinge contact. Three.js checked 129 poses for
monotonic travel and a stationary pivot, housing and lens. The lens is
non-emissive and does not change state on its own.

At the four archived pedestal proxies, the optional mounts have Y=1.32 m,
the moving grip stays between Y=1.117 and Y=1.473 m, and the enclosure
projects at most 0.432 m from the mounting plane. The 1.0 m-wide
approach strips tested from 0.50 to 3.65 m clear the known boundary
and podium footprints. The changed art has been byte-matched on rebuild.

| Corner | Three scene translation X, Y, Z | Yaw |
| --- | --- | --- |
| NW | 127, 1.32, 16 | 0° |
| NE | 231, 1.32, 16 | 0° |
| SE | 231, 1.32, 116 | 180° |
| SW | 127, 1.32, 116 | 180° |

Mount transforms are proposals. No interaction rows, final terrain,
cover, enemies, quest flags, weather, lens binding, sounds or iPhone
play were tested or installed.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e9-beacon-control/build.py -- /tmp/e9-control
WSC_NODE_PROJECT=/path/to/three/project node scripts/blender/e9-beacon-control/check.mjs \
  /tmp/e9-control/wsc-kit-007-storm-beacon-control.glb \
  /tmp/e9-control/e9-beacon-ground-control-proof.json
```

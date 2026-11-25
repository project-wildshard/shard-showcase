# E5a · Riveter warning ring and travelling front

E5a gives the Riveter a one-second slam warning followed by a shockwave.
This delivers the reusable floor effects, not a Riveter model or a gameplay
attack. The boundary uses 24 amber dashes; the travelling front is continuous
with a pale leading edge and ember falloff. Both use planar RGBA geometry,
a single unlit draw, a centered pivot, and one normalized radius unit.
No textures, lights, skeletal nodes or collisions. Total: 40,868 bytes and
1,536 triangles. There is no projectile work in this batch.

The caller scales the GLBs to the authored attack radius. The 3.4 m radius and
0.46 s propagation in this review are explicitly provisional. The one-second
warning comes from E5a; no final radius or wave tuning is inferred. Three's
optional visual adapter keeps occlusion by nearer opaque objects and disables
depth writes. It does not supply floor following or hit/dodge logic.
The render fixture uses exact existing gate leaves, crate and pallets, with
alternate overhead and 1.70 m eye-height views. It is not a live game capture.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/riveter_slam_fx.py -- /tmp/riveter-slam
node demos/riveter-slam-vfx/check.mjs
```

The script writes compact GLBs, reimports them in Blender, and optionally
builds the review plates. Set `WILDSHARD_VALIDATE_ONLY=1` to skip renders.
The Node check reimports the exact tracked GLBs in Three and verifies the
planar bounds, transparent lips, 24 spaced runs, closed wave seam, and the
one-second transition with 241 outward samples. No creature, guard arc,
jump window or normal-room integration is claimed.

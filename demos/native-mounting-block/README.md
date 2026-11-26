# W10a · walk up the original mounting block

This tests the existing prop at the archived pad used by the paddock
chute review: Three.js (−36, 0, −96), yaw 0. The fixture reimports the
exact tracked WSC-PLAN-008 GLB over a flat, local ground datum. The
foot-only bench compares its 36 mesh colliders against three simple
boxes matching the existing 180 mm, 360 mm and 540 mm tread heights.
The original artwork is not changed.

Five starts across ±0.25 m pass at 2.2 m/s in each direction with
both representations (20 traverses). The five ascents in each set
settle on the upper tread, at least 0.15 m inside the rear edge.
The ten descents start on the top and walk off the front, ending
on the ground. Three full-speed 4.3 m/s approaches using the exact
mesh also land on the platform. None stalls or leaves the ground.
With the asset collider absent, the center route stays at grade.
The motor uses about 20 mm of skin clearance above the top, so the
receipt shows feet at about Y=0.56 m.

This is not a horse fit, loan, mount, controls, full paddock, or game
install test. Refit the ground datum against the deployed terrain.
Cyan traces the three-box path; the amber flat control is shifted
16 cm laterally for illustration, not as a second authored lane.

```sh
D=demos/native-mounting-block
T=/tmp/mounting-block
blender -b -t 6 --factory-startup --python-exit-code 1 --python "$D/build.py" -- "$T"
node --experimental-transform-types "$D/sample.mjs" "$T"
blender -b -t 6 --factory-startup --python-exit-code 1 --python "$D/build.py" -- "$T"
```

Use Engine 0.1.44 with its Rapier dependency; set
`WSC_NODE_PROJECT` for an external pinned Node project. The previous
prop source remains under `scripts/blender/w10/mounting-block/`.

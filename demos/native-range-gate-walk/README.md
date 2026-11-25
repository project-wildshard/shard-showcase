# W12 / W0b: Range Gate to the eastern garden walk

A native walking check for the existing Range Gate landscape. It does not
build a firing lane, spawn targets or lend equipment. The tested route
uses the archived Range Gate center at Three.js (−36, 0, 60), then
follows existing pedestrian paths through the reconstructed district.
The turn at z = 79.90 m and stop at z = 120 m are selected test waypoints,
not newly authored navigation or a complete map acceptance route.

The full tracked scenery rebuild matches its 3,025-part semantic
signature. The test extracts a bounded 15-mesh, 6,725-triangle neighborhood
from the compiled Blender scene, converts coordinates to Three space,
and installs those triangles as static Rapier colliders. No simplified
support plane or hidden steps were added. The stock player receives
ordinary movement inputs, not position assignments. The optical marks
added during rendering are not colliders or content. Later supplemental
nameplate studies are not installed by this scenery recipe.

The center route is 78.97 m, about 18.5 s, with two right-angle turns.
The center and ±0.65 m lateral variants all finish without a stall
(<4 mm motion on a commanded tick) or airborne tick. By design a test-only
barrier inside the gate stops the same player at z = 61.42 m and trips
the 30-tick stall guard. A fresh center run and independently extracted
fixture data replay exactly. This is one bounded headless walking test:
no production colliders, other gates, live camera, touch controls,
multiplayer, or performance sign-off.

```sh
T=/tmp/w12-range-walk
D=demos/native-range-gate-walk
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-range-scenery/build.py -- --output "$T/rebuild"
B="$T/rebuild/range-landscape-editable.blend"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/extract.py" -- "$T/geometry.json"
node --experimental-transform-types "$D/sample.mjs" "$T/geometry.json" "$T/native.json"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/render.py" -- "$T/native.json" "$T"
```

Requires Engine 0.1.44 and its Rapier/Three dependencies. If they live
outside the checkout, set `WSC_NODE_PROJECT` to that project. Only the
recipes and test summary are committed; regenerate large scratch files
and images as needed.

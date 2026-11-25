# W7b zipline: engine-law and art fit calibration

Runs the pinned engine's ZiplineDriver and ZiplineTrolley on W08's exact two
static art anchors. The driver integrates at 60 Hz, restarts exactly from a
midspan snapshot, and emits sampled Three.js-space positions. A separate
Blender step checks nine radial/center lines per snapshot against the rebuilt
W08 visual mesh, excluding the cable itself. This is not a swept capsule,
rider IK, product-level player attachment, native client, or phone proof.

The 562-tick trial takes 9.37 s, not the plan's roughly 4.7 s. It tops out at
13.80 m/s despite a 22 m/s cap. Geometry samples exercised a 1.05 m start and
a 1.86 m release setback: a shorter candidate start encountered a turquoise
tower lip, and a later release put a radial sample into the roof terminal.
The accepted **sampled** route has at least 62 mm clearance. The center drops
about 156 mm to the sampled pad, and the release advances the body about
1.254 m between consecutive frames. A collision-aware release and actual
launch interaction are still needed. Do not transplant this calibration row
into a live shard without that work.

The new textureless trolley is a standalone mesh in
`public/assets/wildshard-art/w7b-ochre-cable-trolley.glb`. Its origin is the
wire center. Blender +X runs along the cable; Three.js +Y is up. Rendered
pitch follows the track tangent for presentation; native ZiplineTrolley
supplies positions and yaw/roll but does not set this pitch or drive hands.

Rebuild from the repository root, with the exact pinned Node dependencies:

```sh
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-zip/build.py -- --output /tmp/w7b-donor
node --experimental-transform-types demos/native-zipline/sample-ride.mjs /tmp/w7b-driver.json
blender -b -t 6 --factory-startup --python-exit-code 1 --python demos/native-zipline/render-ride.py -- \
  --donor /tmp/w7b-donor/west-zip-route-WIP.glb --ride /tmp/w7b-driver.json --output /tmp/w7b-fit
```

When dependencies live in another project, set `WSC_NODE_PROJECT` to its
absolute root (must have engine 0.1.44 and its installed dependencies).
Only the concise fit receipt, mesh, and recipes belong in Git. The rebuilt
tower/roof donor, generated frame JSON, and render scratch stay out.

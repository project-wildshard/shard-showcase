# W4b Skittles calibration

The original West Physics Yard combines a 24 × 4 × 6 m slope with four
rolling balls and a triangular rack of ten pins. This bench exercises
those exact horizontal anchors with the project's pinned Engine 0.1.44
fixed-step Physics and its DeclaredBodyOps implementation. The rebuilt
ramp and apron contacts are calibration fixtures, not the final shard's
colliders. The floor is level at 0.04 m. The thin rails in the photographs
are visual only. Every ball passed the ramp toe. The pins remained finite;
nine of ten settled at an angle above 60° under this deliberately centered
release. The same fresh run precisely reproduced the captured poses.

The Format 0.43.0 body schema admits the 14 prop definitions. The bench
explicitly enables the four bodies on release and calculates pin tilt
from the native quaternions; neither operation is evidence of a live
lever or a generic tilt read in the script ABI. It creates no score or
best-record rows in the shard. The test performs a fresh-world replay,
not mid-run restart or save/load. Do not ship the bench as a replacement
for the planned lever, settled score, reset, records or player/collision
integration. The original see-saw is untouched.

The two replacement-finish assets are in `public/assets/wildshard-art`.
Both have floor origins and positive Y up in GLB. The lever arm's named
node is separate at its transverse X-axis pivot (Y=1.103 m); the label,
lamp and plinth stay fixed. The scoreboard has a blank inset; the 9/10 in
the photo is a display layer populated from the captured run, not baked
into the GLB. Rendered context (perch shell, rail, lane and labels) is
reproducible but not exported or staged into the connected yard.

Rebuild from the repo root, with the package-lock environment installed:

```sh
node --experimental-transform-types demos/native-skittles/sample-run.mjs /tmp/w4b-trace.json
blender -b -t 6 --factory-startup --python-exit-code 1 --python demos/native-skittles/render-bench.py -- /tmp/w4b-trace.json /tmp/w4b-bench
node demos/native-skittles/check-exports.mjs /tmp/w4b-bench
```

Set `WSC_NODE_PROJECT` to the absolute path of the pinned dependency
installation if it is separate. Do not commit trace captures, generated
.Blend files or raw renders. `project/layouts/w4b-skittle-bench.json`
contains the bounded evidence needed to review and resume.

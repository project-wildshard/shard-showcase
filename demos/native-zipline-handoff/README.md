# W7b zip-house: swept finish and optional confirmation

The stock calibration dismount assigns the rider's location in one 1.254 m step from its final carried pose. The sampled route and roof mesh are unchanged. This bench tries the same target with the pinned Engine 0.1.44's 1.8 m player motor and actual Rapier on 17,508 exact arrival triangles, including the pad, rail and tie-down. Instead of assigning feet, it requests eight bounded motor moves, then uses downward motor steps to settle. The results are not a patch to the existing cable driver.

All 15 combinations of ±100 mm lateral and ±25 mm vertical offsets were carried onto the exact teal pad surface. Maximum measured movement was 157 mm per 60 Hz step, with no step requests over 180 mm. An artificial closed shutter stops the body about 1.00 m short while the same original roof remains in place. In the centred repeat, the pad is first reported by the motor 12 steps after the last stock carried pose. This is a **release-only bench**, not continuous native player carry, course clock, installed event logic, or a phone test. The 9.37 s cable travel timing itself is unchanged.

An optional 6,456-byte, 108-triangle, textureless jade arc acknowledges a completed landing. The GLB starts and ends collapsed, pulses twice in 0.70 s, and sits above the original enamel with no collider. The Three.js mixer check verifies both peaks and rest; the preview hand-selects the peak on a verified successful contact. A product should trigger it only after a grounded finish on this pad and reset the clip on the next run. The current demo does not wire that trigger.

## Rebuild and verify

From the repo root, with the pinned engine installed (or set `WSC_NODE_PROJECT` to the pinned Node project's absolute path):

```sh
T=/tmp/w7b-motor
mkdir -p "$T"
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-zip/build.py -- --output "$T/w08"
B="$T/w08/west-zip-route-editable.blend"
D=demos/native-zipline-handoff
node --experimental-transform-types demos/native-zipline/sample-ride.mjs "$T/ride.json"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/extract.py" -- "$T/terminal-mesh.json"
node --experimental-transform-types "$D/sample.mjs" "$T"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/finish.py" -- "$T"
node "$D/check-three.mjs" "$T/w7b-finish-ack.glb"
blender -b "$B" -t 10 --python-exit-code 1 --python "$D/render.py" -- "$T"
```

The asset's fixed origin is Three (-115,12.754,-16.5), identity rotation. The 1,350 probes cover the complete peak width on the exact pad, and the animation stays within that strip. Keep the full motor frames, rebuilt W08 scene, and RAPIER scratch out of Git. See [the compact proof](../../project/layouts/w7b-zipline-handoff-proof.json).

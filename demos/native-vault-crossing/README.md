# E10c Room 3 · original bridge to the low lift deck

The authored bridge and both landings in the Room 3 cutaway now have a
bounded native clearance test. From the last scramble apron, the headless
stock capsule walks 14.3 m to the existing lift deck in its bottom pose.
Five entry offsets within ±0.45 m passed in both directions (206–209 ticks
per traverse) without stalls, jumps or airborne ticks. The leave-out
control has no bridge collider and falls below Y −47 m before boarding.

There is no need to collide against the decorative rope, flags, metal and
pegs for these tested lines. Repeating all ten paths with only the
bridge's five original timber material meshes (but retaining the exact
landings, frame, deck and catch floor) cuts the complete collision
fixture from 34,825 to 8,112 triangles. Timing is identical, endpoint
differences are under 12 mm, and the measured low point agrees within
0.1 mm. Geometry is never simplified or moved; rendering is unchanged.
This only tests the central walking corridor, not lateral rail contact
or the entire deck width. Do not use the reduced geometry as a safety
rail or count it as a native dynamic rope chain.

```sh
T=/tmp/vault-cross
D=demos/native-vault-crossing
blender -b -t 6 --factory-startup --python-exit-code 1 --python "$D/build.py" -- "$T"
node --experimental-transform-types "$D/sample.mjs" "$T"
blender -b -t 6 --factory-startup --python-exit-code 1 --python "$D/build.py" -- "$T"
```

If Engine 0.1.44 and Rapier are installed outside the repo, point
`WSC_NODE_PROJECT` to the pinned Node project. The pipeline rebuilds
the original adjustable scene and extracts only this interval.
Cyan and amber show measured paths in the review render. No moving lift,
rope dynamics, ladder or scramble, encounter, door, live install or
phone behavior were tested. See the small receipt in
`project/layouts/e10c-vault-bridge-crossing-proof.json`.

# E11c · Walk from the Gauntlet forecourt through C1 and C2

Same 3 public WSC-SCENE-007 art exports and Round 5 positions as `project/layouts/wsc-scene-007-{forecourt,c1-loading,c2-pit}.json`. Unlike the isolated Pit walk, this pass starts north of the forecourt under the west opening, takes the +3 m approach from z132 to z142, then walks the original Loading Yard and The Pit end to end. Fifteen separately shipped haul crates are reinstanced with the existing C1 staging recipe.

Rebuild from the repo root with Blender 4.3.2, Node 24 and an installed engine 0.1.44 with its pinned Rapier dependency. Set `WSC_NODE_PROJECT` to that workspace if different from the checkout.

```sh
d=demos/native-gauntlet-through-walk
assets=public/assets/wildshard-art
out=$(mktemp -d)
blender -b -t 4 --factory-startup --python-exit-code 1 --python "$d/extract.py" -- "$assets" "$out/geometry.json"
node --experimental-transform-types "$d/sample.mjs" "$out/geometry.json" "$out/walk.json"
blender -b -t 6 --factory-startup --python-exit-code 1 --python "$d/render.py" -- "$assets" "$out/walk.json" "$out"
```

The collider benchmark uses 37,550 evaluated structural triangles in 133 meshes. Paint, wear panels and small lighting details do not define support. G1's two original ramps share the exact four planar top corners at x25/35 and z184/190, from 0 to +2.5 m. The bench keeps the C1 ramp and parapets, suppressing only the redundant C2 copy. The exports remain unchanged. The G2 stub keeps its original end wall; there is no C3 handoff in this proof.

Stock 0.38 m physics capsule, 4.3 m/s and 60 Hz ordinary horizontal movement. No synthetic ground, jump input, position assignments or engine changes. Three paths per ramp pairing (west-west and east-east, offsets −0.64/0/+0.64 m), all grounded with zero stalls along 212–234 m (50.2–55.3 s). Verify that the capsule reached the +3 m terrace, descended to the C1 floor, then crossed onto the +2.5 m C2 ledge before reaching G2. The west center route repeats exactly. Deliberate walks into the dividing wall, staged C1 cargo, and capped G2 stop against those surfaces.

The two pictures are annotated Blender views, not gameplay captures. No waves, live collision install, combat, respawns, doors, physical phone test, or extension to C3 is implied.

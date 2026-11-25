# E11c · C2 Pit pedestrian calibration

This is the existing WSC-SCENE-007 Gauntlet court, not the Big Pallet pit. The plan is `docs/plans/kitchen-sink-v2/slices/E11c-gauntlet-courts-supervisor.md` on main; the original Round 5 geometry and asset provenance are recorded in `project/layouts/wsc-scene-007-c2-pit.json`. The original GLB and editable builder (`scripts/blender/showcase-studies/gauntlet_pit.py`) are unchanged.

From the repository root, use Blender 4.3.2 and a Node 24 workspace with engine 0.1.44 and its pinned Rapier dependencies (set WSC_NODE_PROJECT to its absolute path if external):

```sh
d=demos/native-gauntlet-pit-walk
asset=public/assets/wildshard-art/wsc-scene-007-c2-pit.glb
out=$(mktemp -d)
blender -b --factory-startup --python-exit-code 1 --python "$d/extract.py" -- "$asset" "$out/geometry.json"
node --experimental-transform-types "$d/sample.mjs" "$out/geometry.json" "$out/walk.json"
blender -b -t 6 --factory-startup --python-exit-code 1 --python "$d/render.py" -- "$asset" "$out/walk.json" "$out"
```

The extractor pins donor SHA-256 and gets 5,924 triangles from 38 reimported structural meshes. World translation is (55, 0, 212). Dress panels, painted stripes, lamp inserts, and hanging cloth are intentionally excluded. The stock 0.38 m capsule uses normal horizontal input at 60 Hz and 4.3 m/s; no jumping, coordinate assignments, synthetic support plane, or modified engine. Six routes start on G1's uphill wedge, traverse the +2.5 m ledge, descend either 7 m ramp (at world x48 or x76, three offsets each), pass around cover and arrive inside the G2 stub. All stayed grounded without stalls for 109.0–113.9 m (25.77–26.92 seconds); the western center route repeats exactly. A straight line into the west pillar stopped near z212.55 and continuing beyond the G2 stub hit its actual end wall at capsule x109.11. Nothing beyond that wall was tested.

The two images are Blender views of the unchanged art with measured mint/blue route samples drawn on top. This is not a playable deployment, full C1-to-C2 handoff, physical phone performance result, or proof of combat, opening gates, or connected C3.

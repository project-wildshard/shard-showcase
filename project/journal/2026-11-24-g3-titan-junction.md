# G3 from Court 3 to the Titan lane

A bounded static art study authored from Round 5 `ce1cf050b3`, `art/showcase-template/round-5-blockout/layout.js` lines 326–336 and 369–373 (blob `5d019a020361c47187ec889f2bc947f82cd9f98a`), and `lab.js` lines 541–552, 562–570 and 589–597 (blob `51a3b4bef1f2d4891172164d10893d98d450a3b9`). Map-space anchor (198,0,186) is the GLB origin; the origin does not move gameplay. Reuses the archived layout, not the office/balcony geometry or the larger separate Titan arch. The 12 m road shortcut comes in from the north and is intentionally off-scene, not conflated with G3.

The 0.22 rad cut goes through both terraces and the rim wall. It is 6.15 m across at r=28 m, expanding to 9.22 m at r=42 m. The finished court floor ends on centerline at x=174. The next 14 m are at the original ground datum before the passage starts at x=188. The passage spans x=188–208; the nominal 8 m opening is 7.2 m clear between the passage walls, then feeds the 8 m notch in the west wall of the 14 m Titan lane. The lane continues south to the cropped plaza at z=197.

537 reimported floor samples with 0.125 m spacing show no axial gap, a maximum sampled transition of 0.050 m, and unobstructed centerlines at 1.4 m height. Side rays and off-center passage rays verify the stated bounds; paired rays on each side of the taper verify the floor vs. terrace heights. Turn signage is a proposed art cue, not a runtime waypoint. Striping and cladding are new staging. This does not alter wave 5 logic, gate state, route colliders, either entrance, or the arena.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/g3_titan_junction.py -- /tmp/g3-junction
```

`WILDSHARD_VALIDATE_ONLY=1` reimports and checks without rendering. The GLB is 330,832 B, 4,884 triangles, 36 mesh objects; Three loads its named surfaces and local envelope. GLB and measurement JSON were rebuilt byte-identically. Studio sky, lights, and surroundings are not in the export.

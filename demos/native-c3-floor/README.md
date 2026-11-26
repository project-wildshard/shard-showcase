# E11c: stitch the Foreman's floor between G2 and the office

The original Round 5 layout calls for a flat 28 m-radius floor centred at Three (146,0.05,186). The existing southwest G2 handoff and northeast office are two disconnected partial sectors. This floor adds only the missing surface inside the radius, clipping against the planar triangles of the exact donor GLBs rather than replacing either piece or laying a second floor on top. The textureless vertex colors blend warm concrete from the threshold toward the office earth. The arena still needs its other walls and terraces, G3, doors, encounter and timer.

Place `e11c-c3-fitted-floor.glb` at Three (146,0,186) with identity rotation, the G2 threshold at (110,0,214) at identity, and the office sector at (146,0,186) with +45° around Three +Y (local +X points toward +X/−Z in the map). The floor is 525 triangles / 18,232 bytes. At 890 regularly spaced interior ray probes, every point had exactly one surface: 104 hits on the retained sectors, 786 on new infill. This is a sampled coverage check, not a whole-court test.

With Engine 0.1.44 and the stock player capsule, five lanes from ±1.30 m all walked from the G2 threshold to the office-side floor and back, about 128.8 m each. All stayed grounded, did not jump or stall, and had verified physical contact on both donors and the new floor. Removing the infill left the centre run falling at x131.90, z198.87 before it could reach the office. The line in the renders is the recorded walk, not part of the asset. This does not prove the approach to G3, live behavior, or phone controls.

## Rebuild

From the repo root with Blender 4.3.2 and the same pinned Node project used by the native G2 benchmark:

```sh
T=/tmp/w-c3
D=demos/native-c3-floor
A="$PWD/public/assets/wildshard-art"
blender -b -t 8 --factory-startup --python-exit-code 1 --python "$D/build.py" -- "$A" "$T"
node --experimental-transform-types "$D/sample.mjs" "$T"
blender -b -t 12 --factory-startup --python-exit-code 1 --python "$D/build.py" -- "$A" "$T" "$T/walk.json"
```
Original Round 5 layout and lab hashes: `5d019a020361c47187ec889f2bc947f82cd9f98a`, `51a3b4bef1f2d4891172164d10893d98d450a3b9`. Exact donor and compact replay evidence: [e11c-c3-floor-proof.json](../../project/layouts/e11c-c3-floor-proof.json).

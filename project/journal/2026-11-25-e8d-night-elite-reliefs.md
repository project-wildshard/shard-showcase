# E8c/E8d: three night-elite trophy reliefs

The E8c plan gives Sir Nibbles a cardboard crown, Hot Mess twin torches and
glowing slag, and Riveting Rita a lamp-plate. These concepts translate
those cues into display prizes, not actor variants or finalized drop names.
Each keeps a matching dark locked cut from its primary outline. The locked
and earned comparison uses the same camera and exact shared twelve-frame
donor, with three frames moved together for a close-up. No canonical slot
numbers, perks, unlocks, drop behavior, or scene placement were changed.

One 75,228-byte GLB has six origin-centered nodes: three detailed reliefs
(1,204 triangles together) and three flat cuts (172 triangles together).
Select one state per slug; do not show the whole library at the origin.
The back plane is local Y=0 in Blender, front is +Y; mount offsets are
demonstrated in the script. All three fit with 8 mm front clearance and
at least 55 mm to the mount inset. The source tests contour crossings,
triangle counts and bounds after a clean Blender glTF reimport, and pins
the unchanged mount donor. Independent reruns match GLB and receipt bytes.

```sh
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/night_elite_reliefs.py -- /tmp/e8d-night
cmp /tmp/e8d-night/receipt.json project/layouts/e8d-night-elite-reliefs-proof.json
```

Set `WILDSHARD_VALIDATE_ONLY=1` to skip only the two comparison renders.

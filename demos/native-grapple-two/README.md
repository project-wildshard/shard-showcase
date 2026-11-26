# W7a: two consecutive native grapple hops

The first perch proved that the stock claw needs a standable landing within nine vertical metres below a ring. The second ring is visible from that perch, about 30.73 m from the eye, but the exact W08 corridor alone still offers no valid landing for it. The second tower adds a 3.40 × 2.60 m deck with top Y=8.20 m beyond the unmodified 16 m ring. The optional GLB is 57,016 bytes, 972 triangles, no textures. Position its ground-centred origin at Three (-172,0,-70.2) with identity rotation. This is an exposed test deck, not a final rail or descent design.

The pinned Engine 0.1.44 native grapple and actual Rapier motor land both hops in **one SimHost session**. The second lock starts from the first landing's exact settled pose; the harness points the view at ring 2 without changing position, velocity or motor. Headless portrait camera selection, named lock and a second center replay agree. Across 25 starting offsets over ±1 m in X and Z, the second deck receives all 25 in 156–157 ticks from fire and retains ≥293 mm beyond the capsule radius after settling. The no-second-tower control reaches the first deck but cannot lock the second ring. The collision envelope uses 900 exact W08 triangles, deck boxes measured after GLB reimport, and reimported structural dressing triangles.

This is two of five hops, not a course install, timer, phone playtest, or final art acceptance. Cyan and amber ribbons in the two views show the center replay with a 0.21 m visual lift; they are not in the GLB.

From the repo root, using Blender 4.3.2 and the pinned npm dependencies (see the first perch):

```sh
T=/tmp/w7a-two
mkdir -p "$T"
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-zip/build.py -- --output "$T/w08"
B="$T/w08/west-zip-route-editable.blend"
D=demos/native-grapple-two
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/extract.py" -- "$T/corridor.json"
blender -b "$B" -t 6 --python-exit-code 1 --python demos/native-grapple-perch/perch.py -- "$T"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/model.py" -- "$T"
node --experimental-transform-types "$D/sample.mjs" "$T" "$T/native.json"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/model.py" -- "$T" "$T/native.json"
```

The existing first perch rebuilt byte-for-byte, as did the second tower in two fresh W08 loads. The small checked-in proof omits raw motion frames; regenerate them with the commands above. See `project/layouts/w7a-two-hop-proof.json`.

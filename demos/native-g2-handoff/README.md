# E11c: walk through G2 into the C3 entrance sector

Round 5 gives G2 a level passage at x96–115, z210–218, and cuts the southwest side of the C3 ring near (115,214). The exact C2 art stops at x110 and includes a blind steel recess, not a gate that opens. The optional extension starts flush at (110,0,214), rises 50 mm over 5 m to the original passage datum, and turns inward through two partial terrace shoulders toward the floor at r20. It ends there: no full Court 3, office join, G3, wave or door logic. Terrace levels on either side use Round 5's r28/34/40/42 and 1.5/3/6 m; the traversable southwest floor is a new art proposal.

Place the optional 45,540-byte, 744-triangle GLB at Three (110,0,214) with identity rotation. In this open fixture only, omit the donor's separately imported dark "Blind portal recess" mesh: 12 triangles at x109.505–109.995. The C2 export itself is untouched; neither rewriting nor opening a live gate is part of this work. Decorative lenses and inlays don't provide collision.

Using exact previously audited forecourt, C1 and C2 geometry, reimported handoff meshes and the stock Engine 0.1.44 capsule, six walks (both ramp routes with three offsets) went from the forecourt to x130.00–130.08 in about 240–262 m. All remained grounded without jumping or stalling. With the original cap restored, the capsule stops at x109.10. Turning into the new parapet stops at z217.10. The center route repeats exactly. Ribbons in the two renders mark that replay, not objects supplied in the GLB.

Rebuild from repo root using Blender 4.3.2 and the same engine dependencies as the forecourt-to-Pit benchmark. Set `WSC_NODE_PROJECT` if needed:
```sh
d=demos/native-g2-handoff
out=/tmp/wsc-g2
assets="$PWD/public/assets/wildshard-art"
blender -b -t 4 --factory-startup --python-exit-code 1 --python "$d/model.py" -- "$out"
blender -b -t 6 --factory-startup --python-exit-code 1 --python "$d/review.py" -- "$assets" "$out"
node --experimental-transform-types "$d/sample.mjs" "$out/corridor.json" "$out/walk.json"
blender -b -t 6 --factory-startup --python-exit-code 1 --python "$d/review.py" -- "$assets" "$out" "$out/walk.json"
```

Two fresh model builds byte-match. Numeric checks: `project/layouts/e11c-g2-c3-handoff-proof.json`. Original Round 5 source blobs: layout `5d019a020361c47187ec889f2bc947f82cd9f98a`, lab `51a3b4bef1f2d4891172164d10893d98d450a3b9`.

# Band 1 half-cover

Interprets the archived Round 5 `half` proxy without changing its nine
anchors, rotations, or ground origin. The main strip is 5.0 × 0.8 m and
the 0.8 × 3.0 m return stands at the original local offset. The shared
outside dimensions in glTF axes are 5.8 × 1.10 × 3.0 m, not two scaled
copies of the earlier movable cover barrier. The cast base is the
collision piece; orange plates and wear are visually applied to it.
The crates and freight scenery in the views are not part of this GLB.

Save the exact `layout.js` and `placement.js` files from
`Raynos/project-wildshard-singleplayer@ce1cf050b3`,
`art/showcase-template/round-5-blockout/`, outside the repo. The
extractor verifies Git blob IDs. Reuses the existing pinned crates
and cradle for optional scene context.

```sh
T=/tmp/band1-half
mkdir -p "$T"
D=scripts/blender/e1-half-cover
node "$D/extract.mjs" /path/to/round-5-blockout > "$T/anchors.json"
blender -b -t 8 --factory-startup --python-exit-code 1 --python "$D/build.py" -- "$T/anchors.json" "$T"
WSC_NODE_PROJECT=/path/to/engine/install node --experimental-transform-types \
  "$D/check.mjs" "$T/half-art.json" "$T/half-collision.json" "$T/proof.json"
cmp "$T/proof.json" project/layouts/e1-half-cover-proof.json
```

The bench cooks exact reimported body triangles and walks the stock
0.38 m capsule on flat ground. Each face and return stops the expected
approach; omitting geometry lets the same route through. Both outer
flanks remain open. No installed level, combat hit rays, phone,
navmesh, projectile behavior, or AI/aggro.

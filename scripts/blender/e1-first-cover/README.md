# First East cover on the Round 5 road shoulder

A compact steel-and-oak cradle makes a five-crate stack reusable. The exact
haul-crate mesh is used five times, not merged into the new file. Both assets
have ground-based pivots in Three. Use the crate local XYZ offsets and the
Three Y rotations in the receipt. The three cover rows match the closest
Band 1 crate locations to the road in the first 45 m of Round 5. Their static
model choices are new; the old layout, roads and day pack anchors are not
changed. Distant scenery is only in the render.

The nearest geometry is 5.69 m north of the 17 m road's edge. In the isolated
flat native bench, each cover blocks a head-on walk; removing it lets the same
walk through. The player walked past both flanks of all three stacks and for
42.76 m along the road shoulder without leaving the ground. This isn't a
baked terrain install, a pathfinding/aggro check or a phone playtest.

Save the exact `layout.js` and `placement.js` Git blobs from the archive and
ref named in `extract.mjs` into a directory. The extractor verifies the blobs
before use. The interpreted placement list is also in the tracked proof.

```sh
d=/tmp/e1-cover
mkdir -p "$d"
node scripts/blender/e1-first-cover/extract.mjs /path/to/round-5-blockout > "$d/anchors.json"
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e1-first-cover/build.py -- "$d/anchors.json" "$d"
WSC_NODE_PROJECT=/path/to/pinned-engine-deps node --experimental-transform-types \
  scripts/blender/e1-first-cover/check.mjs "$d/art.json" "$d/geometry.json" "$d/proof.json"
cmp "$d/proof.json" project/layouts/e1-first-cover-cradle-proof.json
```

Only the cradle GLB, proof and authoring source need tracking. The more
detailed intermediate triangle dump is reproduced from both reimported GLBs.

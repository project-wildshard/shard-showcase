# Biscuit coat look board | WSC-ACTOR-019

W10a asks for a toon look board on the existing Nalati rig. W10's original
ride mockup shows orange mechanical head plates and cyan inserts from first
person; it does not show a whole horse. Amber Bay and Winter Dun are coat-only
options, not reproductions of those plates. Amber Bay is the warmer candidate
to pair with a bespoke headpiece if full mockup fidelity is still wanted.
No new model, tack geometry, animation, rider, placement or loan behavior is
included. The D24 boundary is the paddock and oval.

## Rebuild

Use the public project-wildshard/shard-nalati donor, exact commit
`7a718cbcdf1b09c08e240679a5a5b6f1a38fb352`, at
`public/assets/nalati/models/horse-saddled.phone.rigged.glb`.
Do not substitute the similarly named unrigged phone GLB. Expected donor
SHA-256: `7885a70507ef1ce6b6f4a87c72f9706b0a53785e934bc0803a964d3c75528bc2`.
Keep the donor outside this branch; no reason to embed a second copy.

From the repository root, with Python, Pillow (WebP support), NumPy, Node,
Blender 4.3, and a MeshoptDecoder ESM (e.g. Three's
`examples/jsm/libs/meshopt_decoder.module.js`):

```sh
S=scripts/blender/showcase-studies
python "$S/biscuit_coat.py" "$DONOR" "$OUT"
node "$S/biscuit_studio_decode.mjs" "$DECODER" "$DONOR" "$OUT/donor-preview.glb"
for name in amber-bay winter-dun; do
  node "$S/biscuit_studio_decode.mjs" "$DECODER" \
    "$OUT/biscuit-$name.glb" "$OUT/$name-preview.glb"
done
blender -b --factory-startup --python-exit-code 1 --python "$S/biscuit_look_board.py" -- "$OUT"
```

The recipe changes only the embedded coat and its dependent byte offsets.
The compressed geometry, skin payload, accessors and hierarchy remain exact.
The studio decoder expands Meshopt only for Blender. Each of the three
reimports has 5,000 triangles, 24 bones, matching vertex-group coverage,
and no embedded clips. Original is 263,288 B; test Amber Bay and Winter Dun are
286,404 B and 284,928 B, respectively. All exceed the 180,000 B target even
before any additional tack geometry is considered. Rig or LOD optimization,
native integration, gait and mounting proof are follow-up work. No model files
or generated intermediate caches are committed.

# W2b · The Gunsmith's starter sword

An outdoor display for the W1a Weapons keeper on Main Street. It holds the
existing WSC-GEAR-001 sword, turned flat and left as a separate instance.
Smoked oak, pressed felt, ivory enamel and champagne-brass inlay distinguish
it from Rook's forge samples across the road. No prices, level gates, purchases,
interaction or live installation.

The four .028 m feet straddle the old .022 m raised countercloth. The reimported
tray clears it by 6.5 mm at sampled points and sits at least 199 mm inside
the counter bounds. All 36 foot-pad samples hit the same tabletop height;
225 samples cover the full tray footprint. The original sword sits 0.4 mm
above the felt with at least 48.8 mm to its rectangle's edge. The 75,680-byte
textureless GLB contains only the removable tray (1,455 triangles; four
material primitives). Both keepers, fascia, counter and sword donor are
unchanged.

From the repo root, with Blender 4.3 and the repo's Node dependencies:

```sh
out=/tmp/gunsmith-sword-tray
mkdir -p "$out"
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-town/build.py -- --output "$out/town"
node scripts/blender/showcase-studies/decode_rook_for_street.mjs public/assets/wildshard-art/wsc-actor-018-tinker-rook.glb "$out/rook.glb"
WILDSHARD_TOWN_GLB="$out/town/whole-town-WIP.glb" WILDSHARD_ROOK_DECODED="$out/rook.glb" \
  blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/gunsmith_sword_tray.py -- "$out/review"
```

Set `WSC_METADATA_ONLY=1` to skip renders. The town must pass the original
W1a scene parity check; see `project/layouts/w2b-gunsmith-sword-tray.json`
for exact transforms, hashes and measurements.

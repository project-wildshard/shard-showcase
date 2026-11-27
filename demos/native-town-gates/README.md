# W0b: Six gate routes on the reconstructed West town

Run the stock player through the same six openings in two unchanged
tracked scene rebuilds. Source geometry becomes local Rapier colliders;
the host has no fallback ground plane. Inject a slab across the West
Gate as a negative control. Nothing adds or moves geometry in the game.

```sh
T=/tmp/w0b-town-gates
D=demos/native-town-gates
blender -b -t 8 --python-exit-code 1 --python scripts/blender/west-town/build.py -- --output "$T/shell"
blender -b -t 8 --python-exit-code 1 --python scripts/blender/west-range-scenery/build.py -- --output "$T/joined"
for K in shell joined; do
  B="$T/$K/whole-town-editable.blend"
  if [ "$K" = joined ]; then B="$T/$K/range-landscape-editable.blend"; fi
  blender -b "$B" -t 8 --python-exit-code 1 --python "$D/extract.py" -- "$T/$K/geometry.json"
  node --experimental-transform-types "$D/sample.mjs" "$T/$K/geometry.json" "$T/$K/native.json"
done
node "$D/summarize.mjs" "$T/shell/native.json" "$T/joined/native.json" "$T/proof.json"
cmp "$T/proof.json" project/layouts/w0b-native-town-gates-proof.json
blender -b "$T/joined/range-landscape-editable.blend" -t 8 --python-exit-code 1 \
  --python "$D/render.py" -- "$T/joined/native.json" "$T/media"
```

If engine dependencies are outside this checkout, set
`WSC_NODE_PROJECT` to their Node project (Engine 0.1.44). Rebuilds require
Blender 4.3.2. No cached Blend or GLB files are needed.

# W2b · Rook's parts drawer

A low walnut drawer with a petrol cloth lining and spare workshop stock
fits between the edge of the existing counter and the BENCH sign. The
drawer is a single removable GLB. The swatch tray, sign, countercloth,
storefront and actor are unchanged.

The 153 downward samples across the complete drawer footprint hit the
donor's countertop at 1.0295 m; place the base 0.5 mm above it. The
reimport leaves 18 mm to the BENCH sign and 30 mm to the front edge.
The unchanged sign and tray also reproduced their existing hashes.
The two drawer builds matched byte-for-byte: 69,272 bytes, 1,156
triangles, five primitives and no textures. This is set dressing only:
no pickup, ammo, interaction, purchasing or collision.

```sh
out=/tmp/rook-drawer
mkdir -p "$out"
cp public/assets/wildshard-art/wsc-actor-018-tinker-rook.glb \
   "$out/wsc-actor-018-tinker-rook-packed.glb"
node scripts/blender/showcase-studies/decode_rook_for_street.mjs \
  "$out/wsc-actor-018-tinker-rook-packed.glb" "$out/tinker-rook-decoded-for-blender.glb"
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/rook_counter_drawer.py -- "$out"
cmp "$out/w2b-rook-counter-drawer-proof.json" project/layouts/w2b-rook-counter-drawer-proof.json
cmp "$out/w2b-rook-counter-drawer.glb" public/assets/wildshard-art/w2b-rook-counter-drawer.glb
```

Set `WSC_METADATA_ONLY=1` to skip the staged images.

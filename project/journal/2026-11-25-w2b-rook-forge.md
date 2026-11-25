# W2b · Forge tray and BENCH placard

Two separate fixtures for the existing street-facing Tinker Rook
counter. The swatch tray labels Forge I–IV in approved order: Iron,
Steel, Alloy, Titanium. The header says ALL WEAPONS to distinguish
the shared ladder from the Gunsmith's individual gear. The independent
BENCH stand says AMMO ONLY. Its enamel tile and lettering are named
separate meshes, not fused to the oak carrier or brass studs.

The original actor, frame 19, countercloth, pots and storefront are
unchanged. Across both footprints, 234 downward ray samples hit the
actual donor at exactly 1.0295 m, with a nominal 0.5 mm offset above it
to avoid depth fighting. Edge separation: 102 mm from the pots to the
tray and 125 mm from the tray to the stand. Both independent models
are grounded at local zero and contain no textures or external assets.

| GLB | Bytes | Triangles | Draws |
|---|---:|---:|---:|
| Forge tray | 112,784 | 2,184 | 8 |
| BENCH placard | 45,412 | 844 | 4 |

```sh
out=/tmp/rook-forge
mkdir -p "$out"
cp public/assets/wildshard-art/wsc-actor-018-tinker-rook.glb "$out/wsc-actor-018-tinker-rook-packed.glb"
node scripts/blender/showcase-studies/decode_rook_for_street.mjs \
  "$out/wsc-actor-018-tinker-rook-packed.glb" "$out/tinker-rook-decoded-for-blender.glb"
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/rook_forge_fixtures.py -- "$out"
node project/check-rook-forge.mjs
```

Set `WSC_METADATA_ONLY=1` for a no-render pass. The scene reimports the
exports, and Three.js checks the identical distributable files. See
`project/layouts/w2b-rook-forge-fit.json` for exact transforms and hashes.
These are venue props, not prices, in-game shop panels, owned upgrades
or crafting behavior.

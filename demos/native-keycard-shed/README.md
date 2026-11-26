# E5b · Enter the foreman's keycard shed

The original WSC-PROP-065 presents a closed panel with no walkable
entrance. This optional same-origin variant cuts the existing panel,
keeps the rest of the shell, and adds steel jambs and a textured-looking
but texture-free folded ramp to the original 214.5 mm sill. An editable
triangle-clipping script preserves normals, materials and UVs outside
the cut. The original model is untouched. The variant is 579,400 bytes
and 8,420 triangles. It doesn't include the existing desk or keycard,
whose glTF placements are in the receipt.

All 195 directional doorway rays hit the closed donor and cleared the
cut variant. Six round trips (three offsets at 62% and full stick)
used the stock 0.38 m-radius character motor over the post-export
shell and desk triangles. No airborne ticks were recorded. Each run
saw the same keycard on the mat from inside at 1.23–1.26 m eye distance.
The same center line stalled at the original panel. All tests are local
to the hut, not a walk through the Stealth Yard.

The thin ramp and interior use the model's original scale. Keep the
desk and keycard independently selectable. Moving the card off the desk,
pickup interaction, stealth, alarms, player-controlled doors, Vault
unlock, phone play and game integration are not part of this pass.
Exact triangles are used to prove the art fit, not as a recommendation
for the shipped collider budget. Preview lights and cyan foot path are
not in the GLB.

```sh
D=/tmp/keycard-shed
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python demos/native-keycard-shed/build.py -- "$D"
WSC_NODE_PROJECT=/path/to/pinned/node/deps \
  node --experimental-transform-types demos/native-keycard-shed/sample.mjs "$D"
cmp "$D/walk.json" project/layouts/e5b-keycard-shed-walk.json
cmp "$D/e5b-keycard-shed-open.glb" public/assets/wildshard-art/e5b-keycard-shed-open.glb
WSC_SHED_RENDER=1 blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python demos/native-keycard-shed/build.py -- "$D"
```

Uses Blender 4.3.2, Wildshard Engine 0.1.44, and the matching Rapier and
Three.js packages. No cooked game or external plan assets are necessary.

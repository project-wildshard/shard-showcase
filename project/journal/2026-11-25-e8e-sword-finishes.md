# E8e: two common-Sword finish concepts

Warden comes from the Vault chest; Hot Mess earns its own Sword
finish in the night-elite loot list. The concept direction is cold
graphite and cyan for the Warden, warm oxide and copper with a small
ember accent for Hot Mess. These are proposed palettes, not recovered
or approved appearance references. They do not replace the separate
Titan Cleaver or represent a Titan gold finish.

The two textureless previews change only five named material records.
Both keep the exact 34,488-byte geometry buffer, indices, bounds,
inventory pivot, material names and bindings. Both leather materials
remain unchanged. Blender and Three.js reimport the authored outputs;
matched 64 px camera renders check that the color treatments can be
distinguished without changing the silhouette.

This is static inventory art, not the first-person Sword or working
Bag, acquisition, equip, finish-card, or held-render integration.
The exact held material labels and client flow still need their own
test. Do not use these binary inventory models as a substitute for
the gameplay Sword.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/sword_finish_review.py -- /tmp/e8e-sword
python scripts/blender/showcase-studies/sword_finish_boards.py /tmp/e8e-sword
node scripts/blender/showcase-studies/check_sword_finish_materials.mjs /tmp/e8e-sword
```

Board assembly uses Pillow and DejaVu Sans on the review machine;
the materials and GLBs do not depend on either.

[Reward table](../../docs/plans/kitchen-sink-v2/loot-economy-mini-plan.md#numbers)
· [Finish scope](../../docs/plans/kitchen-sink-v2/slices/E8e-finishes-titles.md)
· [Validation receipt](../layouts/e8e-sword-finishes-proof.json)

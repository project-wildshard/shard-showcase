# W3b / W4a: West range refill crate

The W3b/W4a plan calls for a refill crate at the range, separate from Tinker Rook's BENCH. The asset is a cedar crate with iron skid feet, a center divider, two open wells, and an enamel REFILL plaque. The separate stock layer is a decorative suggestion with blunt simplified silhouettes. Both assets use a common ground-centered origin; use an identity transform to fit the stock, or omit it for empty wells. The plaque indicates the intended art role, not an implemented interaction.

Reimport verified both models, the grounded skid seats, 50 unobstructed rays into the two empty wells at 0.346 m, and that the decorative stock stays inside the wells' horizontal bounds. Whole crate bounds: 1.272 × 0.741 m in plan. Crate: 158,956 B, 2,782 triangles, six primitives. Stock: 10,836 B, 160 triangles, three primitives. No images, animations, or external dependencies.

```sh
d=/tmp/w3b-refill
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/range-refill/build.py -- "$d"
cmp "$d/w3b-range-refill-crate.glb" public/assets/wildshard-art/w3b-range-refill-crate.glb
cmp "$d/w3b-refill-display-stock.glb" public/assets/wildshard-art/w3b-refill-display-stock.glb
cmp "$d/w3b-range-refill-proof.json" project/layouts/w3b-range-refill-proof.json
```

Use `--no-render` to skip Blender preview images. The staging set is not a real range location. No actual refill, inventory behavior, economy, collider, map placement, reload function or new stable catalogue ID.

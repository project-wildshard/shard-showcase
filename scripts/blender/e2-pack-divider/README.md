# E2 · 3 m Pallet Jack pack divider

The E2 plan calls for opaque 3 m separation between close packs. This optional crown and seam kit reuses the exact MODULE-020 orange corrugated bay unchanged. Place both GLBs at the same ground-level origin and yaw, with bays on 2.375 m pitch along local +X. The cap sits within the original bay's depth and the graphite seam plates run to grade. Rims and rivets use separate zinc material; the orange cassettes are solid, not lights.

The supplied proof checks three repeated bays in local coordinates. At 1.70 m, 282/310 original rays hit; the assembly blocks all 310. Across nine sampled heights and two directions, including the joins, the count is 1,986/2,790 original and 2,790/2,790 assembled. Five above/beyond-end controls stay clear. The results apply to the tested visual mesh; they do not show a live collider, aggro behavior, charge stun, map placement, or phone playability. Pallets in renders are unchanged preview context.

```sh
d=/absolute/scratch/e2-divider
blender -b -t 4 --factory-startup --python-exit-code 1 --python scripts/blender/e2-pack-divider/build.py -- "$d"
cmp "$d/e2-pack-divider-crown.glb" public/assets/wildshard-art/e2-pack-divider-crown.glb
cmp "$d/proof.json" project/layouts/e2-pack-divider-crown-proof.json
blender -b -t 6 "$d/divider-review.blend" --python-exit-code 1 --python scripts/blender/e2-pack-divider/render.py -- "$d"
```

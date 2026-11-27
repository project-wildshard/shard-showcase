# W3b · A lighter bullseye with unchanged rings

Four planned practice lanes share the WSC-PROP-025 model. The alternate
trims the pewter and graphite hardware only; keep the original for
close views. The board, painted face and rim are left at their original
coordinates with identical UV assignments and byte-identical JPGs.

- 7,688 → 3,212 triangles (58.22% fewer).
- 516,872 → 343,408 bytes (33.56% smaller per distinct export, not per instance).
- All 1,296 board/rim triangles match by position, material and UV after
  GLB reimport. The maximum local bound change is 1.51 mm at metal hardware.
- Six orthographic azimuths × 23,040 rays give at least 98.56% silhouette
  intersection-over-union against the untouched donor.

The matched 10, 30 and 50 m portrait renders serve as visual checks.
This is an opt-in prop only, with no installed lane, switch distance,
collision changes, scoring, draw-call or phone frame-rate claims.

```sh
O=/tmp/w3b-bullseye-distance
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/range_bullseye_distance.py -- "$O"
cmp "$O/proof.json" project/layouts/w3b-bullseye-distance-proof.json
cmp "$O/wsc-prop-025-bullseye-distance.glb" public/assets/wildshard-art/wsc-prop-025-bullseye-distance.glb
```
Append `--proof-only` to skip stills.

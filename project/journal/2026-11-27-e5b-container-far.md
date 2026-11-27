# E5b · A farther shipping container for the stealth yard

The original PROP-058 container stays in the catalogue as the near
mesh. A separate far model keeps the original origin, orange material
colors, overall dimensions and 2.5 mm ground offset. Formed strips
replace stacks of individually beveled ribs. The door seam, locking
bars, corner sockets and roof ribs remain; tiny labels and edge wear
are simplified. This is a material-only GLB without textures.

| Mesh | Triangles | Bytes | Material primitives |
|---|---:|---:|---:|
| Near donor | 10,849 | 637,956 | 11 |
| Far candidate | 1,188 | 68,712 | 6 |

The far mesh removes 89% of the triangles and 89% of file bytes.
Blender reimports both. The local bounds are identical, and the
intersection-over-union of three orthographic silhouettes is 98.39%,
98.70% and 97.46% from +X, +Y and +Z (6,561 probes each). Matched
comparisons at 15 m and 32 m show which near marks are lost. The three
existing yard placements can use the same pivot without changing the
layout. Keep the near mesh for close cover and interaction reads.

No distance switch, culling, shadow-state, collision, patrol or phone
frame rate change is installed. Bounds alone do not make the far mesh
a collider.

```sh
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e5b-container-far/build.py -- /tmp/e5b-container
cmp /tmp/e5b-container/wsc-prop-058-shipping-container-far.glb \
    public/assets/wildshard-art/wsc-prop-058-shipping-container-far.glb
cmp /tmp/e5b-container/e5b-container-far-proof.json \
    project/layouts/e5b-container-far-proof.json
```

Append `--proof-only` to skip the four matched stills. The source
container and existing shadow-pool scene remain untouched.

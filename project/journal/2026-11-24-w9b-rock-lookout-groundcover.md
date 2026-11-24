# Rock lookout groundcover: bearberry and heather

W9b vista dressing for the Rock, paired with the original W11 look study. The existing fern, grass, lupine, buttercups, trees and sandstone are unchanged. Trailing bearberry adds a flatter cover shape with broad evergreen leaves and red berries. Heather provides a low woody mound with wine-colored buds, not another tall flower spike.

| Mesh | GLB bytes | Triangles |
| --- | ---: | ---: |
| Bearberry | 37,340 | 456 |
| Bearberry simplified | 28,924 | 348 |
| Heather | 65,496 | 832 |
| Heather simplified | 45,220 | 572 |

Deterministic seeds keep major stems or runners aligned between both detail tiers. The lower tiers remove interior leaves and small buds and broaden retained foliage rather than scaling the entire clump. No textures; both meshes are grounded at the scene origin and use meter units. Reimport with Three.js checked all four exports for triangle counts, non-textured material and grounded bounds. These are optional dressing assets, not automatic runtime LOD or a change to collisions, vistas, discoveries or collectibles.

Rebuild the GLBs and the two disposable studio previews (Blender 4.3+):

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/lookout_groundcover.py -- /tmp/w9b-groundcover
```

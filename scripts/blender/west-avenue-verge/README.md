# W0b · Dry leaf litter for the avenue paving

Optional street dressing for WSC-MODULE-004. The existing 4.2 × 7.2 m avenue donor, deciduous oak and planter remain unchanged. Warm oak-style leaves use one colored material per insert with no image textures, skins or animation. The west windrow carries 78 leaves / 936 triangles / 43,472 bytes; the east drift uses 41 / 492 / 23,480 bytes. Each insert shares the donor pivot. At identity together they leave the central 2.585 m clear of litter. Rotate or move them with their paving module, or re-fit to alternate paving rather than reusing the same offsets.

From the art checkout with Blender 4.3.2:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/west-avenue-verge/build.py -- /tmp/avenue-litter
```

Set `WSC_LITTER_ONLY=1` to skip lighting and rendering. The script verifies exact donor hashes, rays 13 vertices and 12 triangle centers per leaf against the real paving, repeats the checks on reimport, and exports a fit receipt. Scanned point clearance was 1.89–19.28 mm. Both exported GLBs and the receipt reproduced byte-for-byte. The preview planter, tree, neighboring paving sections, soil and stage are not part of either GLB.

Static overlays only: do not attach collision. No change to installed street, weather, gameplay or phone performance.

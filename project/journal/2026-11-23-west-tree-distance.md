# Distant deciduous and conifer trees (WSC-PROP-012 / WSC-PROP-046)

Measured low-detail alternatives, not replacements for the tracked
near tree models used by the M02 and W11 studies. The builder pins and
reimports both original GLBs. It keeps complete leaf or spray islands
distributed across the canopy and reduces wood less aggressively on
the conifer. Both alternate exports preserve the same ground datum;
no original tree asset is edited.

| Tree | Raw GLB near → far | Triangles near → far | Worst silhouette agreement |
|---|---:|---:|---:|
| Deciduous | 357,584 → 169,260 B | 4,790 → 2,219 | 98.5% |
| Conifer | 645,780 → 344,240 B | 17,268 → 9,654 | 96.3% |

Two elevations and eight evenly spaced azimuths cast reimported
Blender silhouettes, including empty samples beyond projected model
bounds. Agreement is intersection over union per sampled view, not
material fidelity or a performance measurement. Both models retain
the source ground at y=0 in glTF; oak max bounding coordinate
difference is 0.0468 m, conifer unchanged to 0.1 mm.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/tree_distance.py -- /tmp/wsc-tree-distance
```

No textures, wind, collision, placement, distance selector or FPS
claim. Any native adoption needs a screen-space threshold and a
moving-camera pop check; this commit does not choose a switch distance.

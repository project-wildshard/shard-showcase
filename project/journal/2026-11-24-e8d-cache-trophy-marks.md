# E8d: two cache marks and their locked silhouettes

The plan reserves two places for secret cache trophies.
These are proposed compass and clasp reliefs, not assigned
items or identified cache rewards. The comparison uses two
copies of the exact shared 12-frame donor. It does not alter
the existing plaza, Big Pallet trophy or mount geometry.

The two earned shapes export as distinct meshes in a single
20,188 B GLB (308 triangles). Both have a ground-independent
centered backing plane and face +Y in Blender. The preview
seats each 8 mm ahead of the mount's forward surface, with
at least 55 mm to the interior frame edges. On import, reset
the exhibit offset on the second object before placement.

The locked image uses flat outline cuts derived from those
same shapes. The camera, frame and lights do not move. No
unlock system, perk, final naming, loot or native attachment.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/cache_trophy_marks.py -- /tmp/e8d-marks
```

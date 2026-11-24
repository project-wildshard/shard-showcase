# West inventory: Sword and Spear

WSC-GEAR-001 and 002 get their first linked inventory studies. W3a
supports the two families; the provisional catalogue turnarounds,
not the W06 crossbow photograph, inform these silhouettes and colors.
Neither model replaces the private yard or native held-weapon assets.

- Sword: broad satin silver facets, dark maker mark and orange wrap.
- Spear: blue-iron leaf silhouette, brown shaft and garnet pennants.

A single Blender script emits both static visual meshes with repeatable
seam, facet and pennant geometry. Each GLB has a zero origin for preview
placement, one mesh, no texture fetches and no decoder requirement.
Both were reimported to verify primitive and triangle counts. The
dimensions are provisional art proportions, not validated equip poses.
No first-person hands, animation, gameplay or economy wiring changed.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/west_inventory_pair.py \
  -- /tmp/west-inventory
```

See the tracked proof JSON for output bounds, sizes and triangle
counts. Both catalogue frames render the reimported exports.

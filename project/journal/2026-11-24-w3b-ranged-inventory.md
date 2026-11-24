# W3b: Bow and Crossbow inventory meshes

WSC-GEAR-003 and WSC-GEAR-004 had provisional four-view catalog
art and no linked 3D studies. These original static models carry
the catalogue silhouettes forward: walnut recurve with brass
trim, and a compact blued-iron / walnut crossbow with a cyan
shard emblem. They are decorative, nonfunctional meshes.

| ID | GLB bytes | Triangles | Material primitives |
| --- | ---: | ---: | ---: |
| WSC-GEAR-003 | 49,888 | 864 | 5 |
| WSC-GEAR-004 | 52,596 | 924 | 7 |

Both are below their 65,536 byte inventory budgets. They embed no
textures, skins or animation. The geometry and material source,
not a temporary .blend, is checked in. The renders use the exact
reimported inventory exports rather than a separate high-detail
model. In Three.js both GLBs parse with the same counts and
axis-converted bounds as Blender. See the [rebuild receipt](../layouts/west-ranged-inventory.json).

Rebuild from the repository root in Blender 4.3.2:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/west_ranged_inventory.py \
  -- /tmp/ranged-inventory
```

Use `WILDSHARD_VALIDATE_ONLY=1` for mesh exports and validation
without the gallery renders. With repository dependencies installed,
run `node project/check-ranged-inventory.mjs` to verify the committed GLBs. These do not implement or replace
the W3b weapon family, held/equip poses, hands, animation, draw,
reload, projectiles, or game integration.

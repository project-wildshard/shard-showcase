# E01–E06 East material key (WSC-SCENE-005)

The six archived portraits have distinct ground treatments that
are easy to miss in the small references: warm pavers, dusty
yard, pale dock paving, red brick, cool slab and a red coated
court. A six-card Blender study puts those treatments under
the same light. Each card gets a display prop and a repeat of
the cyan robot dock; source IDs and exact binary hashes are
pinned in the layout. The prop combination is editorial and
not proof that every donor matches an original screenshot.

The scene recipe pins the archive, model checksums, and card
palettes. Verified seven reimported source models and bounds
for their fitted stage placements. All existing props stay
unchanged. There is no repeated GLB, texture bake, or .blend
cache in Git.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/east_material_key.py -- /tmp/wsc-east-material-key
```

This is a look-development board, not the approved band map,
level layout, combat route, or an asset-ready encounter. No
actors, behavior, physics, lighting integration or characters
were authored.

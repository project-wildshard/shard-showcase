# Training Vault: Room 2 environment and threshold

A proposed static shell for the middle room in E10c, within D41's
expanded envelope. Reuse linked PROP-064 tiles in a 5 × 5 grid, the
industrial bays, and the existing bulkheads. The odd tile count puts
the centerline on a tile interior. Those models remain unchanged.
The room footprint and its western interface are not native anchors.

The unchanged Room 3 recipe is run in measurement-only mode. The new
threshold spans 2.432 m, with a deliberate 3 mm seam before its tread.
The nominal top is world y −48.994 m, rather than the donor's maximum
embossed height. Measure both joining edges at y = −0.6, 0 and +0.6 m
in the Blender cross-axis. The reimported threshold has no surface
intersection with the nearby assembled Room 3 meshes. Fifteen visual
rays also pass through the staged open bulkhead donor. These checks
do not qualify native collision or movement.

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/vault_room_two.py -- \
  /absolute/scratch/vault-r2
```

Only new support and threshold pieces enter the small GLB. The linked
room is rebuilt by the script, which also renders the floor-eye and
roof-off plan. No working doors, Room 1 connection, waves, enemies,
checkpoints, or native placement are authored here.

# E10c Training Vault: room 1 (WSC-KIT-008)

First of the interior room studies. This is a Blender composition and
resource reuse check, not a game-level submission. Read main's E10c and
[the original puzzle frame](https://github.com/Raynos/project-wildshard-singleplayer/blob/4e548db8b53c1070c7d7e5c370472737b8171bb5/art/showcase-template/round-2-mini-dungeon/02-puzzle-room.jpg)
together. The reference shows amber sidewalls, one weighted plate and one
empty, a locked door, and a second crate near the entrance. The finished-art
translation uses this project's existing round bulkhead in place of the
mockup's rectangular placeholder.

- Room shell reference: 9.46 × 12.62 m; center light optic at 4.025 m.
- Floor plates, industrial wall bays, closed vault bulkhead, pressure plate
  and cargo crate are the five existing GLB sources. Repeated parts share
  Blender mesh data. Source hashes and explicit placements are recorded in
  `project/layouts/e10c-vault-room-01.json`.
- Two 2 m study-scale plates have a 2.40 m central gap. A is visually depressed
  25 mm, supports a crate and shows green. B is empty and amber. A spare
  crate is depicted on the floor near the start. These are illustration
  transforms, not new puzzle tuning. No changes to the donor files.
- New small asset: `wsc-kit-008-puzzle-indicators.glb`, a paired enclosure and
  color-state sample for the bulkhead. Reimport: 58,136 bytes, 1,080 triangles,
  1.33 × .157 × .23 m (Blender X/Y/Z); both materials intact. No callbacks.
  The complete composition is regenerated from source rather than stored
  as a second copy of the reuse assets.

From the Showcase repo root, with Blender 4.3.2:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/vault_puzzle_room.py -- /tmp/vault-room
```

The script writes the indicator GLB, a layout JSON, and two studio renders
(entry camera and cutaway). Build from the pinned source files in layout
JSON if a donor is revised. No runtime floor collision, crate physics,
plate logic, door state, checkpoint, or traversal was run. Fight and climb
rooms and the Warden are not part of this batch.

# W1a: Yard Boss and Shift Boss

WSC-ACTOR-015 and 016 fill the two remaining model studies in the
West plaza quest-giver trio. Both share the existing 21-joint skeleton,
one skinned primitive and a 3 s studio idle. This pair uses one new
deterministic safety-vest palette; the existing Surveyor and Tinker
Rook packed exports and stable/keeper authoring exports rebuild
byte-for-byte unchanged.

| Role | Visible design from provisional sheets | GLB | Triangles |
| --- | --- | ---: | ---: |
| Yard Boss (L1–6) | Rounded visor, zipped vest and two patch pockets | 129,404 B | 3,992 |
| Shift Boss (L13–20) | Squared visor, yellow vest edging, large cuffs/boots | 152,092 B | 4,208 |

The packer verifies exact decoded geometry, winding, weight accessors,
inverse binds, sampler times and values. A separate reader checks the
21-joint topology, normalized skinning and clip duration and continuity.
Both tracked packages need a Meshopt decoder.

W01 frames Shift Boss, Surveyor, board, Yard Boss left to right, with
one gold marker on Yard Boss at level one. The staging uses that order
at a 1.7 m eye height, with the existing Surveyor and board (scaled to
81% for the shot). It is not the historic round-4 layout or a native
accepted scene. The prop reads CONTRACTS because the existing board
export does. The marker is art direction, not an implemented quest state.
Shift Boss is a town NPC, not the hostile E11 Shift Supervisor.

D12 approves Gunsmith Brass and Stable Bot Hay as the names for the
previous keeper/stable studies; their asset IDs and files remain intact.
No dialogue, posed-talk host binding, native placement or game deploy.

Build from repository root (Blender 4.3.2; Node with @gltf-transform
core/extensions/functions 4.5.0; meshoptimizer 1.2.0):

```sh
S=scripts/blender/showcase-studies
O=/tmp/quest-trio
WSC_TOWN_QUEST_GIVERS=1 blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python "$S/town_bots.py" -- "$O"
node "$S/surveyor_pack.mjs" node_modules "$O" yard-boss
node "$S/surveyor_pack.mjs" node_modules "$O" shift-boss
python "$S/check_town_bots.py" "$O" --quest
node "$S/surveyor_pack.mjs" node_modules "$O" surveyor --exact-surveyor \
  public/assets/wildshard-art/wsc-actor-017-surveyor.glb
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python "$S/quest_trio_reimport.py" -- "$O"
```

The two `-packed.glb` files are tracked without the `-packed` suffix.
The raw/decoded GLBs, atlas PNGs and Blender scenes stay out of Git.

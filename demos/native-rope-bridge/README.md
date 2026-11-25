# West Movers Station 6: native room bridge bench

The original room bug had a client deck with no server bodies.
This bench goes through Engine 0.1.44's normal room composition,
`openWorldAdapter → openCellWorld → prepareNativeRuntime`, so it
does not make a passing bridge by installing its own chain.

It overlays schema-checked Format 0.43.0 deck/chain stages on an
already built local calibration product. The stock product is
loaded through the cooked-folder reader; the synthetic client
plan and server assembly rows are added in memory. The declared
native assembly builds only the two static endpoint slabs at
18 m. There is no static floor between them. The test places
the lead on the departure slab for the fixture; all movement
thereafter is ordinary native input. No game or engine changes.

Use the same pinned installation and local fixture as
[the native Mite bench](../native-mite/README.md). From the repo:

```sh
WSC_NODE_PROJECT=/path/to/installed-project node --experimental-transform-types \
  demos/native-rope-bridge/sample-crossing.mjs \
  /path/to/built/mite-calibration /tmp/bridge-18.json
```

Set `WSC_BRIDGE_LINKS=27` or `54` to replay the comparisons.
54 writes its trace then fails the crossing envelope. The exact
anchors are (-168,18,-103) and (-190,18,-104), 22.023 m apart.
The contact deck is 1.6 m wide; the rest chord sag is 0.65 m.

| Physical links | Lowest feet | Interior contact lost | Awake peak | All asleep after exit |
| ---: | ---: | ---: | ---: | ---: |
| 18 | 17.183 m | 0 ticks | 18 | by 9 s |
| 27 | 17.107 m | 0 ticks | 27 | by 11 s |
| 54 | 16.747 m | 1 tick | 54 | by 11 s |

18 preserves all 54 visual planks (three per body) with the
smallest sag and peak of these three. It takes 319 ticks (5.32 s)
from first deck contact until the lead is 0.8 m onto the far slab.
The midpoint save restores one chain, 18 bodies and 19 joints;
all link transforms and player feet match the uninterrupted room
for 166 tested ticks. An old room with no chain falls through
the gap; restoring its untouched save against the bridge rows
builds exactly one chain and the lead crosses. If the authored
bridge builds ahead of further testing, keep it off gameplay
until client poses and multiplayer reconciliation are proven.

For review images, rebuild the pinned [existing art source](../../scripts/blender/west-movers-roof/README.md).
Pick the assembled junction's verified `west-shared-roof-WIP.glb`:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python demos/native-rope-bridge/render-crossing.py -- \
  /path/to/junction/west-shared-roof-WIP.glb /tmp/bridge-18.json /tmp/bridge-review
```

The render reconstructs a measured pose from the room and places
the original boards on the links. The lines and markers are for
review, not a native client or an in-game effect. Not tested:
reverse and off-center walks, multiplayer/prediction under lag,
camera sway, the five-span aggregate, or frame time on phones.
`project/layouts/w6c-room-bridge-proof.json` is the compact receipt;
no generated traces or duplicate scenery go into Git.

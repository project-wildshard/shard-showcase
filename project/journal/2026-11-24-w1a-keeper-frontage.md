# W1a · Main Street's opposite vendors

Round 5 `ce1cf050b3` `layout.js` lines 160–177 places the Weapons keeper at x/z (−64, 3.5) and Tinker Rook at (−64, −3.5). The authored facade and paving come from the exact whole-town rebuild; its normalized semantic parity passes. The positions are 7 m apart. A 180° yaw faces the keeper towards the street center, while Rook retains the studio +Z forward toward the opposite vendor. Both originals have 21 joints and one studio idle clip; same sampled frame 19, reposing and grounding only. The unskinned studio plinth is excluded. No new model, runtime actor, shop layout or animation.

The exact Oak display counter is 2.380 × 0.849 × 1.052 m. A preliminary y=−5.25 location crossed the modeled kerb and gave uneven support readings. I moved the counter 0.55 m forward in Blender y to −4.70 without moving either actor. Nine floor samples now agree at y-up .056 m; facade samples have at least 1.06 m clear, and the counter/posed keeper bounds have 0.446 m separate along X. This is a static mesh fit, not an interaction or traversal test. No shop stock, spawning, NPC navigation, collision, or native level change.

From the repo root:

```sh
mkdir -p /tmp/west-keeper
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-town/build.py -- --output /tmp/west-keeper/town
node scripts/blender/showcase-studies/decode_rook_for_street.mjs public/assets/wildshard-art/wsc-actor-018-tinker-rook.glb /tmp/west-keeper/rook-for-blender.glb
WILDSHARD_TOWN_GLB=/tmp/west-keeper/town/whole-town-WIP.glb \
WILDSHARD_ROOK_DECODED=/tmp/west-keeper/rook-for-blender.glb \
  blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/keeper_street.py -- /tmp/west-keeper/review
```

The stage requires the town's parity receipt and pinned donor hashes. Validation-only mode skips renders; the measurement JSON matches the full run. No decoded copy, whole town model, or native blend file is added to Git.

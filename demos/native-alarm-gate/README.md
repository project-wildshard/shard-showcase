# E5b native crossing bench

The unmodified WSC-KIT-006 pair is loaded in Three.js at Engine 0.1.44's
60 Hz step. Both authored anchors and yaws are tested on isolated flat slabs.
Close and open are the exact 2.4 s and 2.8 s animation clips; the test waits
20 s at the fully closed pose. That hold is a fixture, not an AI alarm.

Using each moving GLB leaf as a kinematic trimesh blocked straight travel
when shut, but reopening with the player still against the gate pulled the
player sideways by 7.66–8.13 m in four of six runs. Those four could not take
the same straight path afterward. A roughly 1.6 m retreat before reopening
allowed six of six crossings; contact with the shut mesh can still bump
player feet off the floor. In two other runs, a close request while the
player was in the doorway was delayed by 20 ticks until the player cleared.

The comparison keeps both animated leaves visual-only. One fixed, floor-
centered blocker (half extents 8.12 × 1.90 × .135 m) is enabled fully closed
and disabled when the opening reaches at least 2.05 m. In all 12 tests it
blocked the closed walk and cleared the reopened route, with zero airborne
ticks. Holding forward crossed 45 ticks into opening at a 2.87 m gap.
This is the better of the tested alternatives for the central approach.
Entry during the closing clip, side routes through opening leaves,
multiple actors, terrain and authoritative alarm wiring remain unproven.
Do not install this test's timing without checking those cases.

```sh
d=/tmp/e5-cross
mkdir -p "$d"
WSC_NODE_PROJECT=/path/to/pinned-engine-deps node --experimental-transform-types \
  demos/native-alarm-gate/sample.mjs "$d/proof.json" "$d/trace.json"
cmp "$d/proof.json" project/layouts/e5b-native-gate-crossing-proof.json
WSC_E5B_MOTION_GLB="$PWD/public/assets/wildshard-art/e5b-alarm-gate-pair-motion.glb" \
WSC_E5B_CROSS_TRACE="$d/trace.json" blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/stealth_alarm_gate.py -- "$d"
```

The overlays are straight connections between recorded player positions,
not interpolated motion or in-game VFX. Gates and scene assets are unchanged.

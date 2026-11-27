# W5a: ride the D7 launch channel from inside

This stock-engine fixture reuses one tracked launch-wall GLB at both
original toe anchors (east x=-216, west x=-224 with yaw π, z=142.5).
It keeps the authored 45 m × 8 m flat channel, including its 23.5 mm
surface height. Beyond the walls, the test paving is an undressed
flat witness, not the Hover Park terrain.

From the channel midpoint, start the stock board and drive toward
either wall. Test five release distances from 2.60 to 1.45 m before
the toe on three lines. Pause for 140 ticks before returning at
30% stick. The fixture releases that return input near the center
based on the remaining distance and speed; it does not teleport,
change the motor, or add an automatic brake to the game. All 30
returned to rest within 0.30 m of center at full health. Releasing
only at the toe crossed the crest in all six installed controls;
the two mesh-removed controls never reached 0.64 m feet height.

The tiny inlay GLB adds only floor marks at the tested midpoint of
the release band (2 m before either toe). It has no collision or
input logic. Don't infer that a rider can read or time it on a
phone. This is not a vert halfpipe, complete trick loop, or installed
level. The Blender renders stage the same walls, channel and cue
with a parked board for scale.

```sh
D=/tmp/w5a-channel
mkdir -p "$D"
WSC_NODE_PROJECT=/path/to/pinned-engine-deps node --experimental-transform-types \
  demos/native-hover-channel/sample.mjs "$D/proof.json" "$D/replay.json"
cmp "$D/proof.json" project/layouts/w5a-launch-channel-proof.json
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python demos/native-hover-channel/build.py -- "$D/proof.json" "$D"
cmp "$D/inlay.json" project/layouts/w5a-launch-channel-inlay.json
```

The exact wall generator and parity receipt are described in the
[original two-wall extraction](../../project/journal/2026-11-23-d7-launch-wall.md).

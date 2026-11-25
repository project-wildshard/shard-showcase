# W6b jump-pad art and engine calibration

The editable vector overlay sits 2.5 mm over the exact existing
jump-pad lid, checked with 1,764 downward sample rays on the
reimported mesh. The second asset is the two-part amber landing
index plus cyan edge dashes, contained by the destination deck.
They are static, texture-free visual layers; no new collisions.

The three pad centres at x −104, −110, −116 and the 4 × 8 m
ledge at x −121 match the current West Movers Roof checkout
(`scripts/blender/west-movers-roof/movers.py`), with world
z −103 and the deck top at 6 m. Round 5 called this the
6 m ledge but drew an earlier 6 m-long slab, whose actual
top was 5.7 m; do not substitute its dimensions into this test.

The renderer-free bench uses the pinned Engine 0.1.44 SimHost,
real 0.38 m capsule/KCC, current gravity/impulse law and 60 Hz
clock. A single impulse is issued on each stationary pad with
verified contact. No airborne steering. In each fresh repeat,
first ledge contact is tick 40 (0.667 s), and the maximum feet
height is 7.49 m. Raw impulse lingers and the controller reports
27 subsequent airborne ticks before settling. A second experiment
clears the test impulse on confirmed ledge contact and reports zero
subsequent airborne ticks. This is a candidate contact handoff
rule in the harness only, not a gameplay or engine behavior change.
The raw input speeds are deliberately tuned extremes for calibration,
not recommendations for responsive player movement.

Format 0.43.0 rejects the planned `launch` traverse row. The bench
calls the existing impulse service directly instead. Requires a
real trigger, launch/cancel and contact ownership, authored
landing safety, client parity, and phone/run-time checks before
shipping. Keep the pinned package versions as they are.

```sh
node --experimental-transform-types demos/native-jump-pad/sample-flight.mjs /tmp/w6b-trace.json
blender -b -t 6 --factory-startup --python-exit-code 1 --python \
  demos/native-jump-pad/render-pads.py -- /tmp/w6b-trace.json /tmp/w6b-pads
node demos/native-jump-pad/check-exports.mjs /tmp/w6b-pads
```

Set `WSC_NODE_PROJECT` to the absolute pinned install if separate.
`project/layouts/w6b-jump-pad-fit.json` is the concise checked
record; generated traces and raw photography are not part of Git.

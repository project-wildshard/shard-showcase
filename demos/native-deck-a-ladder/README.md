# W8a: Deck A six-metre ladder bench

This isolated test reproduces the original Climb Yard deck, ground,
plank rim and guard opening in colliders. It runs the stock ladder
installer and real character motor from Engine 0.1.44, with a
Format 0.43.0-validated mode row. It does not add a game runtime
or change the canonical Climb Yard model.

**Product boundary:** the same row in the normal headless native
assembly room does not install the ladder in this version. The
control player stays below 0.05 m from below and falls from the deck
when walking off its top. For the positive case, the bench explicitly
lends the stock `installLadders` helper to the resident. That is
test wiring, not a fix for the normal room.

Starting on the ground, ordinary forward input meets the 0.9 m reach
and climbs the 6 m route. The player lands on Deck A at tick 244,
219 ticks (3.65 s) after starting forward. Mid-climb restore matches
117 following ticks exactly. Neutral input holds; jump releases;
a lane 1.5 m to the side does not grab. Going back down works, but the
edge transition is not polished: the largest single downward step
was 85 mm while aligning, versus 33.4 mm down the aligned middle
and 251 mm without the ladder. The test does not qualify the six
other ladders, touch behavior, presentation/animation, playtest feel
or simultaneous clients.

Use the same pinned dependencies and local admitted fixture as
[the native Mite bench](../native-mite/README.md). From this repository:

```sh
WSC_NODE_PROJECT=/path/to/installed-project node --experimental-transform-types \
  demos/native-deck-a-ladder/sample.mjs \
  /path/to/local/calibration-product /tmp/deck-a-trace.json
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-climb-rock/build.py -- --output /tmp/climb-base
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python demos/native-deck-a-ladder/review.py -- \
  /tmp/climb-base /tmp/deck-a-trace.json /tmp/deck-a-review
```

The amber markers in the images stand in for exact sampled foot
positions; the blue studs show measured intermediate positions and
the exit path. All markers are review geometry. Only this bench,
source and compact receipt are committed; the calibration product,
full trace and generated scenery are not.

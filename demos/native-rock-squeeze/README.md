# W9a · Rock cave clearance in the stock motor

Rebuild the 316-triangle collision liner from the unchanged static art
profile. Two flat test pads connect the archived north and south mouth
positions. The floor descends to 6 m below the mouths. The shaft opening
stays open. The test does not place the crag, punch the terrain or check
the decorative mouth shells.

- The stock 1.80 m capsule stopped on both sides of the 1.10 m
  squeeze in all twelve runs. Holding the actual version-1 crouch command
  slowed arrival but did not change capsule height or admit entry.
- The same native motor with a 1.02 m candidate capsule, substituted
  before the first tick, walked through the unchanged liner in all six
  runs (both directions, center and ±0.15 m). All six remained grounded
  and walked past the opposite mouth. This tests a size, not a stance
  switch and not a new gameplay implementation. Keep the art height
  until the runtime stance/clearance contract is decided.
- Source profile, generated proof and two repeat traces were checked.
  Render lines are sampled feet offset by 8 cm. The designer's cutaway
  is not a baked playable scene.

```sh
D=/tmp/w9a-native-squeeze
mkdir -p "$D"
WSC_NODE_PROJECT=/path/to/engine-0.1.44-and-rapier \
  node --experimental-transform-types demos/native-rock-squeeze/sample.mjs \
  "$D/proof.json" "$D/replay.json"
cmp "$D/proof.json" project/layouts/w9a-native-squeeze-proof.json
# Rebuild the editable crag per the static squeeze study journal first.
WILDSHARD_CAVE_REPLAY="$D/replay.json" blender -b /tmp/rock-source/climb-rock-editable.blend \
  -t 6 --python-exit-code 1 --python scripts/blender/showcase-studies/rock_squeeze_cave.py -- "$D"
```

No terrain integration, dynamic stand-up safety, multiplayer prediction,
Gold pickup, handheld playtest or new shipped mesh.

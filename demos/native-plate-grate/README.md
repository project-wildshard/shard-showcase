# W4a · Hold-only grate, native one-player rehearsal

D19 says park two crates and stand on the third tread. This bench runs
Engine 0.1.44 in a native headless resident, with Format 0.43.0 dependencies.
The local room contains the canonical three plate centers and simple static
colliders fitted to the known floor, depressed treads and closed grate
envelope. It does not install the full yard or operate the rendered mesh.

- Two real dynamic ITEM crates settle at 0.32242 m crate-bottom height.
  The stock plateOverlap misses them when called at the 0.0345 m floor
  stripe (query top 0.1845 m), but detects both at the raised 0.3225 m tread.
- With the first player arrival staged, the real PLAYER capsule walks off
  and back onto the third plate. The engine interaction transition samples
  read 2 → 3 → 2 → 3; the flags open, clear and reopen correctly.
- Stock one-player QuestFlagGates says closed → open → **still open** →
  open on the collider. A doorway ray passes when it should hit, and the
  player can physically walk through after release.
- The proposed reversible owner in this bench re-enables collision when
  the conditions clear, but defers re-arm while a player or ITEM occupies
  the doorway. A normal approach after re-arm stays blocked. It does not
  alter the stock class or change any other quest gate.

This is a reproducible rehearsal, not a shipped gate implementation. No
carry interaction, release animation, full-yard collision or save/client/
multiplayer behavior is claimed. A player at the third pad cannot also
walk through a strictly hold-only gate without a third weight or a second
player; the test does not silently add a grace period.

```sh
# An admitted native fixture and pinned dependencies are required.
export WSC_NODE_PROJECT=/path/to/pinned/dependencies
O=/tmp/w4a-grate
mkdir -p "$O"
node --experimental-transform-types demos/native-plate-grate/sample.mjs \
  /path/to/admitted/native-folder "$O/w4a-native-grate.json"
cmp "$O/w4a-native-grate.json" project/layouts/w4a-native-grate-proof.json
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-physics/build.py -- --output "$O/yard"
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/physics_grate.py -- \
  "$O/review" "$O/yard" --trace "$O/w4a-native-grate.json"
```

Photos compare the gate occupancy sampled at tick 159 from one locked
camera using the original assets. Amber marks the actual measured player
position projected into Blender. Showing the art grate where collision
exists is a diagram of the trace, not a screen capture of the running game.

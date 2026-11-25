# W6b: three conveyor speeds against the stock player motor

The prior direction study pinned the three tread art transforms.
This bench keeps the same supported signs: west, east, west
(world X = −3, +4, −5 m/s). The three exact X centers are −84, −90 and
−96 m, Z = −103 m. A flat contact slab per belt uses the reimported
tread extent (4.118 × 1.278 m) and top (0.5195 m after placement);
the beveled visual frame, rollers, and deck detail are not colliders
in this test.

Format 0.43.0 rejects the proposed `conveyor` traverse kind. This is
a test-only contact adapter on Engine 0.1.44, not a stock world row
or a production patch. The deck stays still: a grounded walking
capsule receives a native CharacterMotor movement step along the belt,
blocked by real colliders. In separate runs, a native rigid crate
responds to a bounded contact impulse, not a position assignment.
The crate test locks its rotation and uses zero-friction treads/boxes
to isolate the adapter's drive from native friction; no knock-over
or pushing between the capsule and crate is asserted.

All three trials repeat exactly from a fresh world. A standing
player and a crate in established contact stay within 0.002 m/s
of the three requested speeds. The player's test compares ordinary
walking with and against the belt to the same starting walk without
the adapter; the added speed agrees within 0.06 m/s. Jumping, leaving
the belt, standing alongside it, and using the hoverboard receive
no player drive. The extra movement cannot tunnel through a block
in front of the player. The outer deck remains static.

The two Blender images reimport the exact donor and existing arrows.
They use a capsule and a strapped box as review-only proxies to plot
the independent test tracks; they are not gameplay footage or new
asset exports. No player/crate interaction on the same belt, arbitrary
cargo, network prediction, native client, course timing, animated
treads, mid-run save, or live shard installation is proven.

```sh
T=/tmp/w6b-conveyor
mkdir -p "$T"
D=demos/native-conveyor-bench
node --experimental-transform-types "$D/sample.mjs" "$T/native.json"
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python "$D/render.py" -- "$T/native.json" "$T"
```

Use installed Engine 0.1.44 and Format 0.43.0 with Three, Valibot, and
Rapier, as in the other native benches. If installed outside this
checkout, set `WSC_NODE_PROJECT` to that dependency root and make Three
and Valibot available in this checkout's Node resolution. See
`project/layouts/w6b-native-conveyor-proof.json` for exact measurements.

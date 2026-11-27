# E10c Room 2 → Room 3 threshold

Ten stock-motor passages over the existing geometry (five offsets across
±0.45 m, both directions) in 124–125 ticks, without a jump, stall or
airborne tick. The route is 8.7 m target-to-target. Five sealed runs swap
the existing closed round donor into the doorway; all stop grounded.
Five open runs with the 2.432 m threshold omitted fall before the tread.
No exported GLB changes: the 5,820-byte threshold is bit-for-bit original.

```sh
T=/tmp/vault-room2
B=scripts/blender/showcase-studies/vault_room_two.py
WSC_ROOM2_BENCH=1 blender -b -t 6 --factory-startup --python-exit-code 1 --python "$B" -- "$T"
WSC_NODE_PROJECT=/path/to/pinned/node/project node --experimental-transform-types demos/native-vault-room2/sample.mjs "$T"
blender -b -t 6 --factory-startup --python-exit-code 1 --python "$B" -- "$T"
```

Use Engine 0.1.44 and its Rapier dependency. The fixture extracts only
the center floor strip, transition, bulkhead alternatives and first
Room 3 tread from the pinned Blender recipe. The transforms use the
authored coordinates and donor geometry; the heavy exact trimeshes
are test inputs, not a recommended mobile collision budget. The marks
in the two eye-height renders are recorded capsule positions, not
installed wayfinding. No gate animation, seal trigger, waves, Room 1
join, lateral room clearance, phone validation or live installation.
See [receipt](../../project/layouts/e10c-vault-room2-crossing-proof.json).

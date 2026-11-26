# W4b: crate-to-crate see-saw launch

This fixture reuses the independently authored WSC-PLAN-003 GLB and
haul crate. The authored yard has two static instances at Three X/Z
(-80,224) and (-62,224). In the bench, each instance is tested separately
on the yard's 0.02 m floor datum. The GLB's stand and 1.47 m deck pivot
stay aligned, with no changes to either GLB or the authored yard.

The existing engine Physics wrapper runs Rapier at 60 Hz. A revolute
joint about Three +Z joins the fixed anchor to the deck. Its stops are
±9.55°, within the existing ±10° art fit study. The deck and crates use
convex hulls cooked from the hash-pinned GLB POSITION values. The fixed
stand is visible in the render but not a body collider. The launch uses
a preloaded low side and a larger, heavy crate released above the high
side. The simulation applies gravity and contacts, not an impulse to
the launched crate. Explicit body masses are fixture settings, not
requirements for any live shard.

There are six matched trials (two placements, three lateral offsets)
and twelve negative controls. For each good run, the entire lighter
crate clears the plane of the highest local deck vertex by at least
2.09 m at peak while still above the footprint center lane. It spends
80–81 consecutive ticks more than 4 cm clear and eventually contacts
the deck again. Locking the hinge or omitting the heavier crate
produces no launch. Across the suite, the deck stays more than 0.25 m
above the floor and within 2 mm of its anchor. The centered run is
repeated and compared exactly.

The bench calls Rapier directly through the existing engine Physics
world. It does not implement a dynamic hinge row in the shard format;
the scripted kinematic mover called "hinge" is not this joint. There
is no installed behavior, player launch, drop interaction, reset,
persistence or phone playtest. Next: confirm a supported dynamic-joint
path and test a stock capsule on the deck before offering player launch.

From the art root, using Engine 0.1.44 / Format 0.43.0:

```sh
d=/tmp/w4b-saw
mkdir -p "$d"
node --experimental-transform-types demos/native-seesaw/sample.mjs "$d/proof.json" "$d/trace.json"
cmp "$d/proof.json" project/layouts/w4b-seesaw-launch-proof.json
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-physics/build.py -- --output "$d/yard"
blender -b -t 6 "$d/yard/physics-yard-editable.blend" --python-exit-code 1 \
  --python demos/native-seesaw/render.py -- "$d/trace.json" "$d"
```

Set `WSC_NODE_PROJECT` to an absolute dependency checkout if not using
the art checkout's own dependencies. Both photos show recorded poses;
the wide photo pairs the independently recorded centered apex samples.

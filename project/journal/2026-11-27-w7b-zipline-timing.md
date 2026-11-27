# W7b · A 4.70 s calibration on the existing wire

W7b describes a nominal 4.7 s ride at 22 m/s. The current comparison
keeps the original W08 anchors, sag, 1.05 m launch setback, 1.86 m
release setback, deck target, 2.5 m/s walking release speed and drag.
Only stock Engine 0.1.44 row numbers change.

| Driver row | Gravity coefficient | Cap | Cable time | Peak speed | Peak acceleration |
|---|---:|---:|---:|---:|---:|
| Existing calibration | 9.8 | 22 m/s | 9.367 s | 13.80 m/s | 2.97 m/s² |
| Short | 48 | 26 m/s | 4.700 s | 26 m/s | 14.84 m/s² |
| 22 m/s ceiling | 64 | 22 m/s | 5.033 s | 22 m/s | 19.81 m/s² |

The faster row is a timing candidate, not a new default. It hits the
time target by exceeding the planned speed, with a stronger launch.
The capped comparison keeps the speed but launches even harder and
takes a third of a second longer. Test the Short row on a phone before
choosing it. Do not silently promote either row or change a shared
engine default.

All three complete and restore exactly from a midpoint snapshot. Nine
vertical rays per carried or arriving frame clear the original W08
meshes. The Short row has 93 mm minimum clearance among those samples;
its coarser step positions do **not** prove greater geometric clearance
than the baseline. In a separate release-only Rapier bench all 15 Short
starts land on the original pad, with no step longer than 153 mm. A
closed test shutter stops the same release 0.98 m short. This does not
establish continuous native carry, a product clock, touch input, or
clearance of a full capsule along the wire.

## Reproduce

From the art checkout, use Blender 4.3.2 and the pinned Engine 0.1.44
Node dependencies (set `WSC_NODE_PROJECT` if they live elsewhere).

```sh
t=/tmp/w7b-timing
mkdir -p "$t"
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-zip/build.py -- --output "$t/donor"
blender -b "$t/donor/west-zip-route-editable.blend" -t 6 --python-exit-code 1 \
  --python demos/native-zipline-handoff/extract.py -- "$t/terminal-mesh.json"
for v in baseline short capped; do
  mkdir -p "$t/$v"
  cp "$t/terminal-mesh.json" "$t/$v/"
  node --experimental-transform-types demos/native-zipline/sample-ride.mjs "$t/$v/ride.json" "$v"
  node --experimental-transform-types demos/native-zipline-handoff/sample.mjs "$t/$v" "$v"
  blender -b -t 6 --factory-startup --python-exit-code 1 --python demos/native-zipline/render-ride.py -- \
    --donor "$t/donor/west-zip-route-WIP.glb" --ride "$t/$v/ride.json" --output "$t/$v" --proof-only
done
node demos/native-zipline/compare-timing.mjs "$t"
cmp "$t/comparison.json" project/layouts/w7b-zipline-timing-comparison.json
```

Remove `--proof-only` from the Short run to render the two trolley views.
Keep all reconstructed scenes and detailed traces out of Git. No new
game asset, actor or release trigger is introduced in this pass.

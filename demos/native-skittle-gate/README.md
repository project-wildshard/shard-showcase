# W4b: hold and release four rolling balls

Follow-up to [the earlier skittles run](../native-skittles/README.md), which
released all balls by enabling their bodies on a simple slope. Here the
four balls are enabled the whole time. The original W4b ramp core and
its rails are extracted from editable Blender geometry. A kinematic
bar holds the settled balls for four seconds; its only release input is
a 1.78 m lift over 36 ticks. Nothing is despawned or teleported. The
floor at 0.04 m and ten native pin bodies stay as in the earlier fixture.

Three lateral offsets (center and ±0.12 m) have matched held and lifted
runs. The metric is crossing both the bar plane and 24 m ramp toe, plus
tilt over 60° on the pins. The clean center replay repeats exactly.
There is no lever interaction, game scripting, score, reset persistence,
or installed runtime. The rendered yoke has no collider in this fixture;
the physical bar is a box checked against the actual GLB bounds.

Both GLBs use the same bar-centered fixture origin at Three
`(-26.14, 4.72, 196)`. Keep the yoke fixed and translate the bar only by
`+1.78 m` on Three Y. The older release stand and score board are untouched.

```sh
d=/absolute/scratch/w4b-gate
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-physics/build.py -- --output "$d/yard"
blender -b -t 4 "$d/yard/physics-yard-editable.blend" --python-exit-code 1 --python demos/native-skittle-gate/extract.py -- "$d/ramp.json"
node --experimental-transform-types demos/native-skittle-gate/sample.mjs "$d/ramp.json" "$d/proof.json" "$d/trace.json"
blender -b -t 4 --factory-startup --python-exit-code 1 --python demos/native-skittle-gate/model.py -- "$d/proof.json" "$d"
python demos/native-skittle-gate/check-models.py "$d"
cmp "$d/proof.json" project/layouts/w4b-ball-gate-proof.json
cmp "$d/models.json" project/layouts/w4b-ball-gate-models.json
blender -b -t 6 "$d/yard/physics-yard-editable.blend" --python-exit-code 1 --python demos/native-skittle-gate/render.py -- "$d/trace.json" "$d"
```

Set `WSC_NODE_PROJECT` if Engine 0.1.44 / Format 0.43.0 dependencies
aren't installed in the art checkout. Images use the exact Blender
ramp and the reimported rolling-ball and gate GLBs at recorded poses.

## Walk up and use the existing release stand

The optional player run reuses that ramp and the five hash-pinned GLBs. The
stand is on the flat shoulder at Three `(-30, .04, 200.55)` (identity yaw);
the prompt is near its grip at `(-30, 1.64, 200.70)`, reach 2.5 m.
Those are bench coordinates, not installation instructions for a new map.

The stock player walks about 5.93 m on the same physics world, remaining
grounded for all 86 movement ticks. Engine 0.1.44's headless prompt picker and
admitted latched lever run the author's row. The bench observes the resulting
flag to drive the existing 36-tick gate lift. Moving into reach without a
press, pressing from far away, and pressing at valid distance through an
opaque blocker do not release the balls. A clear press releases all four and
leaves nine pins above the 60° tilt threshold for the final second. A second
press is ignored. An independent fresh session repeats all results exactly.
This is not a map install, network/UI playtest, saved best, nor player reset.
In the renders the grip pose is staged; balls, gate and pins are replay data.

After generating `"$d/ramp.json"` with the commands above:

```sh
node --experimental-transform-types demos/native-skittle-gate/sample.mjs \
  "$d/ramp.json" "$d/lever-proof.json" "$d/lever-trace.json" --lever
cmp "$d/lever-proof.json" project/layouts/w4b-player-lever-proof.json
blender -b -t 6 "$d/yard/physics-yard-editable.blend" --python-exit-code 1 \
  --python demos/native-skittle-gate/render.py -- "$d/lever-trace.json" "$d"
```

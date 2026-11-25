# W10b: taking the first westbound rail

The unchanged R02 striped rail stands at Three (-125, .025, -148), after ring 2.
Its beam is too high for the scale-1 horse's low obstacle ray (0.7 m above
feet) and for the mount's short vertical collision envelope. In the stock
headless ride the horse can go under the rail without jumping, despite the
visual expectation. This optional oak apron makes the low obstruction visible
and triggers the existing auto-jump at a gallop. It leaves the striped beam,
standards and course geometry intact. No new horse model or motor code.

The exported apron is a separate piece with the same local pivot as the rail.
The simulated filled box uses its reimported world bounds; decorative grooves
and pin heads are not independent colliders. The original 32 reimported
donor meshes remain triangle colliders, with the existing review track datum
(.025 m) as the bench's flat floor. The fitted test uses the stock declared
riding installer, real AnimalSim and CharacterMotor, and raw analog reins on
a synthetic, scale-1 calibration horse (top gait 13 m/s).

- Fifteen gallops across three run-up starts and five side offsets to ±1.1 m
  jumped without a jump-button press and landed. All 15 raw-rail controls
  went under without lifting.
- The lowest interpolated feet sample over the entire 2.4 m collision body's
  rail span still cleared the highest beam cap by about 73 mm (not a rig and
  rider mesh clearance claim).
- Three slow approaches stopped at the apron rather than going under.
- The separate manual-jump sample on the original rail had 29/45 attempts
  where the conservative full-body envelope stayed above the rail. This is
  not a device timing recommendation.

This is one straight-line rail, not a full riding lap, penalty, PB, touch
test, or change to the live shard. Ring triggers, other jumps and visual
occupation of the saddle remain out of scope.

```sh
d=/absolute/scratch/w10b-native-rail
mkdir -p "$d"
for step in extract apron; do
  if [ "$step" = extract ]; then arg="$d/geometry.json"; else arg="$d"; fi
  blender -b -t 4 --factory-startup --python-exit-code 1 --python "demos/native-riding-rail/$step.py" -- "$arg"
done
node --experimental-transform-types demos/native-riding-rail/sample.mjs "$d/geometry.json" "$d/apron.json" "$d/proof.json" "$d/replays.json"
cmp "$d/proof.json" project/layouts/w10b-native-rail-apron-proof.json
WSC_RIDING_RAIL_REVIEW="$d" blender -b -t 6 --factory-startup --python-exit-code 1 --python scripts/blender/showcase-studies/riding_course.py -- "$d"
```

Set WSC_NODE_PROJECT to the installed Engine 0.1.44 and Rapier package root
if needed. Amber and mint overlays in the Blender photos use original and
fitted stock input samples, respectively; they are not live effects.

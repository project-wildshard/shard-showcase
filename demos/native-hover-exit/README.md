# W5a: steer or stop after the tallest kicker

The earlier receiver pass checked jumps along a straight line, ending before the east launch wall. This follow-up tests what happens without a jump when the rider releases the stick, briefly presses opposite their travel, or turns. It uses the exact reimported receiver top and all three original ramp and run-up surfaces plus the zone paving. Both meshes remain unchanged, and the stock board sees only ordinary input frames at 60 Hz. The east launch wall is represented by its measured leading X plane; the runs stop there if they reach it. This does **not** simulate hitting that wall or install a blocker.

## Results

Each maneuver repeats at centerline and ±0.75 m. All 27 runs retain full HP. The arrival speed before each intervention is 14 m/s.

| Input | Result |
|---|---|
| Neutral at X −171 | Coasts 32.55 m; stops 3.18–3.34 m short of the wall's X plane. |
| Neutral at X −195 | Reaches the plane at about 12 m/s in all three runs. |
| Brief opposing input at X −193, then neutral | Stops in 11.80–11.89 m, with at least 1.90 m of center clearance. |
| 31° turn at X −198 | Leaves the low deck but still reaches the plane at 13.65–14.00 m/s. |
| 78° turn at X −196, release beyond the deck | All six stop short with at least 1.15 m of center clearance; crosses the edge with feet at 0.24–0.40 m above world zero. |
| 35° turn at X −176 | Leaves the elevated shelf at about 5.25 m feet height, then settles to the paving. The stock repulsor mode doesn't mark this as explicit jump flight. |

The stop plane is conservative beyond the wall's actual Z span. Passing a plane does not demonstrate a collision. The bounded result favors a visible early release signal over assuming a phone swipe or late stick release will work. Do not put a turn arrow on the flat elevated shelf. Validate contact against the real launch-wall collider and repeat both exits with touch input before installing a course cue.

This is a standalone server fixture, not a phone touch-input test, a park-wide collision pass, or a playability claim. Release is neutral input; the stock board coasts, with no dedicated brake shown here. A sustained reverse command would reverse the board; the test releases it as the velocity approaches zero. Steering runs follow a six-frame turn. ## Reproduce

```sh
d=/absolute/scratch/hover-exit
mkdir -p "$d"
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-hover/build.py -- --output "$d/park"
blender -b -t 6 "$d/park/hover-park-editable.blend" --python-exit-code 1 --python demos/native-hover-kickers/extract.py -- "$d/base.json"
blender -b -t 6 "$d/park/hover-park-editable.blend" --python-exit-code 1 --python demos/native-hover-receiver/build.py -- "$d"
cmp "$d/w5a-high-kicker-receiver.glb" public/assets/wildshard-art/w5a-high-kicker-receiver.glb
node --experimental-transform-types demos/native-hover-exit/sample.mjs "$d/base.json" "$d/receiver.json" "$d/replay.json" "$d/proof.json"
cmp "$d/proof.json" project/layouts/w5a-high-kicker-exit-proof.json
blender -b -t 6 "$d/receiver-review.blend" --python-exit-code 1 --python demos/native-hover-exit/render.py -- "$d/replay.json" "$d"
```

Set `WSC_NODE_PROJECT` to a package root with Engine 0.1.44 and Rapier if needed. Mint and amber lines offset 19 cm and 20 cm in opposite directions in the first picture so their identical lane centre does not hide one trace; the oblique steering traces have no lateral offset. Dots are Blender overlays of recorded positions, not engine screenshots or placed gameplay objects.

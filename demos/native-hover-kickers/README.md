# W5a: stock hoverboard on the three D7 kickers

Bounded server fixture, not a live or multiplayer install. Unchanged D7 park
build places ramps of 2.4, 3.6 and 4.8 m at Three Z 132, 143 and 154, with
shared toe X −157 and 45 m runs. The exact assembled ramp, strip and paving
triangles are loaded as WORLD trimeshes. Art props elsewhere in the park
are not installed as colliders in this test. No jump assist, injected impulses
or teleport is used. Ordinary movement reaches 14 m/s before the toe.

Starting at X −114, all three ramps are rideable straight through in this
fixture. Without JUMP, stock repulsors carry the board over the lip and
down without entering the board's explicit ballistic state or losing HP.
The maximum feet heights are 2.58, 3.78 and 4.98 m. Those are not jump apexes.

At 60 Hz the harness tries one independent JUMP input at each of 134
centerline ticks between toe and passive peak. Every lane has a refusal
window as the board enters the slope, a second acceptance window near
the lip, and another refusal at the lip. The highest actual jumps reach
5.37, 6.61 and 7.75 m and cost one stock 8 HP hard-landing hit apiece,
before ordinary recovery. Tested with identical commands on flat control
paving, the jumped apex is approximately 3.38 m. Moving the start 0.5 m
to either side makes the lowest lane's best centerline timing miss, while
the other two accept it and still land hard. No sampled higher clean
jump exceeded nominal ramp height by 0.40 m without taking damage.
Do not add a universal takeoff stripe based on these timing results.
Next check an explicit receiving slope and player-controlled cue in the
whole-park fixture before proposing live trick or scoring integration.

## Reproduce

From repository root with Blender 4.3.2 and Node 24.22.3. Set
`WSC_NODE_PROJECT` to the package root housing Engine 0.1.44 and its
Rapier/Three dependencies if they are not in this checkout.

```sh
d=/absolute/scratch/w5a
mkdir -p "$d"
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-hover/build.py -- --output "$d/hover"
blender -b -t 6 "$d/hover/hover-park-editable.blend" --python-exit-code 1 --python demos/native-hover-kickers/extract.py -- "$d/geometry.json"
node --experimental-transform-types demos/native-hover-kickers/sample.mjs "$d/geometry.json" "$d/replay.json" "$d/proof.json"
cmp "$d/proof.json" project/layouts/w5a-native-kicker-proof.json
blender -b -t 6 "$d/hover/hover-park-editable.blend" --python-exit-code 1 --python demos/native-hover-kickers/render.py -- "$d/replay.json" "$d/photos"
```

Mint dots show passive samples; amber dots show the chosen jump during its
explicit flight. The dots, lights and camera are Blender review overlays,
not native gameplay footage or new assets. No motion or art is changed by
this study. No client prediction, touch feel, scoring, board rendering,
full counter-route collision, or showcase deployment is proven.

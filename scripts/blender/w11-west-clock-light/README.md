# W11a West lamps: clock and shared point lights

Build reusable candidate rows from the checked Stable and West gate
mounts, four existing obelisk uplights, and the Movers record-board
lamp. No models are duplicated. The movers eye chooses the record-board
anchor; the plaza eye chooses the nearest pair of obelisk anchors.
The Range board lamp has only a local model fit and is not placed here.
The blocked Stable pier stays unlit.

The distinct wave arrays are stable pool identities in Engine 0.1.44.
Each bank takes one PointLight and chooses the nearest active anchor
using the actual `SiteLights` class. Eight anchors therefore use four
resident lights in the test. A proposed day-hour gate switches all at
18:00 and clears them at 06:00, using the stock phase clock. The node
fixture tests the format parser, clock law, stable allocation and anchor
selection; it does not boot the full installed client plan. No renderer
timings, production intensities, weather changes or gameplay are implied.
The images use the sampled locations and states in Blender with review
exposure and converted intensities, not native photometric values.

```sh
D=/tmp/w11-west
mkdir -p "$D"
node scripts/blender/w11-west-clock-light/make.mjs "$D/rows.json"
WSC_NODE_PROJECT=/path/to/pinned-engine-deps node --experimental-transform-types \
  scripts/blender/w11-west-clock-light/check.mjs "$D/rows.json" "$D/check.json"
cmp "$D/rows.json" project/layouts/w11a-west-clock-lights.json
cmp "$D/check.json" project/layouts/w11a-west-clock-lights-proof.json
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/w11-west-clock-light/render.py -- "$D/rows.json" "$D/check.json" "$D"
```

An integration would publish the named points and dedicated empty lens
groups in `world/scenes`, install the rows under `light.emitters` and
declare the host seconds field separately. The emitter seconds field is
for flicker, not the day/night switch; wire the latter from the day-cycle
phase clock (or equivalent admitted data policy). Never parent the visible
lamp housing under the emitter group merely to hide an off lens.

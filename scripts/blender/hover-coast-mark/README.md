# W5a: ease-off paint on the tallest kicker's receiver

The exact launch-wall bench showed that neutral input at X −171 stopped the
stock board at least 3.176 m short of the wall, but letting go much later
did not. This optional marking is fully visible before the tested release
line. It tells players to ease off rather than directing a turn on the shelf.
The two materials and built-in Blender glyphs make it texture-free.

Import at the existing receiver origin (Three −167.39, 0, 154). It lies 2 mm
above the exact riding surface and stays inside the shoulder stripe. Marking
only: never add a collider. The measured release is from the earlier fixed
server input, not a reaction-time, touch control, or game test. The two
renders show an isolated receiver and preview paving, not the live course.

From repository root with Blender 4.3.2:

```sh
O=/tmp/hover-ease-off
WSC_COAST_RENDER=1 blender -b -t 6 --factory-startup --python-exit-code 1 --python scripts/blender/hover-coast-mark/build.py -- "$O"
cmp "$O/w5a-high-receiver-ease-off.glb" public/assets/wildshard-art/w5a-high-receiver-ease-off.glb
cmp "$O/w5a-high-receiver-ease-off-proof.json" project/layouts/w5a-high-receiver-ease-off-proof.json
```

Omit `WSC_COAST_RENDER` to check fit and framing without rendering.

# E3: Band 3 suspended canvas pillar screen

The original E03 portrait in Round 11 (`east/e03.jpg` Git blob
`6a069115c5247cf353196c6b03a722d0f6bfb2da`) shows
capped dark posts, warm cross members, and amber over slate fabric.
That image is the material reference. Round 5 `lab.js` holds the
dimensions: paired 1.6 m post envelopes 8 m apart, 7 m tall;
a 9.6 × 1.6 m maximum footprint; a 7.6 m cloth span from 2.2 to 6.2 m.
The binding rings, sewn hem, and subtle fabric waves are new inferred detail.

`placement.js` has 27 Band 3 pillar rows. Testing a conservative full
footprint rectangle against the archived pack points, 19 rows meet the
archived 8 m keep-clear radius. The screen closest to the entry does not:
8.878 m center to center is only 4.170 m using its footprint.
The next closest row is the tested one (Three.js x = 127.0018881,
z = −193.2672736, yaw = 1.6358348); its footprint stays at least
33.705 m from the nearest pack. The archive is unchanged and the
candidate module is not installed at any position.

The GLB is one mesh with eight material primitives. The procedural
authoring source still separates the pin hardware, posts, beam and
two-sided cloth. It uses no textures or animators. The reimported
model was checked both ways at 33 samples across the central 6.4 m.
All 66 rays at each of 0.85, 1.70 and 2.10 m clear the screen;
all 66 at each of 3, 4, and 5 m hit cloth; 7.20 m clears above it.
The post control rays hit at every tested height and direction.
These are geometric ray checks, not collision or gameplay visibility.

Rebuild from the repository root with Blender 4.3.2 and Three:
```sh
T=/tmp/wildshard-e3-screen
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/drone_pillar_screen.py -- "$T" --render
node project/check-drone-pillar-screen.mjs "$T/e3-suspended-pillar-screen.glb"
```

Drop the `--render` flag for a rebuild without review images. The size
guides, studio paving, and real shadows are presentation only. There is
no new drone actor, docking behavior, collider, active sightline, or
runtime integration. See `project/layouts/e3-pillar-screen-proof.json`
for source identities and exact proof.

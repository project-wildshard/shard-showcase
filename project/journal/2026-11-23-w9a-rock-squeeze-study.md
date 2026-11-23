# W9a: the Rock squeeze cave, static art study

The two exact exterior arch centers are `(-200, 0, 14)` and
`(-200, 0, 74)` in glTF world coordinates. WSC-PROP-011 is a
decorative blind recess, which remains intact. Separate hollow
trim rides over both ends of the new continuous liner. The section
clips a temporary copy of the rebuilt crag at X −203.6; the cut
exposes the liner and does not show an integrated terrain carve.

The section stages a 60 m route with two nominal 22 m ramps (15.255°),
a 16 m bottom at Y −6, and the proposed 1.1 m high / 4 m long squeeze.
The shaft opens from the 4.8 m high north antechamber to Y 16 at
world X −200/Z 39. Nine ray samples hit the original crown at Y 16.
Its proposed rim is 8.784 m clear of the exact bench along X. Floor
rays clear at each interior station, ceiling samples show the
squeeze height, and an upward centerline ray clears the shaft.
These are mesh checks only, not player traversal tests. Q29/Q30
in OPEN-QUESTIONS record recommendations, not final answers.

From repository root, with Blender 4.3.2 and the repository Node setup:

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-climb-rock/build.py -- --output /tmp/rock-source
blender -b /tmp/rock-source/climb-rock-editable.blend -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/rock_squeeze_cave.py -- /tmp/rock-cave
```

Keep the compact recipe and generated measurements, not the 41 MB
intermediate .blend. No new GLB or catalogue ID, collision,
W0a terrain integration, W9a host work, Pine migration, interactive
cache, crouch sweep, lightmap or gameplay capture.

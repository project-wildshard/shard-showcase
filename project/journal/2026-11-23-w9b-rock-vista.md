# W9b: Rock lookout vista framing

The 16 m summit and the existing WSC-PROP-044 bench come from the
source-only West Climb Yard / Rock rebuild. The bench remains at
Blender (-210, -40, 16), glTF world (-210, 16, 40), with a .605 m
high seat. The vista test sets a candidate seated eye 1.48 m above
the crown, aimed at the existing West Town roofline, and a separate
approach camera behind the bench.

A moss variation for the in-memory crown, stepping stones, three
existing decorative donors (rail, conifer, wildflower), and off-map
silhouette cards frame the view. They are studio additions only:
nothing is saved into the source scene, and no new mesh delivery or
level placement is implied. The source paths, hashes, placements
and camera parameters live in `project/layouts/w9b-rock-vista-camera.json`.

From repository root, with Blender 4.3.2 and the repository Node setup:

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-climb-rock/build.py -- --output /tmp/rock-source
blender -b /tmp/rock-source/climb-rock-editable.blend -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/rock_vista_camera.py -- /tmp/rock-vista
```

No bench prompt, player snap or idle, discovery flag, FINDS counter,
camera movement, phone field of view calibration, or shipped terrain.
The seated view is a measured art camera, not a capture from gameplay.

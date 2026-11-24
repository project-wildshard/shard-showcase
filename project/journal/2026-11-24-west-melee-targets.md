# W3a / W3d: West melee practice fixtures

Round 5 gives separate sword and spear rows at world X −30, −24,
−18; sword Z 86, spear Z 104. The receipt preserves those anchors.
These assets are independently reusable and retain the existing
W3b ammunition-lane soft dummy unchanged.

The parry fixture is 1.90 m tall and has a separate named padded
arm node, 1.80 m across at 1.30 m high. The 0° and 28° art poses
retain one pivot. The proposed pivot clears the canvas body in
the turned pose. No swing, collision, parry window or scoring.

The spear ring retains the 2.00 m center, 0.20 m forward offset,
0.96 m nominal opening, and 1.44 m nominal outside diameter. The
old 2.40 m central post in the blockout would occlude that opening.
A fork replaces the obstructing part so 29 sampled rays clear the
inner bore. This is a mesh check, not a player or collider test.

Both exact GLBs reimport in Blender and Three.js. See the
[fit and geometry receipt](../layouts/w3a-w3d-melee-targets.json).

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/west_melee_targets.py \
  -- /tmp/west-melee-targets
```

Set `WILDSHARD_VALIDATE_ONLY=1` for the meshes and checks only.

# W4a Physics Yard plate-gate art study

The reconstructed yard had three cyan blocks and a bare frame. D19
calls for a grate that opens only while all three plates are held.
This adds a six-bay metal insert, leaving the reviewed yard, tracked
pressure plate and haul crate unchanged. The two review stills stage
the two crates in the same positions. The third plate is unheld in
the closed shot and marked held by an illustrative footprint in the
open shot. Nothing latches; nothing here runs at all. The render
replaces only the plate stand-ins in a temporary scene.

The exact reimport spans 19.256 m over six bays, in the existing
19.450 m opening at map x/z (−52,192). It clears the sampled floor
stripe by 25.5 mm and the header by 85 mm. Jamb clearance is 97 mm
at either edge. Ray samples hit both steel and true apertures in
each bay. Pressed treads support the two reimported crates at z
0.3225 m. These are geometric checks, not collision, animation,
joining, structural or gameplay claims.

The standalone insert is 151,960 B and 2,664 triangles. It has a
center-bottom local origin, Blender Y across the opening and Z up,
with the colored tabs toward local −X. Placement in the reviewed
yard uses Blender translation (−52,−192,0.060) with zero rotation.
Keep the six panel meshes together for this presentation; their
construction does not imply a drive, pocket or moving path.

From the repo root with Blender 4.3.2 and repo Node deps installed:

```sh
out=/absolute/scratch/physics-grate
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-physics/build.py -- --output "$out/yard"
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/physics_grate.py -- \
  "$out/study" "$out/yard"
```

The builder checks the inherited yard semantic signature and the
exact plate/crate donor SHA-256s before staging. It emits a JSON
receipt, the standalone insert and three photos. Neither the
full yard GLB, temporary .blend files nor duplicate donors belong
in the art commit.

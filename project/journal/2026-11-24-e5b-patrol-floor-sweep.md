# E5b patrol lamp floor cue

The E5b slice needs the player to read a patrol's lamp even
where the floor already has shadow pools. This study isolates
a short amber floor cue from any actor, actual lamp or vision
logic. It keeps the original shadow decals and five exact donor
models, and holds the staged camera and light between frames.
The narrower side edges and feathered far arc keep the shape
distinct from the industrial floor lines without filling the yard.

The standalone GLB is 9,008 B and 312 triangles. Local +Y in
Blender (−Z in glTF) is forward; the flat mesh is 17 mm above
the floor datum, 5.8 m long with a 30° total visual opening.
This dimension is an art choice, not the gameplay cone angle.
In the staged yard the Blender transform is (1.42, 4.67, 0)
with −174° yaw. The script ray-checks every reimported vertex
over the existing floor. glTF uses normal alpha Blend and
`KHR_materials_unlit`; it is not additive and emits no light.
Three's loader confirms one unlit transparent mesh with RGBA
and no depth writes. This is an import check, not mobile proof.

From the repo root:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/e5b_patrol_sweep.py -- /tmp/e5b-sweep
node scripts/blender/showcase-studies/check_e5b_sweep.mjs \
  /tmp/e5b-sweep/wsc-kit-006-patrol-floor-sweep.glb
```

No patrol model, animation, occlusion, alarm or detection
logic. For a real scene, add terrain-conforming projection
and drive yaw/visibility from the patrol's sight host.

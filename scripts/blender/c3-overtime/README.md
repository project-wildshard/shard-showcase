# E11d Foreman Overtime floor tape

One 7.60 × 2.80 m patch, no textures, one material primitive, 100
triangles and 8,712 bytes. Amber slants around the charcoal rails and
inward chevrons distinguish the boundary by shape as well as color.
The center is unfilled, preserving the original floor. This is an
optional phase-only render layer, not a permanent paint stripe.

The [placement receipt](../../../project/layouts/e11d-c3-overtime-tape.json)
gives two independent Three origins and Y-axis rotations. Add the
unchanged GLB at each transform. Its top is 4–6 mm above the original
0.05 m deck. 377 samples per marked rectangle hit the same height, and
both reimported instances have no triangle crossings with the actual
C3 art. The proposed bounds clear five previously tested G2 → G3 path
centerlines by at least 2.81 m after deducting capsule radius and sample
spacing. That is a placement check, not a combat or dodge test.

```sh
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/c3-overtime/build.py -- /tmp/c3-overtime
```

Set `WSC_VALIDATE_ONLY=1` to generate the GLB and receipt without renders.
No collision, slow state, server trigger, boss, damage, or phone behavior
is implemented. If adopted, use the listed rectangles as a starting
point for matching visuals and authored zones during the actual phase.

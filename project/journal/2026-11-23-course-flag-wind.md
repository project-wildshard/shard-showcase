# W11a: reusable course flag wind loop | WSC-PROP-028

The existing course flag and five hardware meshes stay unchanged.
This is a cloth-only replacement; do not layer it over the original
cloth. At the donor placement transform, hide the three original cloth,
hem and hoist nodes and mount the new GLB. It uses the original mesh
positions at equal morph weights (0.5, 0.5); the GLB default is the
first animated pose, not the neutral stance. The fixed hoist stays
attached at all weights. No runtime swap performed.

The 2.5 s `Course flag gust` clip uses two complementary morph shapes
with values in [0,1]; the entry and exit poses match. Blender
reimport confirmed the 2,168 cloth triangles, donor point coverage at
the neutral weights, and 0.1777 m movement at a measured outer vertex
between frames 0 and 25. Current export is 204,108 raw bytes, cut from
310,024 B by using two rather than four morph shapes. The static
189,876 B full flag remains separate. No mobile performance claim,
wind coupling, physics cloth, new placement or native deployment.

Rebuild with Blender 4.3.2 from repo root:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/course_flag_gust.py -- /tmp/course-gust
```

The proof image samples frames 0, 17, and 35 from the reimported clip
on the same unchanged hardware. The GLB and JSON validation rebuilt
byte for byte on a clean pass.

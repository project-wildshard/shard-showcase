# E6: the half-second before an Arc Sentry combo

The E6 plan sets a 0.60 s lance crackle before the three-hit combo.
This reusable visual starts with two tight pilot arcs, expands across
the head and then resolves into a brighter spine with side branches.
It stays at the attachment and stops at 0.60 s. It neither fires an
attack nor draws or blocks a hit. No camera bloom, light, textures,
projectiles, damage, shock, parry or partial Sentry actor.

`makeChargeCue()` gives a Three mesh, `sample(ageSeconds)` and `dispose()`.
Attach the mesh with local +X along the head and +Z toward its open face.
The presentation caller supplies elapsed time and plays the event once.
The call evaluates absolute age, so seeking back or resetting does not
retain prior vertices or extend the charge. It allocates one geometry
and material whose position/color buffers are reused; 62 of 80
segment slots are ever active in the millisecond sweep. Closed radial
profiles are rendered as narrow four-sided tubes, with a lifted pale
edge so it stays visible outside the blue outline. No GPU timing or
phone performance claims.

Preview pictures use the exact sampled Three mesh triangles. The
phone-size still shows the final cue at 10 m in front of a pinned
Round 5 low cover, whose geometry and archived anchor stay unchanged.
The ceramic bracket and plinth are just review mounts, not a new
lance or a spawn. The image pair uses no bloom or emitted scene light
from the cue. A separate hidden-cue render tests contrast.

```sh
OUT=/absolute/scratch/arc-charge
mkdir -p "$OUT"
node demos/arc-charge/check.mjs "$OUT/sample.json"
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python demos/arc-charge/render.py -- "$OUT/sample.json"
python demos/arc-charge/check_render.py "$OUT"
```

The repo's Three dependency must be installed. Pillow is used for the
image check. Review render instructions use Blender 4.3.2. These are
photographs of the staged art study, not a browser or native gameplay
capture. No per-user photos, large scratch frames or derived buffers
need to be committed.

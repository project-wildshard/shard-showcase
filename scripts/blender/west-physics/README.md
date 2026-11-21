# West Physics Yard: source-only static art WIP

From repository root, build with Blender 4.3.2 and the repository Node environment:

```sh
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-physics/build.py -- --output /absolute/scratch/west-physics
```

The recipe rebuilds reviewed Hover Park from tracked inputs and adds the
Physics Yard. It checks the original tracked haul-crate donor hash and reuses
that donor at native scale. No private dependency or binary duplication;
all generated output stays outside checkout. No fresh renders are generated.

W4b/W9b placement follows ce1cf050b3 round-five layout.js and lab.js: the
78 × 54 m yard, adjacent 8 m alley and cache marker, two seesaws, the 24 × 4 m
ball ramp with 6 m rise, and the ball/pin bank. The ramp is scene geometry,
not a new catalog item. Existing WSC-PLAN-003/004/005 inspired three studies
but were not imported donors. Finish and dressing are authored art.
The alley marker and pressure-plate court are static, not interactable.

Native and clean-reimport QA preserve all inherited meshes, the zip and
Hover anchors, exact study placements, measured ramp profile, and sampled
alley/approach sightlines. The semantic comparison permits only the already
scoped W08 untextured arm UV exception (5.96e-8); the GLB remains untouched.
No runtime, physics, collision, player clearance, scoring, performance,
mobile, or gameplay validation.

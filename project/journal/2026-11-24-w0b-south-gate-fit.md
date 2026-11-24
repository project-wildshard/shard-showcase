# Park and Range nameplate fit

Two more placements for the existing six-face W0b sign kit.
The exact rebuilt W0b town passes the recorded normalized
mesh parity check. Both south-facing timber lintels are
12.2 × 1.75 × 0.75 m, 59 m apart in X. Reimporting the
tracked kit at full size leaves 60 mm above and below
each frame. One mount works for both, translating only X.

Four 45 mm-radius pad seats per gate were ray-checked at
their centers and four cardinal points against the evaluated
lintel. The plaque rear sits 30 mm proud of the beam and
7 mm clear of the old letter meshes. The old Range letters
extend beyond the new plaque's outline, unlike Park's.
Hide the two old labels for the comparison, not the source.
The matched south approach views stage both gates with a
1.7 m eye height. The mock-up pads are Blender-only.

From the repo root with Blender 4.3 and Node on PATH:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/west-town/build.py -- --output /tmp/w0b-town
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/town_south_gate_fit.py -- \
  /tmp/w0b-town/whole-town-editable.blend /tmp/w0b-south-fit
```

The receipt in /tmp/w0b-south-fit records evaluated bounds,
margins, pad centers and camera lettering heights. No revised
GLB or large staging scene is needed. This is a geometry
fit check, not a native placement, collision or routing change.

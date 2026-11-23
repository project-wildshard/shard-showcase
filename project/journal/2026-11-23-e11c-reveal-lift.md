# November 23 · E11c C2 reveal lift

WSC-KIT-009 fills the discrete lift gap in the C2 court art. The
current E11c plan calls for a 6 × 6 m platform and 4 m rise under
the banner. The native layout is untouched; the older blockout
center (x 55, z 229) is placement reference, not a transform in
either GLB. The court kit and banner art are not duplicated.

The floor-local fixed frame and moving deck are separate. The
stable moving node is C2_Lift_Moving_Deck. In glTF its top is at
Y=0, centered in X/Z; translate only the deck +4 m on Y for the
raised pose. The checker proves 60 mm per-side deck clearance, plus at least 55 mm for the shaft,
from the fixed frame across the vertical stroke using actual
triangles. This is geometry proof, not playable collision.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/reveal_lift.py -- /tmp/e11c
python scripts/blender/showcase-studies/check_reveal_lift.py /tmp/e11c
```

Set `WSC_LIFT_RENDER=1` for two poses reimported into Blender.
The fixed frame is 121,744 bytes / 2,144 triangles. The moving
deck is 91,596 bytes / 1,584 triangles. No textures or caches are
required. The winch host, stage trigger, banner placement and
Supervisor encounter are not implemented in this art pass.

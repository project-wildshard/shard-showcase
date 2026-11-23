# W10a trough: tiny surface motion, unchanged basin

This is a visual add-on for the paddock's WSC-PROP-079 trough, not a new
trough, an activated spout, or a real fluid simulation. The original GLB
is left untouched. The replacement only uses the original inset's
3.16 × 0.82 m footprint and 0.6775 m surface height. To assemble the preview
at its native origin, hide the original `Inset water surface` node and load
the new GLB without an offset.

The 99,568-byte textureless GLB holds one mesh, 1,344 triangles, and the
three-second `Trough_Ripple_Loop_3s` clip. Four shapes drive small height
changes while all 124 perimeter vertices stay fixed. The checked exported
start and end weights are identical and the reimported intermediate poses
differ. The broader waves and rougher finish soften the original faceted glare.
The blue color is simple opaque PBR; the reflections in the images
need the preview lighting. Playback, lighting parity, and performance are
not verified in the game.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/trough_ripples.py -- /tmp/w10a-water
```

This rebuilds the asset, validation JSON, and two Blender photos of the
reimported animation staged in the exact trough.

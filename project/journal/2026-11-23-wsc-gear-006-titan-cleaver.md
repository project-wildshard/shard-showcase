# Titan Cleaver WSC-GEAR-006: inventory visual

First reusable mesh for the planned E12h reward. The provisional
catalogue turnaround supplies the exaggerated asymmetric housing,
asymmetric oxide trim, graphite grip, and blue-green inset. E12h
supplies the gold finish and reward identity, not a source mesh or
an implementation. The model is decorative and nonfunctional
and uses neither the existing sword nor any private test-yard work.

The grip center is the origin. The GLB uses one mesh, six PBR
material primitives, 1,096 tris, and 58,344 bytes (under 65,536).
Flat cosmetic inlays, rather than extruded hidden sides, kept the
download small. No textures, rigs or animations. No equip pose,
combat effects, unlock, drop, or gameplay integration. Rendering
starts from the reimported model.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/titan_cleaver.py -- /tmp/wsc-cleaver
```

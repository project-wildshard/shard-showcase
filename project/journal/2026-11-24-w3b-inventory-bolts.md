# W3b inventory bolt silhouettes

Three previously concept-only catalogue rows now have compact,
nonfunctional fantasy inventory models. They are based on the
existing public four-view art and the family names in
W3b-bow-crossbow-ammo.md. Their forms deliberately read at icon
size: pewter diamond and silver vanes for Iron, pierced blue
iron and jade vanes for Broadhead, and crossed russet bands
around a luminous amber gem for Pitch.

| Existing ID | Export | Triangles | Bytes |
| --- | --- | ---: | ---: |
| WSC-GEAR-007 | wsc-gear-007-iron-bolt.glb | 764 | 46,920 |
| WSC-GEAR-008 | wsc-gear-008-broadhead-bolt.glb | 804 | 49,904 |
| WSC-GEAR-009 | wsc-gear-009-pitch-bolt.glb | 1,068 | 62,820 |

Three separate GLBs, one mesh each. Each reimport has an identity
object origin at the base and a normalized vertical display pose.
No texture archive or .blend is needed. The Pitch glow lives in
its material, with no flame, lighting object or emitted particles.
They have solid display caps, not launch interfaces, and are not
sized to working equipment.

From repo root with Blender 4.3.2:

```sh
out=/absolute/scratch/w3b-inventory
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/west_inventory_bolts.py -- "$out"
```

The script exports, reimports, checks geometry bounds and the
65,536-byte cap per model, and writes SHA-256 receipts and two
Blender stills. This is an inventory art pass only. No equip pose,
weapon motion, projectile behavior, impact, fire effect or
game/UI integration changed.

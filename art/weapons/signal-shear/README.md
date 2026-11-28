# WSC-WPN-014 · Signal Shear
Original Wildshard salvage-forged gate blade. Broad asymmetric nickel edge, bronze opening gates, segmented green signal channel, and a woven grip. No Fable assets or game code.

- Editable Blender scene: `signal-shear.blend`. Weapon and lit display bench are separate collections.
- Runtime: `signal-shear.glb`, 6,508 triangles. Grip pivot, grip/tip sockets, three rigid mechanism bones, and the independent clips `Signal_Release` and `Arc_Cut`. This is a weapon rig, not a hero rig.
- Rebuild from the repository root: `blender -b -t 8 --factory-startup --python-exit-code 1 --python scripts/blender/signal-shear/build.py -- /tmp/signal-shear`.
- Runtime checks: `python scripts/blender/signal-shear/verify.py art/weapons/signal-shear/signal-shear.glb`.

The neutral render is a presentation scene and the export contains only the weapon. The clips are presentation-ready; damage or equipment integration is not in this asset.

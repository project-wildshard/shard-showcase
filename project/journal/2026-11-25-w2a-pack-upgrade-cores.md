# W2a: the three mini-boss upgrade components

Three original props fill the remaining named upgrade-component slots next
to the [six ordinary salvage parts](2026-11-24-w2a-salvage-parts.md). They
follow the reward table and the approved unfound PACK silhouettes, not
the discarded combined currency/inventory layout.

| Component | Planned source | Planned use | Silhouette cue |
| --- | --- | --- | --- |
| Hydraulic Heart | Big Pallet first kill | Dodge Servo | Split red pressure manifold and exposed pistons |
| Plate Core | Vault Warden chest | Parry Gyro | Cold armored frame with a real center aperture |
| Foreman's Capacitor | Foreman Unit 7 | Arc Insulation | Tall twin ceramic banks and twin brass terminals |

The Plate Core is not Warden's Plate; the Hydraulic Heart is not
Big Pallet's Tines; the Capacitor is not the Foreman's Whistle. None
is Titan's Core. The models are concepts, not detached meshes from the
bosses. No gameplay drops, inventory UI, skill purchases, or boss
rigs were added.

One texture-free GLB contains three separately named components at
study scale. Each has a bottom-center local origin; their file-level
translations only space out the display. Renders normalize display sizes.
The 48 × 48 alpha tests compare the selected orientations instead of
claiming real user recognition. The exact prior six-salvage GLB is
the comparison set; none of those meshes was changed. The Three.js
test also verifies that the Plate Core hole stays open through the
geometry, not just dark in the lighting.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/pack_upgrade_cores.py -- /tmp/w2a-pack-cores
node scripts/blender/showcase-studies/check_pack_upgrade_cores.mjs \
  /tmp/w2a-pack-cores/w2a-pack-upgrade-cores.glb
```

[Plan and rewards](../../docs/plans/kitchen-sink-v2/loot-economy-mini-plan.md#numbers)
· [Approved PACK treatment](../../docs/plans/kitchen-sink-v2/slices/W2a-currency-pack-owned.md)
· [Validation receipt](../layouts/w2a-pack-upgrade-cores-proof.json)

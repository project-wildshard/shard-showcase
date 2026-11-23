# Standalone E08 Training Vault frame

WSC-ARCH-007 is the exterior walk-in portal from E08 and E10a, not the swung physical door (WSC-MODULE-021), the interior bulkhead (WSC-PROP-063), or the Vault Warden. No alias or standalone file was found in the checked project art. The first separate model keeps the orange clay piers, bolted gunmetal flange, brass markers, turquoise lens and keycard emblem. Its sill sits near the floor and the exported triangles leave a clear 1.6 m × 2.885 m rectangle. That is a geometry check, not collider or traversal QA.

The texture-free GLB is 242,196 bytes, below the 256 KiB catalogue budget, and 4,688 triangles. No baked or animated swirl, moving door, keycard state or gameplay logic is part of the model. Four other Vault entrance pieces are unchanged donor exports, not newly modeled. The review render reimports their GLBs with scale adjusted for the composition.

From the art checkout:

```sh
out=/absolute/scratch/vault-frame
blender -b -t 6 --factory-startup --python-exit-code 1 --python scripts/blender/showcase-studies/vault_portal.py -- "$out"
python3 scripts/blender/showcase-studies/check_vault_portal.py "$out/wsc-arch-007-training-vault-portal.glb"
```

Set `WSC_VAULT_RENDER=1` for the tracked-donor reimport scene. The standalone source is self-contained apart from the existing export helpers. Coverage ledger: one East Vault architectural gap filled as static art. KIT-008 rooms, Warden and portal transfer/VFX remain distinct work; rotate families rather than polish this frame again next hour.

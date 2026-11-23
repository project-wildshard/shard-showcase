# West Physics Yard standalone props

First breadth pass. The catalogue already had stable IDs and visual references, and the connected West Physics Yard had static scene-only stand-ins. It did not have individual, placement-ready files for these four. This pass supplies standalone GLBs with consistent enamel, metal and timber. The scene WIP and native game remain unchanged.

| Catalogue ID | Export | Triangles | Raw GLB bytes | Handoff |
|---|---|---:|---:|---|
| WSC-PLAN-003 | Hinged see-saw | 1,296 | 98,836 | Fixed base and a separate level 14 m deck with a 1.47 m axle pivot |
| WSC-PLAN-004 | Rolling ball | 440 | 18,524 | 1.6 m diameter, origin at the sphere center |
| WSC-PLAN-005 | Skittle pin | 248 | 8,908 | Separate ivory pin with a floor pivot |
| WSC-PLAN-006 | Pressure plate | 664 | 53,536 | Four-meter frame with a separate moving tread |

Static Blender art candidates. The pivots are authored for later integration; this does not implement hinges, physics colliders, a press-to-open gate, a score counter or mobile runtime proof.

Rebuild and validate with Blender 4.3 and Python from repository root:

```sh
out=/absolute/scratch/west-physics-props
blender -b -t 6 --factory-startup --python-exit-code 1 --python scripts/blender/showcase-studies/physics_props.py -- "$out"
python3 scripts/blender/showcase-studies/check_physics_props.py "$out"
```

Set `WSC_PHYSICS_RENDER=1` for the separate studio preview. No .blend file or embedded textures required.

Coverage ledger: W4a/W4b now have four standalone art exports under the original IDs. Scene, native integration and physics proof remain separate. The next breadth pass should rotate out of W4 and reconcile an equipment, travel or Vault family; don't count existing scene props or aliases as missing models.

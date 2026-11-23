# November 23 · Seven existing catalogue assets verified

Seven already tracked GLBs were reimported for a new review sheet.
These are not new models. File names under
`public/assets/wildshard-art/` remain unchanged.

| Catalogue ID | Tracked GLB | Status clarification |
| --- | --- | --- |
| WSC-PROP-002 | utility-bollard.glb | Safety bollard, static study |
| WSC-PROP-003 | haul-crate.glb | Cargo crate, distinct from Crate Mite |
| WSC-PROP-004 | wall-lantern.glb | Wall mount only; post mount not proved |
| WSC-PROP-005 | market-awning-stall.glb | Freestanding market stall WIP |
| WSC-MODULE-029 | window-shutter-module.glb | Recessed window WIP |
| WSC-PLAN-007 | wsc-plan-007-mover-jump-pad-casing.glb | Inert casing |
| WSC-PLAN-008 | wsc-plan-008-horse-mounting-block-wip.glb | Mounting block WIP |

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/catalogue_reimport.py -- /tmp/wsc-audit
```

The output report identifies actual hashes, reimport triangle counts
and original dimensions. The contact sheet scales each asset to fit
its display tile and does not compare real-world size or certify
production acceptance, rider interaction, physics or placement.

# W9b: the two high West vistas

Round 5's layout keeps ★2 on the Movers Tank roof at
(−206, 18, −104) and ★3 on the Grapple tower top at (−212, 45, −34).
The lab draws both physical bench proxies 2 m in positive world Z
from their discovery anchors. These are not the Grapple water-tank
hook or the tower's fourth-deck Gold.

- **★2 Movers Tank.** The original bench proxy is supported by the
  unchanged 18 m steel roof. The bench faces the Grapple tower's
  cyan crown. Keeping the proxy at its original offset also leaves
  the centre-mounted hook pedestal in place.
- **★3 Grapple tower.** The original bench proxy falls outside the
  walkable mesh of the current zipline-aligned art. The discovery
  anchor remains a plan reference. The *visual bench* moves 2.502 m
  horizontally onto the reimported 45.05 m boards and looks toward
  the existing zip-house roof. The tower, departure and rail meshes
  are unchanged.

The original WSC-PROP-044 bench is reused twice. The only new asset
is one small GLB with two separate survey badges, 02 and 03. The
canonical whole-town scene is reproducible; it is not included in
the export. Fifteen floor probes under each original bench shape and
five under each badge check the proposed seat offsets. The measured
seated eye is 1.48 m above each roof; a wider camera shows each seat
and its destination. The background mountains and lighting are review
dressing, not live scenery. This is not a discovery trigger, bench
interactable, scene transfer, structural check or native collision.

```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/west-town/build.py -- --output /tmp/whole-town
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/roof_vista_pair.py -- /tmp/whole-town /tmp/w9b-roofs
node scripts/blender/showcase-studies/check_roof_vista_badges.mjs \
  /tmp/w9b-roofs/w9b-roof-vista-badges.glb
```

[W9b six vistas](../../docs/plans/kitchen-sink-v2/slices/W9b-vistas-caches-gold-finds.md)
· [Compact fit receipt](../layouts/w9b-roof-vista-proof.json)

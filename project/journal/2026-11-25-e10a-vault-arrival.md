# E10a Training Vault arrival lobby

This room precedes the four E10c trial rooms. It stages a cyan ceiling, copper ribs, dark utility cassettes, and amber approach markers. The **SURFACE** pedestal sits outside the center aisle so the way back can be distinguished from the existing circular training bulkhead. The pedestal is an independent mesh, not a transport button. The round bulkhead is previewed from its unchanged donor and is not packed into either download.

| Export | Bytes | Triangles |
| --- | ---: | ---: |
| Arrival shell | 527,964 | 6,801 |
| Return pedestal | 50,028 | 675 |

Three-space art datum is [166, −38, −83] within E10a's specified interior volume. The center envelope is 2.256 m wide. On the separate model geometry, all 1,020 clearance samples passed, and 2,553 downward samples found floor 3 to 7 mm below the datum. Samples exclude the unmodified closed training door and are not a capsule or game collision proof. Both exports reopened in Blender with no coincident or zero-area faces and in Three.js with the expected footprints. No textures or bundled lights. Preview lamps are not runtime light settings.

This does not add a room host, Keycard grant, portal link, streaming, collision, sound, or scores. If integrating later, first verify the pinned SDK/engine can admit the plan's interior resident state; a walk-in transport link alone does not satisfy E10a.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/vault_entry_hall.py -- /tmp/e10a-arrival
```

Measured receipt: `project/layouts/e10a-vault-arrival.json`. Plan: `docs/plans/kitchen-sink-v2/slices/E10a-portal-interiors.md`.

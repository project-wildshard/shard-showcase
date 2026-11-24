# E10b: Vault record plate and room seal indicator

The E10b entrance best-time plate is a new freestanding static model.
It has a fixed BEST label and blank dashes, not a fabricated run. The
second model is a door-side seal indicator with two versions that share
an envelope: cyan chevron for open, amber cross for sealed. The symbols
carry the distinction without relying on colour alone. These are
proposed art cues and no game state switches them yet.

| Export | Bytes | Triangles |
| --- | ---: | ---: |
| Record plate | 45,324 | 724 |
| Open indicator | 14,788 | 200 |
| Sealed indicator | 14,972 | 206 |

The reimport scene keeps the exact exterior portal GLB unscaled. The
plaque has 0.265 m of lateral separation from the outside of the shell.
The two indicator variants have the same measured bounding dimensions.
Both toolchains, Blender 4.3.2 and Three.js, reimported all three files.
The light rail in the preview is a presentation stand, not a new room.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/vault_checkpoint_fixtures.py \
  -- /tmp/vault-checkpoint-fixtures
```

Set `WILDSHARD_VALIDATE_ONLY=1` for meshes and checks without renders.
See [donor hash and measurements](../layouts/e10b-vault-checkpoint-fixtures.json).
No timer, checkpoint, seal, wave, collision or deployment change.

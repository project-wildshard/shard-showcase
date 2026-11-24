# E10a Training Vault iris, active art only

E08 shows a turquoise aperture inside the gate arch. Add an optional
animated iris rather than filling or editing the existing opening.
The original WSC-ARCH-007 frame bytes are pinned and unchanged. The
effect takes the same origin as the frame, with tapered ribbons and fine edge traces
inside the aperture. The middle stays transparent rather than using
a solid surface. Preview lights and the slate stage are not shipped.

The reimported GLB carries one three-second shape-weight animation
with matching endpoint geometry. Twelve poses interpolate around the
oval; no textures, physical surface, or runtime state are added.
A separate BVH of the original gate checks the ribbon samples against
the visible frame at 25 points in time. This is an overlap check along
the look-through axis, not native collider, renderer, or phone QA.

The original frame is the inactive visual. This study does not
implement a keycard grant, door opening, interior pass-through,
teleport, exposure transition, or gameplay hook.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/vault_iris.py -- /tmp/vault-iris
```

[E10a portal plan](../../docs/plans/kitchen-sink-v2/slices/E10a-portal-interiors.md)
· [E08 original mockup](https://github.com/Raynos/project-wildshard-singleplayer/blob/8c56c4616b2bc26dbd9da03945dfd340e875ecce/art/showcase-template/round-11-remaster/east/e08.jpg).

For a silent motion review, set `WSC_VAULT_IRIS_CLIP=1` before the
same Blender command. Encode its 48 preview frames at 16 frames/s:

```sh
ffmpeg -framerate 16 -i /tmp/vault-iris/clip/%03d.png \
  -c:v libx264 -pix_fmt yuv420p -movflags +faststart /tmp/vault-iris/review.mp4
```

# E02 dock: layered facing on the E03 core

The [E02 mockup](https://github.com/Raynos/project-wildshard-singleplayer/blob/8c56c4616b2bc26dbd9da03945dfd340e875ecce/art/showcase-template/round-11-remaster/east/e02.jpg)
shows a cyan crown, inset three-band face, raised metal frame, and orange
lower caps. The existing WSC-PROP-053 model is the simpler E03 look.
An unchanged instance remains alongside the proposed E02 facing. The
back and exact dimensions cannot be reconstructed from this image; the
four-way repeat and shared-shell treatment are proposals.

The accessory GLB contains four unique part meshes (frame, caps, bands,
crown) used by sixteen nodes. File size is 69,640 bytes, with 1,056 unique
triangles and 4,224 after instance expansion. The actual E03 body is not
copied into the accessory. Load both at the same origin for the preview;
the frame deliberately overlaps the original sloping shell in places.
The added trim is about 2.131 m across. On this geometry the upper trim
starts about 136 mm outside the original landing-pad edge; the donor
and its pad plane at 0.554 m stay unchanged. This is not a qualified
attachment or docking fit. No physics, lights, activation, or spawns.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/e02_dock_face.py -- /tmp/e02-dock-proof
```

Outputs are the accessory GLB, validation JSON, and two rendered views
from the reimported geometry. The staging floor and lighting are separate.

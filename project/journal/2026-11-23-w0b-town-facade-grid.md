# W0b town houses: one wall grid for multiple heights

The plan calls for 35 houses built from repeated parts, with 2–4 storeys.
[W01](https://github.com/Raynos/project-wildshard-singleplayer/blob/8c56c4616b2bc26dbd9da03945dfd340e875ecce/art/showcase-template/round-11-remaster/west/w01.jpg)
shows the cream walls, limestone corners, gable roof and shutter rhythm.
This is a visual assembly exercise within WSC-ARCH-003, not 35 individually
authored buildings or an exact reconstruction of the W01 block.

The optional 163,708-byte GLB is five assembly parts with 2,860 triangles:
wall, ashlar plinth, L-shaped quoin, stringcourse, and eave trim. They share
a local panel convention. The wall is 4.4 m across, 3.1 m tall and 0.20 m
deep; panel front is local Blender Y=0. Front/back are full span; each return
uses the same wall scaled to 3.6 m along its local horizontal axis. The
returns end at the inside faces of the fronts. The corner relief conceals
the wall junction; decorative trim may overlap at corners intentionally.

The script stages a 4.4 × 4 m footprint at two and three storeys using
linked object instances. Five pinned donors remain unchanged: the original
arched door, shutter window, terracotta gable, flower box and street planter.
The front plinth breaks around the door frame. The moulding and eaves are
separate parts, not fused into any donor. Window and door assets dress the
solid wall fronts; this pack does not make openings navigable, add interiors,
or imply any native placement, walk test, collision or draw-call result.

Rebuild the GLB, validation JSON and two previews from a clean art checkout:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/town_facade_grid.py -- /tmp/w0b-facades
```

The overview camera includes the full three-storey ridge with margin; the
detail camera intentionally crops in to show how trims meet the corner.

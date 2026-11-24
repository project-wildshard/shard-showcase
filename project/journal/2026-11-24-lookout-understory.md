# Rock lookout: low trail foliage

Add two optional understory prototypes alongside the existing W11
sandstone, lupines and buttercups. The fern adds broad, arching leafy
silhouettes; the folded verge blades fill openings without another
flower color. These are art proposals, not species identified in the
old image or new catalogue IDs.

Both editable recipe outputs use one vertex-color material, no
textures and no decoder. The trail preview instances the two meshes
15 times beside exact pinned sandstone, distant wildflowers and two
existing distant tree variants. One radial bound per prototype keeps
all new plant geometry outside a staged 2 m strip. This is a
conservative art-only test; other props, collision, runtime placement
and performance are not covered.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/lookout_understory.py \
  -- /tmp/lookout-understory
```

Blender reimports both exports before the studio and trail shots.
The proof JSON records their topology, bounds, and placement margin.

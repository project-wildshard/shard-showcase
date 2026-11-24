# West Plaza and East Gate: two paving inlays

A terracotta compass medallion picks up the separate circular inlay in W01, while two warm stone ribbons pick up the East Gate approach in M07. Colors and exact dimensions are an art interpretation, not measurements of the illustrations. The W11a wet-paving study and underlying Town shell are unchanged.

- Compass medallion: 4.81 m diameter with cut terracotta, pale stone and a blue-slate center. Centered at Blender (−26, −3), distinct from the obelisk.
- Ribbon: one 3.75 m × 0.78 m mesh repeated four times along each side of the 15 m approach. The 9 mm difference between the two assembled top datums follows the two underlying surfaces. Pair is mirrored by placement, not different art.
- The fit receipt in `project/layouts/w0b-paving-inlays.json` records 14,351 vertical samples on the freshly rebuilt Town donor. The intact plaza spans 0.090–0.099 m; the apron is at 0.082 m. The installed art is a thin overlay, not a replacement walk surface. Heights are 5–13 mm over the highest sampled donor at each location before the compass center detail, which rises a further 4 mm.
- Town WIP semantic parity passed at signature `e6bbb20e18adbc863c18fd637211e6c8a35ae4a01deed667d071f4850dce7b4f` (2,692 authored/imported components). GLBs use no textures; Both exports reopened with zero degenerate triangles in Blender; Three.js verified footprint and thickness. The medallion is 44,844 B and 880 triangles. The reusable ribbon is 17,624 B and 334 triangles. Staged fit only; no collider, road, clock, encounter, or phone behavior claims.

```sh
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-town/build.py -- --output /tmp/paving-town
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/west_paving_inlays.py -- \
  --town /tmp/paving-town/whole-town-WIP.glb --output /tmp/paving-variants
```

# W11 lookout flowers: distant variant and border study

WSC-PROP-047 is the existing flowering clump. Its purple lupine spires and
gold buttercups are visible beside the sandstone and timber in the original
[W11 Rock lookout](https://github.com/Raynos/project-wildshard-singleplayer/blob/8c56c4616b2bc26dbd9da03945dfd340e875ecce/art/showcase-template/round-11-remaster/west/w11.jpg).
The editable asset here is the pinned GLB plus its distance-geometry script.
The original stays untouched. This is an optional lighter candidate, not a
scene change or an automatic LOD switch.

| Reimport audit | Original | Distant |
| --- | ---: | ---: |
| Raw GLB bytes | 539,260 | 177,752 |
| Triangles | 20,622 | 5,556 |
| Primitives | 2 | 2 |

Both keep vertex color on stems and petals; there are no textures, skins, or
animations. XY bounds are unchanged; lowest/highest vertices move less than
1 mm. Reimported masks across 8 directions and 2 elevations share a minimum
92.26% and mean 94.47% intersection over union. Thin petal detail does change.
The mask test is geometry only and does not establish draw time, frame rate,
a switch distance, or acceptance in the native client.

The daylight border is a standalone dressing composition, not the whole W11
scene or authoritative placements. It reuses exactly the released boulder,
deck bay, bench, and guardrail. The three closest clumps use the original;
twelve smaller/distant clumps use this candidate. The soil and lighting are
presentation. No donor duplication or scene file is needed.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/lookout_flower_distance.py -- /tmp/w11-flowers
```

The output is one distant GLB, two review JPEGs, and validation.json.

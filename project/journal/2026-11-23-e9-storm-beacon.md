# November 23 · E9 Storm Hour beacon

WSC-KIT-007, based on the E9 plan and the catalogue four-view
illustration. The 5.47 m tower has orange warning flanges, armored
panels, maintenance ladder, exterior conduit, and an open cage.
The unlit tower stays unchanged for the charged look: add the small
emissive lamp GLB at the same transform. The lamp bottoms at the
4.67 m seat and the mesh check finds 83 mm conservative radial
clearance above the seat. The dark tower is not emissive.

Rebuild and verify with Blender 4.3.2 and standard Python:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/storm_beacon.py -- /tmp/e9
python scripts/blender/showcase-studies/check_storm_beacon.py /tmp/e9
```

Set `WSC_BEACON_RENDER=1` to see a reimport of the exact exports
side by side. The tower is 244,772 bytes / 5,164 triangles. The optional
lamp adds 16,052 bytes / 260 triangles. No textures, caches, .blend
snapshots, or other external data are required to rebuild.

The ladder is decorative. Lighting here is a material study, not a
game implementation of the quest, activation, collision, weather hold,
sound, four map placements or native performance. Placement and scale
are art proposals, not layout decisions.

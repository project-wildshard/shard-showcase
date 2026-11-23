# Crate Titan bowl (WSC-SCENE-008): environment study

This is the separate underground **Crate Titan** space, not Nalati's
Storm Titan room or the surface gate. A pale circular slab, amber edge
band, pale/dark tiers, chevron banners, and four floodlight bridges
carry the E13/E14 remaster's visual cues into a reusable first-pass
environment. The portraits are evidence for the palette and silhouettes,
not for hidden dimensions or live attack tells.

The layout JSON pins Round 5 and current E12g: centre x/z 150/165,
floor y −150, sky y −80 (metadata only), 52 m floor radius, 56 m
wall edge at 8 m high, stands out to 70 m and 24 m high. Diagonal lane
headings and cardinal covers are the plan's. Lane width is 10 m.
The southern pocket is 16 m × 14 m before the decorative threshold
overlap. The stand sectors, light placements, and trim are inferred.
The south exit and checkpoint are visual placeholders, not triggers.

Rebuild from repo root with Blender 4.3:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/titan_bowl.py -- /tmp/wsc-titan-bowl
```

Deterministic geometry and materials are grouped by part for editing:
slab, band, lanes, wall, terraces, pocket, crate covers, floodlight
bridges and banners. The script reimports the exported GLB before
rendering. Blender x east, y north, z up; glTF x east, y up, z south.
The 6 m slab lies below the origin. The GLB has no embedded textures,
animations, studio lights or cameras. Blender lights are for evidence
renders only. Validation records size, triangle count, reimport meshes,
and bounds. No boss model or rig, cutscene, world placement, colliders,
performance benchmark, or native encounter was implemented here.

# Storm Hour: distant lightning silhouette

W11a and E9 specify an evening storm and thunder. This standalone
art pass proposes one cold, branched flash above the existing warm
beacon. It does not infer a strike location or change the quest.

The small GLB uses one emissive material and two crossed ribbons
per section. Its origin is the upper branch seed. Geometry and
emission are static; no animation, textures, sound, or gameplay
are embedded. The proof JSON carries a proposed normalized
single-pulse curve for review, not a connected host or timing rule.

Both stills reimport the same exact beacon and charged lamp. Only
the visible bolt, feathered cloud glow and diffuse fill light
change between the two exposure-matched frames. The cloudy sky,
wet concrete and lights belong to the preview and do not ship in
the GLB. No native weather, sound, exposure or accessibility UX
was implemented. No repeating or autoplaying flash is published.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/storm_sky_flash.py \
  -- /tmp/storm-sky
```

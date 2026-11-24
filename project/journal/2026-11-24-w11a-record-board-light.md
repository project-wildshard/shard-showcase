# W11a · One roof light for two record displays

The day/night plan calls out personal-best boards in addition to street and gate lanterns. This study fits one unscaled 0.88 m fixture to two existing exports: the Movers BEST/LAST board and the Range timer. It does not touch the riding timer, replace role labels or invent any record values. The neutral GLB stores the shade, lens and mount, not a light engine component.

At both candidates the bracket center is 0.12 m toward the front from the donor origin in Blender. All 18 contact samples per board match the exact mount plane (Movers y-up 2.835 m, Range 1.245 m). The first emitter position hit the deep Movers visor; moving the lens outward cleared the ray to the title. The final reader and emitter rays both clear the title area of each donor. This verifies just the sample rays, not glare, electrical design, device or animation behavior. The source preserves original text, rest materials, fixture poses and camera in both previews; only the in-studio light source and lens emission change. A riser aligns the shorter Range timer in the comparison, not in the map.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/record_board_lamp.py -- /tmp/record-light
```

Use `WILDSHARD_VALIDATE_ONLY=1` for exact reimport checks without rendering. Rebuilt GLB and measurement JSON are byte-identical. Three loads the 39,768 B / 440-triangle neutral fixture. No clock row, runtime light, timer or world placement has changed.

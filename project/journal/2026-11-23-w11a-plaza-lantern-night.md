# West Plaza day and blue hour (W11a lighting study)

W11a asks for a West town that reads at night. This matched
Blender pair lights three copies of the existing shared street
lantern. The W01 board, storefront, awning and paving are from
the pinned quest-trio stage; the camera is wider but stays at
1.7 m. This is a new comparison, not a replacement for the
earlier obelisk daylight, original W01, or quest-giver portraits.

Matching stage geometry, camera, exposure, and color management
leaves light as the only variable. The mounted glass center
starts at post-local Blender (0, −0.732, 2.661) m. A separate
preview point emitter is offset 77 mm forward and 212 mm down
from that center so the glass housing doesn't swallow its light.
Each post's yaw rotates both the fixture and emitter offsets.
Blue-hour sky and rim light retain the house and path silhouette.
The existing GLBs and their material settings are unchanged.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/plaza_lantern_night.py -- /tmp/wsc-plaza-night
```

The script checks pinned file hashes, visible fixture centers
and identical scene geometry transforms across both renders.
The point values are studio choices only. No native day clock,
light emitter rows, gate or obelisk glow, PB board light, weather,
runtime optimization or gameplay was implemented.

# W2b: modular stock display

W2b lists the Sword, Spear, Bow and Crossbow as store stock.
This study reimports those four exact exports at unchanged scale.
It proposes two fixtures related to WSC-ARCH-006, a wool-lined
three-bay wall display and a compact felt counter riser. These
can dress a frontage or a temporary shop booth; W0b still does
not add a walk-in interior. There is no inventory UI or sale.

The stock wall is 46,024 B / 724 triangles; the riser is 35,000 B /
528 triangles. Both are untextured static GLBs with a bottom-center
pivot. Blender reimports each fixture and each gear donor. The receipt
checks separation of the three tall silhouettes, the wall and riser,
and that the Crossbow's projected footprint fits on the riser.
These are bounds checks, not a mount or collision certification.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/west_stock_display.py \
  -- /tmp/w2b-stock-study
```

Use `WILDSHARD_VALIDATE_ONLY=1` to skip the gallery renders.
See [measured placement and donor hashes](../layouts/w2b-stock-display.json).
The scene is rebuilt from the script; no duplicate gear or scene GLB.

# W3b practice plank

W3b calls for three prop stations at 20 m. The existing unlit straw
bale and soft dummy already have standalone studies; the plank did not.
W06 polished uses a round vermilion mark. The export recreates that
read without claiming the screenshot as an exact mesh or scale source.

The five chamfered larch boards carry modeled grain marks and chipped
paint. The part has a single mesh, no textures, and a floor-centered
origin. The dummy, straw bale and backstop are pinned donor models and
are placed unscaled for the stills, not copied into the plank GLB.

Run from the repository root:
```sh
blender -b -t 6 --python-exit-code 1 \
  --python scripts/blender/showcase-studies/range_practice_plank.py -- \
  /absolute/scratch/w3b-practice
```

The direct Blender reimport is photographed in detail, as a trio and
from 20 m with a 1.70 m eye and 50-degree horizontal FOV. The center
mark is about 31 pixels across in the 1,240 pixel plate. No gameplay
placement, projectiles, impact, burning, stagger or scoring is added.

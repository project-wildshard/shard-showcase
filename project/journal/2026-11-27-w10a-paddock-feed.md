# W10a: a feed bin next to the paddock trough

A standalone oak and iron feed bin with a shallow heap of hay.
It sits at (-57, 0, -100) in Three, five meters west of the
existing trough's ground pivot. No change to the trough, fence,
chute or mounting block, and no extra feed logic. Exact Blender
reimports leave a 2.0875 m horizontal gap from the trough mesh
and keep the bin 9.8375 m outside the 12 m chute's side line.

The GLB contains only the feed bin: no landscape, fence or camera.
The review ground and short fence stretch are contextual scenery.
The placement is a proposal, not an animal use, collision, rendering
performance, or live level test. No additional stable catalogue ID.

Rebuild from the repository root with Blender 4.3.2:

```sh
D=/tmp/w10a-feed
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/w10a-feed/build.py -- "$D"
cmp "$D/fit.json" project/layouts/w10a-paddock-feed-fit.json
cmp "$D/w10a-paddock-feed-bin.glb" public/assets/wildshard-art/w10a-paddock-feed-bin.glb
```

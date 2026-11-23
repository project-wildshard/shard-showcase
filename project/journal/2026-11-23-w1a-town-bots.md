# November 23 · W1a town dev-bots

First model studies for WSC-PLAN-001 (stable hand) and WSC-PLAN-002
(weapons keeper). The stable hand has a canvas apron, stable badge and
orange vest. The keeper has a blue collar, split coat and copper cuffs.
Both follow the plan illustrations and share the same mechanical body,
21-joint hierarchy, atlas and small three-second idle. They are not
variants of the Tinker Rook storefront. Catalogue role labels stay
unchanged; proposed character names are not promoted to canon.

Build and verify with Blender 4.3.2 and standard Python:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/town_bots.py -- /tmp/w1a
python scripts/blender/showcase-studies/check_town_bots.py /tmp/w1a
```

Set `WSC_TOWN_BOT_RENDER=1` for a studio view made from the reimported
GLBs. The builder recreates the two small atlas images and rest
landmarks. The GLBs are 400,308 B and 428,788 B, with 3,396 and 3,512
triangles respectively. The validator checks one skinned primitive each,
weights, joint names/order/hierarchy, exact atlas reuse, and motion and
loop closure from actual GLB buffers. No .blend, cache or source texture
downloads are required.

This is studio output, not integrated NPCs. The pinned figure host
rebinds raw geometry to declared rest points and drives movement itself.
It requires a native standing fallback and a separate material with
albedo and normal maps; neither is in this pass. The generated toe
positions are approximate authoring landmarks, not tested IK targets.
Dialogue, vendor inventory, stable behavior, look fitting, walk and
point motion, and native admission remain to be validated.

# W1a: Surveyor | WSC-ACTOR-017

The tier-two West Plaza quest NPC now has a rigged art study. The existing
W1a body generator supplies the same 21 joints and 64×64 atlas; the
stable hand and weapons keeper still rebuild byte for byte. Surveyor
has no apron or long coat. The original visibility vest and pale tape
are supplemented with a temple optic, pocket slate and rear datum patch.
The optic and slate are costume geometry, not game tools.

The render uses a lossless decode of the packed GLB. The packer welds
identical vertex data, reorders the buffers, and verifies attributes,
oriented triangles, weights, inverse binds, joint order and animation
samplers after decode. It does not quantize the positions. The packed
129,432-byte download is below the catalogue's proposed 180,000 bytes.
There is one mesh, one primitive/material, 3,920 triangles and one
3-second idle loop. The Blender action is `Idle_Studio`; the exported GLB
clip is named `Animation`. The GLB requires a Meshopt decoder;
it does not include native actor placement, portrait, dialogue, talk,
idle blending, level conditions, collision or animations beyond that clip.

Build from repository root with Blender 4.3.2, Node, @gltf-transform
core/extensions/functions 4.5.0 and meshoptimizer 1.2.0:

```sh
S=scripts/blender/showcase-studies
WSC_TOWN_SURVEYOR=1 blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python "$S/town_bots.py" -- /tmp/surveyor
node "$S/surveyor_pack.mjs" /absolute/node_modules /tmp/surveyor
python "$S/check_town_bots.py" public/assets/wildshard-art \
  /tmp/surveyor/surveyor-decoded-for-blender.glb
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python "$S/surveyor_reimport.py" -- /tmp/surveyor
```

Only the packed variant is tracked. The raw authoring export and
decoded intermediate are not added to the branch.

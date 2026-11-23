# November 23 · W01 shared lantern on a post

WSC-PROP-004 identified reuse between wall and post mounts. The
verified wall lantern is kept byte-identical. This pass exports only
a compatible 3.476 m floor-standing post with a forged shaft, basalt
footing and flat pad. The post is 37,232 bytes and 620 triangles.

In Blender Z-up coordinates use the tracked lantern at
`(0, -.182, 2.27)` m relative to the grounded post. In glTF Y-up
coordinates this is `(0, 2.27, .182)`. The reimport check verifies
the donor digest, position, mounting plane and separation. The wall
lantern remains a separate GLB, not baked into the new post.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/lantern_post.py -- /tmp/w01-post
```

Set `WSC_LANTERN_POST_RENDER=1` for the staged reimport. This is
a modular art proposal, not a confirmed location or a game-lighting
change. No new catalogue ID is needed.

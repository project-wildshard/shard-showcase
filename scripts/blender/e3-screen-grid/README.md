# Band 3 suspended screens: exact-placement movement fixture

Reuse the one source screen GLB, instanced at the 19 positions in the
archived Round 5 layout that preserve an 8 m open radius measured from
the whole projected screen envelope to the nearest pack center. Eight
other positions are kept in the ledger but not placed in the fixture.
These are older blockout pack anchors, not the final E3 population plan.

Each accepted instance has four simple closed collider boxes: two posts,
the high panel, and the beam. Local positive X runs along the crossbar.
The stock player can cross below the panel at three offsets in both
directions, but both solid posts stop direct approaches. The fixture
includes all 19 accepted instances on a flat floor, without enemies.
Three routes walk from the old Band 3 entry coordinates to screen 26
and back. Routes and proxy positions are visible in the tracked receipt.

Copy the verified Round 5 layout, placement and lab files into a scratch
directory with a Node ESM package.json (`{"type":"module"}`). The
extractor verifies exact Git blob hashes. The sight-fit calculation is
conservative and does not assert that a drone should be occluded by the
cloth. The pictures add staged materials and foliage, not game terrain.

```sh
node scripts/blender/e3-screen-grid/extract.mjs /path/to/round5 /tmp/e3-layout.json
WSC_NODE_PROJECT=/path/to/pinned-engine-deps node --experimental-transform-types \
  scripts/blender/e3-screen-grid/check.mjs /tmp/e3-layout.json /tmp/e3-proof.json
cmp /tmp/e3-proof.json project/layouts/e3-screen-grid-proof.json
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e3-screen-grid/render.py -- /tmp/e3-layout.json /tmp/e3-images
```

Screen mesh source: [drone_pillar_screen.py](../showcase-studies/drone_pillar_screen.py).

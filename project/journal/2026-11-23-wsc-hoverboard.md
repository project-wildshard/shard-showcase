# November 23 · Native hoverboard catalogue export

WSC-PROP-032 uses the exact procedural board geometry shared by the
riding view and Model Explorer in engine 0.1.44,
`f61079f816be881c405796b597e5523fdd9061df`, Three.js 0.186.0.
The exporter runs the pinned builder rather than recreating W07's
partially seen board. It verifies the source digest, geometry count and
material classes and converts the latter into four standard materials.
It does not make a change to the game or load path.

The static GLB is 122,392 bytes. Its 1,232 solid triangles are the
dark deck (524), grip (140), rim, nose lamp and inlay (376), and two
repulsors (192). The original live pulse and 48 additive halo triangles
are deliberately absent. The cyan parts have fixed emissive settings.
The native -Z nose and Model Explorer's +0.061 m vertical lift are
preserved. Without the discarded halos, the repulsor lower face is
14 mm above the floor reference.

From the repository root with Node 24 and the pinned, already installed
engine dependency (or equivalent pinned engine checkout with deps):

```sh
node scripts/blender/hoverboard/export.mjs /path/to/engine /tmp/wsc-board
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/hoverboard/reimport.py -- /tmp/wsc-board
```

Set `WSC_HOVERBOARD_RENDER=1` for a top and underside composition.
No engine source copies, caches, or editable binaries are needed.
The tested static appearance does not qualify rider controls,
tricks, physics, or the runtime shader.

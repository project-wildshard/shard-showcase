# West Hover Park: source-only static art WIP

From the repository root, use Blender 4.3.2 and the repository Node environment:

```sh
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-hover/build.py -- --output /absolute/scratch/west-hover
```

The build pins four additional tracked donors (three native kicker GLBs and
one seven-piece run-up), regenerates Climb/Rock and builds Hover Park without
altering any predecessor mesh. Generated outputs stay outside this checkout;
no private input or download is needed. No fresh render is generated.

West placement: ce1cf050b3 round-4 layout.js HOVER/ZONE 11 and lab.js buildHover
(Round 5 retained West); current W5a/STATE MK1/D7 supersede older profiles and
heights. Measured zone is 134 × 122 m. Three aligned lanes use exact 2.4/3.6/4.8 m
donor crests and shared 45 × 3.9 m strips without rescaling. Launch walls are
45 m long, with a 4.5 m design crest; the nonvertical profile and 26 m visual
width are explicit art decisions. Other park obstacles and path dressing
are static inferred geometry.

The build checks reviewed semantic geometry, inherited meshes, actual native
and reimported lane/strip/wall measurements and retained zipline endpoints.
Only the prior W08 untextured arm UV exception (5.96e-8) is allowed by semantic
comparison; the output GLB itself is not altered. No ride-fit, phone, runtime,
physics, scoring, performance, gameplay or production validation; no new IDs.

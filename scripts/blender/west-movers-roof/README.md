# West Movers and shared roof: source-only static WIP

Continuation atop verified r02 recipe. No assembled GLB, native file, render or
duplicate asset is committed. Requires Blender4.3.2 and its built-in glTF/Bfont.

From repository root:
`blender -b -t 6 --python scripts/blender/west-movers-roof/build.py -- --output /absolute/scratch/west-continuation`

Output must be outside checkout. The driver rebuilds tracked r02, checks five
additional tracked asset hashes, builds six static Movers stations, then the
shared roof/tank/rope bridge. No external downloads or private runtime inputs.
Outputs include both scenes, native editable files and parity.json.

movers.py is the reviewed unique assembly/structures/signage and unscaled shared
asset placements. junction.py is the authored tank, native cedar planks, ropes,
rails and hook proxy. It removes one central west return rail to open departure,
and includes the final12mm threshold correction. This preserves reviewed
18.012m threshold tops on18m walking planes, not a new structural claim.

expected.json pins the original reviewed output hashes and canonical semantic
fingerprints. The existing r02 semantic checker compares positions,normals,UVs,
triangle winding/topology, material contents and instance transforms while
ignoring exporter ordering and arbitrary material names. Both stage fingerprints
must match; byte-identical GLBs are not promised. No fresh render is claimed by
this build. The reviewed visual framing remains in the original private study.

Source layout: Raynos/project-wildshard-singleplayer@ce1cf050b3,
art/showcase-template/round-5-blockout/layout.js, West unchanged in round5.
Movers zone BlenderX[-168,-70],Y[74,132], sequence axisY103.
Tank center(-206,104),radius16m,roof18m; bridge endpoints
(-168,103,18) and(-190,104,18). Plank1.6m width and0.65m sag are inferred.
Relevant tracked plans: W6c-rope-bridges.md,W7a-grapple-course.md and Movers plans.

Static art WIP only. Slider/spinner/lift/hook poses are illustrative.
No gameplay, collision, timing, jumpability, phone/mobile/runtime performance,
horse fit, engineering or quality acceptance. No new catalog IDs.

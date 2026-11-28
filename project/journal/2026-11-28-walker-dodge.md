# Walker: load, tuck, plant

Replace Walker's mirrored squat dodge with a side-loaded launch, staggered tuck and left-leg plant. Key the off-hand, boots, chest, pack and coat separately. The original rig remains editable in Blender; geometry, three sockets and the other eleven clip signatures are unchanged.

The pose now samples actual dodge progress instead of starting a separate render clock. No root motion, dodge distance or invulnerable window changes. The Blender builder samples both boots and bakes a pelvis height correction where the new poses would clip the floor. The verifier checks all integer and quarter frames; these are conservative boot-box samples, not a foot-locking solution.

In separate 402 × 874 portrait Chromium runs, a trusted touch produced the same 2.40 m forward displacement and returned to Idle before and after. The new pose stayed aligned to simulation progression. The Node suite, GLB checks and minified build passed. No physical iPhone test or game deployment.

Rebuild via `scripts/blender/forge-walker/build.py` and run `blender -b art/actors/forge-walker/walker.blend --python-exit-code 1 --python scripts/blender/forge-walker/verify-dodge-clearance.py`. The browser A/B runner is `demos/forge-yard/walker-dodge-smoke.mjs <local-yard-url> <out> <baseline-js> <baseline-glb>`.

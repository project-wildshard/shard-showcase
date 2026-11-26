# W10b: westbound lap and missed-ring replay

A mounting and steering bench for the authored stadium oval and
eight unchanged ring centres from `w10b-riding-course-study.json`.
The R02 gantry starts the westbound example. The engine's existing
mount installer and native Rapier motor ride a continuous path using
scripted rein commands, no position overwrites. The harness uses a
flat box at the track datum, not the scene's full collision geometry.

An offline scorer intersects each recorded movement segment with
planes at the ring centres, oriented to the course tangent. In this
bench the middle 4 m count as a hit; within the 12 m track but outside
that band is a miss. Crossing the gantry forward twice only counts
when all eight ring planes have been visited in order. The scorer
adds the approved 5 s per missed ring. A partial, reversed, or
early-finish trace does not produce a record. This is **horizontal
checkpoint calibration**, not clearance through the circular GLB.

From three starting offsets (−0.5, 0, +0.5 m), all clean laps hit
2→1→8→7→6→5→4→3 and measured 45.469 s. The matched Ring 1 bypass
registered seven hits, one miss, and exactly 5 s of penalty in
each replay. The centred comparison was 45.517 s raw, 50.517 s
adjusted; it passed 3.07 m from Ring 1's centre. The clean
centreline error is below 0.67 m, and the intentional bypass
stays within 3.10 m of that line.

This is not a shipped course row or PB, a human lap time, gate
collision, jump exercise, mounted rig fit, or phone playtest.
The four obstacles are not loaded. Integrating the proven westbound
rail and rechecking height/jump clearances are separate tasks.

From art root (Engine 0.1.44; set WSC_NODE_PROJECT to the dependency
checkout if missing locally):

```sh
d=/tmp/w10b-lap
mkdir -p "$d"
node --experimental-transform-types demos/native-riding-lap/sample.mjs "$d/proof.json" "$d/trace.json"
cmp "$d/proof.json" project/layouts/w10b-riding-lap-proof.json
node demos/native-riding-lap/render.mjs "$d/trace.json" "$d"
for v in map penalty; do inkscape "$d/nov26-w10b-lap-$v.svg" -o "$d/$v.png"; done
```

Review boards are generated from the recorded traces. The lap
receipt is retained; full trace and generated diagrams are not
checked in on the art branch.

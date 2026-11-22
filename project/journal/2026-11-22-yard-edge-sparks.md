# 2026-11-22: readable hit feedback at portrait edges

Pinned the actual Chrome camera at the 150 ms impact and at 200 ms, the
same distance at center, left, right and offscreen. An edge hit could take
24 HP without leaving visible sparks, particularly on the right.
For near-edge confirmed damage, the burst now moves to an approximation
of the camera-side shoulder, capped at 31 cm tangentially. Centered
feedback stays at the old point. Nothing changes in the swing pose,
damage, aim, offscreen gate, or timing. This is readable feedback, not
an exact blade-to-mesh contact fix.

All 25 focused tests passed. Controlled Chrome captures at 402 × 874
show sparks on both edges during follow-through. The previous baseline and
new build both registered 70 → 46 HP at the edges, and 70 → 70 offscreen.
The diagnostic fixture is not part of the published build.

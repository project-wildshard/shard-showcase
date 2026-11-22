# Skip invisible yard props in Canvas fallback

The portrait software painter used to transform loaded scenery and visit every triangle before checking if any of it was on screen. Opt only the rigid dock, crate and gantry meshes into four padded screen-plane tests. Work with transformed bounds, not projected centers. Never clip by the camera far plane (the painter never did); keep skinned meshes, the viewmodel, paint and gameplay unchanged. The original GLBs remain the editable source exports.

Run `node --test demos/mite-yard/*.test.mjs`. The renderer regression captures Canvas path submissions across 50 yaw/roll/pitch and aspect combinations, including transformed nested meshes, a long piece spanning the viewport, a near-plane crossing and a prop beyond the camera far clip.

In Chrome with Canvas forced at 402 × 874, the centered opening visited 19,186 triangles before and 14,014 after, with 8,261 paint paths either way. A pixel comparison over nine yaw angles found no changes. On this cloud session, fixed-pose render call p50/p95 was 24.6/28.0 ms before and 24.0/29.4 ms after (40 warm samples per variant, alternating batches). The 50 ms median animation-frame callback interval did not improve. This is a reduction in geometry processing, not a measured device frame-rate improvement.

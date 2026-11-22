# 2026-11-22: concrete aggregate on the playable apron

Replaced the flat colour slabs with a shared 128 × 128 procedural mineral
grain. The repeat is 1.65 m and anchored to world coordinates; existing joints,
paint, wear, and shadows remain layered separately. Three uses mipmapped
metric UVs. The software renderer uses a half-resolution floor projection
with a reusable buffer, caches it while the view holds still, and fades
microdetail towards the horizon. No texture downloads, new geometry, or
collision changes.

Observed in 402 × 874 Chrome using the software fallback. A controlled
side-by-side showed the grain at an identical pose. A first, more expensive
strip renderer was rejected. In a 120-frame stationary retest, the current
and baseline builds were both around 66.7 ms median and 83.4 ms p95 on the
cloud browser; this is not a physical-phone or movement benchmark. The
standalone touch fight ended at 54 HP with one Servo. WebGL path built but
was not visually exercised by that browser. All 20 focused tests passed.

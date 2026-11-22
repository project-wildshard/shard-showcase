# 2026-11-22: ground the Mite in sunlight

The software renderer now adds a tapered shadow behind the Mite and dock,
using the same sun vector as WebGL. Contact stays darkest below their bases.
The cast direction stays fixed as the Mite turns, softens when it breaks
apart, and fades at the yard boundary. Gantry contact and the WebGL shadow
map are unchanged. Shadows draw below the cyan warning. No textures, light
map, wall shadow, or combat changes.

The complete focused suite passes (23 tests). Verified the live windup in
402 × 874 Chrome and the caster outlines from a second, matched test angle.
This remains an approximation for the software fallback, not a rendered
shadow map or a physical iPhone test.

# E3 Band 3: Plumb Drone warning art

The [Band 3 plan](../../../docs/plans/kitchen-sink-v2/slices/E3-band3-plumb-drones.md) calls for a 0.7 s plumb-line warning. This art splits it into a high signal beam and a ground read so the player can follow the direction even when an endpoint is off the phone screen. The warm core stays narrow while the side marks widen; both collapse at 700 ms. They are textureless unlit surfaces. The clips do not emit light and need no bloom.

These are reusable visuals, **not an actor**: no rig, projectile, hitbox, collision, attack, triggering, occlusion policy, or native placement. The matched renders are at 1.72 m eye height in a 15 m flat-floor setup with the exact existing E3 screen and perch, not a shipped scene or device playtest.

- Beam: 22,740 bytes, 180 triangles. Local +X from 0 to 1. Rotate the entire loaded scene's +X from the effect origin to the supplied target and scale only local X by the distance. Its peak continuous core is 70 mm wide; collars are up to 122 mm.
- Floor: 13,220 bytes, 96 triangles. Fit local +X from the projected origin to the supplied floor target with the same X-only scale. Peak width 1.23 m. Use a verified 6 mm height bias on a flat floor; conform to uneven surfaces before product use. The floor markers are not a replacement for the game-defined warning width.
- Start the two 0.70 s clips simultaneously, one shot. Remove the visual or clamp at the final shape. Where a smaller field or overhead occlusion changes the cue, determine visibility in the gameplay renderer; these meshes do not bypass cover.

Rebuild from repo root with Blender 4.3.2 and a pinned project with Three.js installed:

```sh
T=/tmp/e3-plumb
D=scripts/blender/plumb-cue
blender -b --factory-startup -t 4 --python-exit-code 1 --python "$D/build.py" -- "$T"
node "$D/check.mjs" "$T"
blender -b --factory-startup -t 12 --python-exit-code 1 --python "$D/render.py" -- "$T"
```

Set `WSC_NODE_PROJECT` to the absolute Node project path if needed. The proof checks actual GLTFLoader/Mixer playback at six clip times, exactly folded final triangles, endpoints at nine 3–5 m height × 12–18 m span pairs, and peak projection estimates across 27 camera poses. The minimum 4.02 px nominal beam-core span is a geometric estimate at 402×874, not a human readability score. Both renders use matched framing.

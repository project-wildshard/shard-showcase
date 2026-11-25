# E4 Welder: floor warning study
The band-4 plan calls for a blue-to-orange 0.8 s wind-up, then a 6 m cone and a separate six-second slag hazard. This is only the floor outline for that first cue. There is no new actor, torch, fire, timing, hitbox, or installed behavior. The existing Foundry and cover-bay GLBs are unchanged and used only to show scale.

The wedge uses a 6 m **radial** reach, not a 6 m rectangular bounding box. The 28° half-angle is a preview choice, not a gameplay value. Use the attack's actual wedge half-angle and dispatch timing before integration. Place the origin at the gameplay wedge apex, local forward glTF −Z, with Y up. Here the flat visual is 6 mm above the test floor to avoid sharing its surface. On stepped or uneven terrain a projected decal or clipped triangles would be needed to avoid floating and bleeding through walls. Keep the boundary and indicator renderer-only. Do not infer damage from mesh contact.

```sh
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/e4-welder-cue/build.py -- /tmp/e4-welder
blender -b --factory-startup --python-exit-code 1 \
  --python scripts/blender/e4-welder-cue/build.py -- /tmp/e4-welder-34 --half-angle 34 --no-render
```

One mesh, two emissive materials, 176 triangles. No images, UVs, lights, bloom, or animation in the GLB. Reimport checks upward-facing geometry, exact reach, angular containment and plane height. Default captures verify all footprint vertices fit inside both frame margins. The portrait view is 10 m horizontally from the apex at 1.68 m eye height; it tests composition, not a phone GPU, timing, combat readability under impact effects, or occlusion by a Welder.

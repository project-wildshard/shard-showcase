# E12h / WSC-SCENE-008 — interior sky for the high stand shot

E12g gives the hidden arena its own sky and a 70 m ceiling above the slab. E12h's 30 m stand camera needs both the far stands and the sky in frame. This optional shell replaces the old flat preview backdrop with a low-contrast blue storm shelf, not an enclosed roof. The palette is deliberately subdued so it does not compete with the arena's floodlights or a future Titan.

Origin is the arena slab centre; import at identity alongside the matching bowl (pin in layout proof). GLB +Y is up. The shell has inward faces, reaches local Y=70, and extends to 114 m radius beyond the 70 m bowl. It belongs in an isolated interior presentation scene, not the overworld. One unlit material, one primitive, no textures, collision, lights, actors, or gameplay. A runtime sky shader may use the same palette instead; this does not install or replace the game sky.

From repository root with Blender 4.3.2:
```sh
O=/tmp/titan-sky
blender -b -t 6 --factory-startup --python-exit-code 1 --python scripts/blender/titan-arena-sky/build.py -- "$O"
WSC_SKY_RENDER=1 blender -b -t 6 --factory-startup --python-exit-code 1 --python scripts/blender/titan-arena-sky/review.py -- "$O"
```

Without `WSC_SKY_RENDER=1`, the second step only checks geometry: reimport the exact donor and shell, project a 72×100 grid through each of the four previous cameras, confirm all 6,830 missing donor rays meet an inward shell face, and confirm no donor ray changes first-hit geometry. The two renders include the existing 15 m and 6 m rulers, not actors. Blender source and deterministic scene reconstruction, not the preview renders, are the editable handoff.

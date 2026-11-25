# W3c virtual steel target

The West plan's Q12 chooses a swinging plate. This standalone game-art
prop packages the graphite and orange frame, zinc-edged plate and cream
mark, with a single triggerable 1.4 s swing-and-mint clip. The stand stays
stationary and its pivot is separate, so a future runtime can use a
geometry-independent response. There is no real-world fixture intent.

Run from the art checkout using Blender 4.3.2, Three.js and Python Pillow:

```sh
D=/tmp/w3c-target
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/west-steel-target/build.py -- "$D"
node scripts/blender/west-steel-target/check.mjs "$D/w3c-swing-steel-target.glb" "$D/check.json"
python scripts/blender/west-steel-target/review.py "$D" "$D/check.json"
```

The Blender scene generates the deliverable and edits stay in the Python
source. Set W3C_ASSET_ONLY=1 to skip renders. Three.js reimport checks track
identity, endpoints, swing angles and the width/height envelopes at all 85
samples. Review-stage stills are not the actual range; the eye stays 1.70 m
above a flat stage, at the three distances called out by the plan. The mint
cue survives at 75 m without bloom (20 active pixels vs. zero in the idle
frame within the same ROI). Short pixel evidence is not a phone visibility
or accessibility verdict.

No map placement, sound, impact test, weapon, scoring, or PB controller.
The engine receives none of these animations automatically. Reuse the same
export, not duplicate copies per distance. Measurements: `project/layouts/w3c-swing-target.json`.

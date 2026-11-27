# Portrait combat · a smaller sword-contact cue

The point of this pass is to show the hit without losing the enemy.
The prototype starts at an explicit contact point on the existing
Pallet Jack study. A small amber core lasts 52 ms, while seven tapered
sparks travel mostly along the blade tangent and away from the surface.
Everything is off by 155 ms. The cue uses one depth-tested geometry
batch and does not add a screen flash, point light, or bloom pass. No
new actor, weapon, camera, damage rule, or animation was made.

Six 402 × 874 review cameras (3.7 and 5.5 m, straight on and ±27°)
test eight moments with depth-aware ray casts. The highest fraction
of sampled enemy silhouette overlapped by the cue was 1.04%, and the
cue was visible at onset from all six views. A deliberately broad
sphere obscured 27.56–74.64%; that is a test control, not an estimate
of a shipping effect. No claim about GPU performance or luminance
follows from these ray tests.

The two Blender stills use only the existing public art. The camera
does not move and the enemy is not playing a clip. This is neither
an installed combat patch nor a successful sword-hit or retreat test.
Next, test the cue on a real confirmed hit with the existing player
and enemy animations; check that contacting steel, missing, revving
and being hit each read distinctly. Preserve damage timing, visible
blade travel, audio/hit-stop, and the physical iPhone acceptance gate.

## Run

```sh
node --test demos/mite-yard/contact-cue/contact.test.mjs
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python demos/mite-yard/contact-cue/render.py -- /tmp/contact-review
cmp /tmp/contact-review/wsc-portrait-contact-proof.json \
  project/layouts/wsc-portrait-contact-proof.json
```

Set `WSC_NODE_PROJECT` to the existing pinned Node
environment if Three.js isn't installed in this checkout. Append
`--proof-only` to the Blender command to skip rendering. The event
adapter in `contact.mjs` takes a contact point, outward normal and
blade tangent in Three.js coordinates. The caller owns event selection
and the clock, and should advance the visual age in seconds even if
simulation hit-stop holds the poses.

# Use the blade pose from the hit tick

The Fable reference at `3afcd88` updates and evaluates Rook before combat advances the sword phase. The confirmed damage can therefore be shown against the previous animation pose. Pointing a tiny glint at the old tip is not enough; read the actual blade after the new swing phase has been written and evaluated.

## Rig measurement

The probe uses the pinned unmodified Rook rig, animation/IK/fit modules, the original decoded source skeletons, and the Shop Blade's actual base and tip sockets. A minimal adapter omits production shaders, drawn mesh selection, LOD and shadows. No Fable assets or source are checked into Wildshard. Root stays fixed, all input is scripted (random seed 293), and the swing/effect boundary is modeled rather than running Fable combat. No claim is made about physical blade–armor contact.

Three update rates (30/60/120 Hz), two modeled wind-up rates (1.0 and 0.65), five moves (both light attacks, third hit, held heavy's release curve, dodge counter) give 30 matched comparisons. At 60 Hz unslowed, measuring the current instead of the previous phase moved the tip 0.62 m on the third cut and 0.93 m on the counter. The logical hit tick stayed identical in both paths. Blade segment length stayed constant in all cases.

## Candidate presentation boundary

1. Resolve the existing game rules and emit confirmed damage with the simulation tick, attack phase and weapon instance.
2. Evaluate the hero rig **once** with the final presentation phase for that tick. If splitting an actual update, keep locomotion/input and combat resolution order intact; do not run the animation/cloth timers twice.
3. For matching tick/phase/weapon and positive damage, read base and tip behind that fence. The candidate rejects previous pose, swapped weapon, whiff, immune hit, missing/canceled phase and duplicate. This supplies the shown blade for the effect, **not the physical impact point or a damage rule**. A later real contact check needs the swept segment and Jack surface; do not force a sparkle onto armor when they disagree.

This is editable adapter and proof, not a native or Fable patch. Still needs actual moving Rook/Jack, target contact, default camera, casual combat cadence and an iPhone run.

## Reproduce

```sh
node --test demos/mite-yard/sword-presentation/contact-after-pose.test.mjs
node --experimental-transform-types demos/mite-yard/sword-presentation/probe.mjs /path/to/authorized-reference /path/to/dependency-project
python demos/mite-yard/sword-presentation/sheet.py project/layouts/wsc-sword-presentation-proof.json /tmp/sword-sockets.jpg
```

The probe requires Node 24, Three (r186 used in this comparison) and `@gltf-transform/core` + `@gltf-transform/extensions` in the dependency project. It verifies Git blob IDs before running. Reference rig source and meshes stay outside this repository.

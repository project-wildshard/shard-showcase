# Pallet Jack sword impact: preserve the armor underneath the hit

Fable's golden comparison 09 is the third ordinary sword swing against a common Jack, not the cinematic Finish. That swing has heavy feedback but does not use the held level-two full-screen effect. The pinned reference sets the enemy material mix to white at weight 1 and subtracts 7 per simulation second. Hit-stop scales simulation time to 0.04, so material wash can outlast the readable part of the cut.

## What changed in this study

- Trigger a body pulse only from a confirmed sword melee strike that dealt positive damage, not from the planned swing time, a target in range, a whiff or an immune contact. Keep a distinct hit ID per actor and present the pulse on the same render frame.
- Replace, rather than add to, the ordinary white body wash. The display-age envelope peaks at 0.22 and quadratically fades to zero by 75 ms even during hit-stop. It obeys the flash accessibility setting. This preserves at least 78% of differences in the pre-tone-map actor radiance with a constant white mix target. This is **not** the percentage of visible screen contrast.
- Keep the same scope: no extra light, full-screen overlay, damage or animation changes. Do not erase status tints, charge tells, stagger or death. The adapter in a real runtime must hand control back to those tints immediately at zero and leave other weapons and the special Finish behavior alone.

## Matched comparison

Both pairs use the existing Pallet Jack study, the existing directional spark cue and the same pose, lens and lighting. Only the actor material white mix varies. The values shown are an idealized continuous-clock envelope for 110 ms heavy hit-stop, not exact engine tick samples. At +33 ms the baseline model is 0.991 versus 0.068; at +100 ms it is 0.972 versus 0. Blender approximates the outgoing-light mix with an emissive shader blend. It is not a pixel match to Three.js tone mapping or a replay of the golden shot. No Fable changes, gameplay changes, runtime integration or device test.

## Reproduce

```sh
node --test demos/mite-yard/body-flash/pulse.test.mjs demos/mite-yard/contact-cue/contact.test.mjs
node demos/mite-yard/body-flash/proof.mjs | cmp - project/layouts/wsc-jack-body-flash-proof.json
blender -b -t 6 --factory-startup --python-exit-code 1 --python demos/mite-yard/contact-cue/render.py -- /tmp/jack-wash --body-flash-ab
python demos/mite-yard/body-flash/sheet.py /tmp/jack-wash /tmp/jack-wash/compare.jpg
```

Next acceptance: same normal landed third strike before/after in one naturally triggered Jack duel. Hold the material, impact and camera comparisons separately; log attack phase, real and sim time, exact hit tick, damage, hold vs light, and onscreen blade–armor position. A whiff should produce no contact pulse. Confirm overlay/text, portrait drag and side-dodge behavior in real iPhone Safari.

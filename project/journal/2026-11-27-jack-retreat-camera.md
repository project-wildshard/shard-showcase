# Pallet Jack: keep the charge tell through a tactical backstep

At 402 × 874 and 60 Hz, the pinned Fable camera and engagement logic turns the camera away before the end of the Jack’s 950 ms wind-up. For one straight and one diagonal scripted backstep, the tell anchor left the viewport at 583 ms and 567 ms respectively. This is a camera-projection measurement, not a physical iPhone playtest or an assertion about what the HUD renders.

**Candidate:** For the already selected and framed Jack only, suppress the automatic fleeing swing during its active daytime charge wind-up (cap 950 ms). End on wind-up exit, released stick, sprint, manual look, explicit clear, target change, camera mode/assist change or interruption. Arm once on wind-up entry, not after the player has already left, and do not rearm on the same attack. Leave selection, manual look, movement and the underlying flee timer untouched. This is not a global lock-on or a replacement camera.

| Case | Original | Candidate |
| --- | --- | --- |
| Straight / diagonal backstep | Tell anchor visible 34 / 33 of 57 frames | 57 / 57 of 57, within the inner viewport |
| 400 ms backstep | 57 of 57 | 57 of 57 |
| Continued escape | Automatic swing starts 417 ms; selection drops at 3,017 ms | Swing starts 967 ms; selection still drops at 3,017 ms |
| Sprint away | Starts escaping on first frame | Same trace |
| Explicit look | 62° of input during 18 frames | Same 62°; hold canceled at first drag frame, no re-arm |
| Assist disabled / no charge | Original behavior | Same trace |

The manual drag can move the tell off screen. That is intentional: the filter does not override the user. The clipping test uses a single fixed eye-height anchor; “inner viewport” is ±0.8 horizontal and ±0.82 vertical NDC, not the HUD’s safe area. Open-space camera test only: wall/eave collision, actual player motion, a moving or obscured tell, edge warning arrows and browser/phone frame pacing were not run. Wall checks and a real level-four iPhone duel are gates before considering it playable.

## Editable and repeatable

- `demos/mite-yard/retreat-camera/policy.mjs`: standalone camera-feed proposal, not installed.
- `node --test demos/mite-yard/retreat-camera/policy.test.mjs`: 15 positive/negative checks.
- `node --experimental-transform-types demos/mite-yard/retreat-camera/probe.mjs /path/to/authorized-reference /path/to/dependency-project`: executes the pinned camera/engagement with scripted movement and null collision queries. Node 24, Three r186 for the checked snapshot. The reference’s declared Three version is r187; check with its locked package before adoption. The probe verifies five Git blob hashes before loading and writes the proof (or live per-frame samples with `--full`). No reference code or images are bundled.
- `project/layouts/wsc-jack-retreat-camera-proof.json`: measured results and camera transforms.
- `blender -b -t 6 --factory-startup --python-exit-code 1 --python demos/mite-yard/retreat-camera/render.py -- /tmp/jack-camera`: two original comparison stills at 750 ms. Existing Wildshard Jack model with a minimal stage and player marker. Not game captures.

No Fable or Wildshard runtime changes, new actor, gameplay or deployment.

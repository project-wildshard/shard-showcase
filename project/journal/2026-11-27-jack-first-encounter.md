# Read the Jack’s first charge without taking over the camera

The retreat framing candidate starts only with a selected Jack. A natural common Jack can begin a ram at 5–15 m while sword auto-target radius starts at 9 m plus target size. At 12 m, test the independent floor, pose and original edge tell before considering any camera change. Keep the existing locked-target rule separate.

The probe loads the pinned reference animation and Pallet skeleton, the daytime charge definition (0.95 s wind-up, 0.75 s active, 1.1 s recovery, 2.2 × 14 m lane), and the existing edge-warning decision. It advances movement pose, wind-up, ram, recovery, stagger and death on the original rig. Head and fork sockets, plus the original emission scalar, are sampled. The wind-up emission rises from 1.0 to 3.16 by the last sampled frame. Reference meshes and source stay outside our repo.

| 402 × 874 fixture | Head or fork visible | Floor sample visible | Existing edge warning | Proposed extra warning |
| --- | ---: | ---: | ---: | ---: |
| Unselected Jack at 12 m, open | 57/57 | 57/57 | 0/57 | 0/57 |
| At 12 m, crate corner | 0/57 | 57/57 | 0/57 | 0/57 |
| At 12 m, turned away | 0/57 | 0/57 | 57/57 | 0/57 |
| All cues hidden; artificially confirmed reachable | 0/57 | 0/57 | 0/57 | 57/57 |
| All cues hidden; lane blocked | 0/57 | 0/57 | 0/57 | 0/57 |

“Visible” is geometry: clip bounds and ray–box intersections to actual rig sockets; floor visibility means at least three of 18 independent points. It is not tested reader comprehension, GPU rendering, or live hit collision. The fully hidden reach boolean is an explicit test input, not a conclusion about any crate’s gameplay behavior.

**Decision:** leave the open and corner cases alone. The floor already carries enough geometric evidence to test on a phone, and the stock off-screen arrow works when turned away. Only consider a supplemental HUD cue if a current, authoritative lane can reach the player and both the body and floor are hidden, with no existing edge warning. No guessed threat, new target, camera turn, damage change, or installed HUD. Candidate cannot run in gameplay until the receiver supplies reach/occlusion. A normal, no-cheat 12 m approach and 6–8 m selected backstep near a real crate corner remain the acceptance tests. Record wall and sim clocks separately during hit-stop.

## Reproduce

```sh
node --test demos/mite-yard/jack-warning/visibility.test.mjs
node --experimental-transform-types demos/mite-yard/jack-warning/probe.mjs /path/to/authorized-reference /path/to/dependency-project
blender -b -t 6 --factory-startup --python-exit-code 1 --python demos/mite-yard/jack-warning/render.py -- /tmp/jack-warning
python demos/mite-yard/jack-warning/sheet.py /tmp/jack-warning project/layouts/wsc-jack-warning-proof.json /tmp/jack-warning.jpg
```

The probe verifies source Git blob IDs. Its fixed input stages no native combat state selection, aim lock, camera collision, actual player movement, physics, browser HUD, or device behavior. The renders use original Wildshard art rather than reference assets. No Fable changes or game deployment.

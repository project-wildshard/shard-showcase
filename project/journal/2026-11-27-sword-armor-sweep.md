# A positive sword hit does not guarantee visible blade contact

The previous probe made it possible to test the visible blade on the confirmed hit tick. This pass replayed the prior-to-current base/tip sweep for the third cut and dodge counter against the pinned Fable Pallet Jack **rest mesh** with its 1.18 truck-bone adjustment. The original asset is not part of this repository or in the public image.

The 216 pairings span three update rates, two wind-up speeds, three lateral offsets, and six fixed spacings. The 1.9 m third-cut and 2.1 m counter spacings are modeled capsule targets (attack range minus 1.3 m from the lunge source), not distances from the visible surface or measured player destinations. With the centered nominal 60 Hz swing, the closest sampled blade-to-armor gaps there were 0.64 m and 1.68 m. No farther tested placement (108 at 1.9–2.6 m) got inside a 6 cm glint threshold. Thirteen closer cases did; one needed the sweep instead of the last pose alone. Repeating at twice the subdivision on both axes changed the sampled minimum by less than 13 mm in every case. The sweep is a linear interpolation of measured sockets, not continuous live blade or Jack motion.

**Rendering decision:** leave existing game rules, sound, damage numbers and reactions alone. In the candidate, a metal glint can use a nearby displayed armor point only after positive confirmed sword damage and a matching blade, hit, weapon instance and target surface. If there is no sufficiently close surface, use existing hit feedback without placing an invented glint at the chassis center. Do not shorten hit range or force the hero forward based on this rest test.

## Reproduce

```sh
node --test demos/mite-yard/sword-presentation/{contact-after-pose,surface-cue}.test.mjs
node demos/mite-yard/sword-presentation/surface-source.mjs /path/to/reference/pallet.glb /path/to/dependency-project > /tmp/wsc-jack-rest-private.json
blender -b -t 2 --factory-startup --python-exit-code 1 --python demos/mite-yard/sword-presentation/sweep-proof.py -- /tmp/wsc-jack-rest-private.json project/layouts/wsc-sword-presentation-proof.json /tmp/wsc-sweep.json
cmp /tmp/wsc-sweep.json project/layouts/wsc-sword-armor-sweep-proof.json
python demos/mite-yard/sword-presentation/surface-sheet.py /tmp/wsc-sweep.json /tmp/wsc-sweep.jpg
```

Keep the extracted triangles private. The exact asset hash is checked by the adapter; only distance summaries go in Git. No live integration or device run. Next test must log root motion, Jack pose, exact hit tick and actual gap in a natural selected level-four duel before proposing changes to a lunge, reach or rig. The v293 heavy *curve sample* is not the warmed held-release sequence; held attacks are outside this comparison.

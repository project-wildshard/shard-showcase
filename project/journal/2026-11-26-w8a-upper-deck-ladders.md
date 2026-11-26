# W8a · Ten- and fourteen-metre ladder fit

Extend the Deck A bench to original Decks B and C. The source climb yard
is unchanged. The stock ladder installer and Rapier capsule use original
deck centers, tread height and gap dimensions in separate controlled runs.
Each climbs from the ground, lands on the deck and returns to ground with
ordinary movement. No position overwrite after the initial test spawn.
Mid-climb save/restore reproduces 177 ticks (B) and 237 ticks (C) exactly.

Both top handoffs are sensitive to analog input. From the same landed
snapshot on each deck, five approach inputs (40%, 55%, 70%, 85%, 100%)
were replayed, switching to full input only once aligned to the ladder.
The 70% approach reduced the largest single downward step from 85 to
61 mm on B and from 92 to 64 mm on C. Slower was not always smoother.
Aligned motion stayed at 33.4 mm per tick or below. This comparison is
not an automatic input policy or an iPhone recommendation.

| Deck | Authored height | Ground to landing | Guard-gap width |
|---|---:|---:|---:|
| B | 10 m | 5.65 s | 1.5 m |
| C | 14 m | 7.65 s | 1.5 m |

For each rebuilt art deck, 25 floor rays, 15 tread rays, 30 guard-gap
rays and a ray beneath the measured landing prove the physical fit
against the pinned visual source. Markers in the Blender images show
recorded positions, not a game character or phone capture.

**Product limit:** as with Deck A, the normal native room does not
install the route in the pinned build. The test explicitly lends the
stock ladder installer; the normal room control fails to attach and
falls from the top. No normal-room fix, bridges, other ladders,
multiplayer behavior, on-device controls or live changes.

Use the existing [Deck A recipe](../../demos/native-deck-a-ladder/README.md)
to build the local fixture and exact art. With the same pinned versions:

```sh
for deck in B C; do
  WSC_CLIMB_DECK="$deck" WSC_NODE_PROJECT="$deps" \
    node --experimental-transform-types demos/native-deck-a-ladder/sample.mjs \
    "$fixture" "$out/$deck.json"
  blender -b -t 6 --factory-startup --python-exit-code 1 \
    --python demos/native-deck-a-ladder/review.py -- \
    "$climb_base" "$out/$deck.json" "$out/$deck-review"
done
node demos/native-deck-a-ladder/summarize-upper.mjs "$out" "$out/w8a-upper-deck-ladder-proof.json"
```

Here `deps` is the pinned dependency project's directory, `fixture` the
local admitted product, `climb_base` the original Blender rebuild
directory and `out` an existing scratch directory.

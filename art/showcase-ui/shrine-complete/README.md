# UI-30 · Shrine Complete / D56

The approved behavior is in `UI-PICKS.md` and `slices/DECISIONS.md` (D56) on main, with the card and shrine host in E10b. Reference: archived Round 12 `ui-30-shrine-complete-after.jpg`, `ce1cf050b36fa236155ac26d43e721b9012c49df`, blob `f9fe6181721c2aa7890aec5bdfb177e16c37237d`. The reference is a mockup over a different shard; it is neither imported nor published here.

This portrait review reuses the public Training Vault Lockdown room render. Numbers match the approved example: 11:42, new best, two deaths, four rooms, 150 Scrip / Plate Core and Warden’s Plate in the summary. It is not an authoritative loot table. Continue only dismisses. The next layer is explicitly a schematic, not an alternate HUD: the marker walks past the chest and must cross the threshold to leave. Walking back over the threshold starts a new example run; puzzle/chest state for a new run is outside the review's scope. No card buttons for leaving, restarting or claiming rewards.

Copy `index.html`, `model.mjs`, `board.mjs` and `review.mjs` to the Catalog's `dist/shrine-complete/`. It resolves the backdrop in the adjacent `media/` folder. Run the tests and rebuild the two 402 × 874 vector boards at 2× (using Inkscape/ImageMagick):

```sh
d=art/showcase-ui/shrine-complete
out=$(mktemp -d)
node "$d/check.mjs"
WSC_NODE_PROJECT=/absolute/test/project node "$d/dom-check.mjs" # happy-dom installed in test project
node "$d/render.mjs" ../wildshard-publish-website/dist/media/nov24-vault-r4-idle.jpg "$out"
for n in nov25-ui30-shrine-complete nov25-ui30-portal-route; do
  inkscape "$out/$n.svg" --export-width=804 --export-filename="$out/$n.png"
  convert "$out/$n.png" -quality 91 "$out/$n.webp"
done
```

No interaction with live saves, rooms, rewards, timers, achievements or world coordinates. SVG renders were reviewed at 402 px; DOM transitions were tested headlessly, not on physical iPhone.

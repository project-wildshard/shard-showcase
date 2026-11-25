# E1f / UI-16 portrait contract board

This visual review brings the approved wood panel and pinned paper cards
to the present E1f plan. It illustrates Scrap Patrol at level 1: 20 Crate
Mites, 20 Scrip plus a wall trophy and Pest Control on the first claim,
20 Scrip only on repeats. Big Pallet (level 6) and the Vault Warden (level 12)
show the locked style. The three visible rows are only a subset.

Approved reference: Raynos/project-wildshard-singleplayer at ce1cf050b36fa236155ac26d43e721b9012c49df,
art/showcase-template/round-12-ui/ui-16-contract-board-after.jpg
(blob f0213ca293d4e64d27007977367b9990d82a6cba). Use the E1f slice and UI-PICKS
for current reward direction. The prototype's illustrative amounts and
“Scrip and parts” footer are not game data.

The board reuses a published Gate Plaza render, not an in-game screenshot.
The editable vector source emits three frames, not button handlers, reward
grants, save changes, or playable UI. Counting before acceptance is not
decided here.

## Reproduce

Provide dist/media/nov23-east-boundary-plaza.jpg from the website branch at
4abf5a30664df0b1f0043962b007046a4bdb32c1. The renderer verifies its digest.

```sh
p=art/showcase-ui/contract-board
o=/absolute/scratch/contract-board
node "$p/render.mjs" /path/to/nov23-east-boundary-plaza.jpg "$o"
node "$p/check.mjs" "$o"
for s in progress first repeat; do
  inkscape "$o/e1f-contract-$s.svg" -w 804 -o "$o/e1f-contract-$s.png"
  magick "$o/e1f-contract-$s.png" -strip -quality 89 -define webp:method=6 "$o/nov25-e1f-contract-$s.webp"
done
```

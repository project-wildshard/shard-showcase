# E0f / UI-10 Character and Gear

The approved bag has five top tabs: Map, Character, Finds, Pack, Feats.
Character opens first by default; Gear is nested within it. The layout keeps
all seven attributes, level-par markers, separate aptitude arrows, and the
derived readouts visible at 402 × 874. These are two editable vector boards.
The buttons are visual and do not open the live Bag or equip weapons.

The exact approved original is
`Raynos/project-wildshard-singleplayer@ce1cf050b36fa236155ac26d43e721b9012c49df:art/showcase-template/round-12-ui/ui-10-character-tab-after.jpg`
(blob `9a8b33b3562c44a55872297e932dff0e66b40c9e`), cross-checked with
UI-PICKS and D49. The original is illustration, not production data.
This comparison swaps the Driftwood label for Showcase, keeps the sample
level and XP, and completes the derived panel using a clearly illustrative
same-level fixture based on §15 of the levels/combat plan. Line items are
not balance, XP, equipment, or profile assertions. The two gear pictures
are standalone vector icons and the slot labels are sample content.

## Reproduce
Use the exact `nov23-west-plaza-day.jpg` already on the website branch
at `680f5e9096d19f5ef035624a0507fbd4fa6ba0f9`. No original archive image
is needed for a rebuild. From the art root:

```sh
D=/tmp/wildshard-ui10
p=art/showcase-ui/character-tab
node "$p/render.mjs" /path/to/nov23-west-plaza-day.jpg "$D"
node "$p/check.mjs" "$D"
for s in character gear; do
  inkscape "$D/ui10-$s.svg" -w 804 -o "$D/ui10-$s.png"
done
```

MDEF/armour sample mitigation is against equal-level par,
the fail roll is before LUK's save, and both crit chances assume equal level.
Bar length compares each attribute locally to its own par; it doesn't use a
single shared raw unit. Character stays read-only. No E332 shared-HUD wiring,
runtime combat, character saves, private backdrop, or live install is included.

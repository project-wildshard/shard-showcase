# W9b / E13: FINDS in the portrait Bag

Two editable portrait reference states, following the approved five-tab
Bag layout in UI-10. Character remains the default Bag tab; these
boards show FINDS already selected. They do not change the live Bag
or UI-18's separate one-line discovery toast.

W9b defines 8 vistas, 6 cosmetic caches, and 20 Gold 1×1s. A
Calibration Chip milestone arrives every five Gold (four total).
The separate 12 East Scrip chest placements in E13 do not increment
the cosmetic cache counter. We show illustrative counts and three
sample personal-best rows; not all launch records are listed. A
missing result is not shown as a zero. Time values are rendered as
minutes, seconds and hundredths; skittles show pins out of ten.
The sample-state function validates counts and the verification
covers every Gold count from 0 through 20.

Use the unchanged public `nov23-west-plaza-day.jpg` in the website
branch, shared with the UI-10 Character board. The script pins its
SHA-256. Generate 402 × 874 SVGs at 2× raster size from the art root:

```sh
d=/tmp/wildshard-finds
p=art/showcase-ui/finds-tab
node "$p/render.mjs" /path/to/nov23-west-plaza-day.jpg "$d"
node "$p/check.mjs" "$d"
for s in new trail; do
  inkscape "$d/finds-$s.svg" -w 804 -o "$d/finds-$s.png"
done
```

No playtest, live record table, saves, collectible placement, reward
claim, toast, or game integration. No generated background duplicate
or raster source is tracked on this branch.

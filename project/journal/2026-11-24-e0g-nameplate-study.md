# E0f / E0g · Nameplate and stagger tint art board

The 144 × 39 CSS-pixel plate is a review candidate, not active UI. Four same-crop examples show (1) separate HP and thin amber stagger fill, (2) a burn tint on the side edge without periodic damage numerals, (3) a full striped stagger bar so the state does not depend on a color change, (4) a single shock tint taking the edge instead of burn. The level prefix keeps its independent example con color. There is no blast tint: the plan's blast is knockback. HP values, meter amounts and sample level are illustrative, not combat balance or timing evidence. The 25 m filter, overlap, float limit, accessibility at device scale, precise timings, and status behavior are not implemented/tested.

The standalone vector has four viewBox-aligned symbols (steady, burn, full, shock) and a neutral default render. It includes no external resources. The composition takes a pinned copy of an existing public catalogue image, not a capture from the native game. The source plate is `dist/media/nov22-mite-dock-court.webp` on website commit `e28de134037ad6296349bb9c5f85d28affdcbf01`. The compositor uses ImageMagick and Inkscape, and checks text/edge colors against the opaque plate backing. Local rebuild returned identical SVG and JPEG bytes. Regenerate without checking a duplicate game screenshot into art:

```sh
python3 project/ui/e0g-nameplate-study.py /tmp/nameplate /path/to/nov22-mite-dock-court.webp
```

No native HUD edit or change to the public audience.

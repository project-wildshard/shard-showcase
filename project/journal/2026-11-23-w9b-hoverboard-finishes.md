# W9b: four West cache hoverboard finish proposals

Oval Ochre, Rock Jade, Alley Violet and North Frost are cosmetic palette
proposals for W9b/D26, not rewards assigned to placed chests. No XP, Scrip,
perk or speed effects. The native board and default cyan render remain
unchanged.

The alternate GLB stores four named `KHR_materials_variants` mappings
for the deck, grip, illuminated trim and repulsors. The 118,272-byte
binary payload matches the existing 1,232-triangle board exactly. There
are no duplicate geometry buffers inside this GLB. The alternate is
126,860 bytes, only 4,468 B above the original 122,392 B. The original
GLB remains an engine-parity reference and stays tracked separately.

The default material slots are unchanged. A viewer without the optional
material-variants extension will show the default board, not four boards.
Blender proof resolves each mapping directly out of the exact export and
reimports it into the studio. These are static tones; no runtime pulse,
halo, material-selection UI, chest choice, unlock or placement validated.

From the repository root:

```sh
S=scripts/blender/hoverboard
python "$S/cache_finishes.py" /tmp/board-finishes
blender -b -t 6 --factory-startup --python-exit-code 1 \
 --python "$S/cache_finishes_reimport.py" -- /tmp/board-finishes
```

Only the variant-enabled GLB and a small palette report are tracked.
Four resolved preview GLBs, source geometry exports and studio setup
are rebuildable; none are committed.

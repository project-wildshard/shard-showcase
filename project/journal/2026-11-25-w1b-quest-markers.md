# W1b · Quest giver marks

UI-12 (approved in UI-PICKS and D60) asks for flat outlined marks close to
the head, with the name above. Round 12 `proto.css` blob
`297dff6669b7ac8c15239b30833338144cbee418` pins the 40 px glyph, 8 px label,
1.5 px stroke, warm yellow and cool grey. Four W1b states are shown across
three matched 402 × 874 CSS-pixel portraits: Surveyor holds the locked grey
`!`; Yard Boss changes yellow `!` → yellow `?` → no marker. The Shift Boss
remains in the composition without a marker in this example. The old diamond
is absent only in these new alternate plates. All three tracked 21-joint
rigs, poses, plaza pieces and the fascia remain unchanged.

No quest flags, gating, minimap, visibility/occlusion policy, native HUD or
game install. Blender camera is at 1.70 m; evaluated head vertex projection
gives anchors. The raster proof puts outlined ink four CSS pixels above the
cap; a reusable DOM/CSS sketch matches the size and palette, but the browser
capture is optional (this cloud image lacks the Chromium binary).

## Rebuild

From the art checkout, with Blender 4.3.2, Pillow, the DejaVu Sans bold font
and the exact glTF dependencies listed in the W1a trio journal:

```sh
S=scripts/blender/showcase-studies
O=/tmp/wildshard-w1b
mkdir -p "$O"
for pair in 015:yard-boss 016:shift-boss 017:surveyor; do
  role=${pair#*:}; id=${pair%:*}
  node "$S/surveyor_pack.mjs" node_modules "$O" "$role" --decode-tracked \
    "public/assets/wildshard-art/wsc-actor-$id-$role.glb" || exit 1
done
WSC_QUEST_MARKERS_ONLY=1 blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python "$S/quest_trio_reimport.py" -- "$O"
python demos/quest-giver-markers/compose.py "$O" /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
cmp "$O/w1b-quest-marker-proof.json" project/layouts/w1b-quest-marker-proof.json
node --test demos/quest-giver-markers/markers.test.mjs
# Optional actual browser capture using a Playwright modules directory and installed Chromium:
# CHROMIUM_PATH=/path/to/chromium node demos/quest-giver-markers/capture.mjs "$O" node_modules
```

The 804 × 1748 base and generated photographs are review products rather
than inputs. The tracked receipt pins actor inputs and actual pixel bounds.

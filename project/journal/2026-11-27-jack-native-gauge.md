# The Broken countdown ring is the biggest tested glow contributor

The earlier body-only comparison left a huge gold ring in the actual Pallet Jack counter. One stock reference counter was executed, then **the same frozen 402 × 874 frame** was rendered eight ways. The gameplay clock, camera, poses and Rook/Jack HP (204/85 here) stayed the same. Across variants we held the body cap at 0.22. Only selected render attributes were modified; gameplay, cooldowns, point lights and the small sparkle at the gauge head were not changed. This is one staged native capture, not an iPhone test.

| Layer change in the same frame | Bright pixels in the fixed left impact region |
| --- | ---: |
| Body cap only (comparison baseline) | 12,003 |
| Hide robot-break and break-ring particles | 11,951 |
| Hide blade-impact particles | 10,739 |
| Hide player counter-ring particles | 12,003 (none live at this instant) |
| Hide all the tagged particles above | 10,737 |
| Hide the Broken countdown gauge ribbon | 6,802 |
| Hide the heavy sword trail ribbon | 9,228 |
| Keep the gauge but shrink it to 58% and dim gold alpha to 65% | 7,974 |

The large circle was the **Broken countdown**, not just the one-shot hit flash. Shrinking it retained the timer shape and dark track and reduced the bright pixel count in this frame by 33.6%. Bright pixels are a repeatable RGB threshold in one fixed image crop, not measured luminance or viewer perception. This does not fix Jack being cropped by the camera. Preserve the gauge semantics; do not remove the timer or turn down every effect. Validate the smaller gauge from open and close angles, with sweep trails and the HUD still readable, before adopting it. The particle isolation does not diagnose point lights or other bloom sources, which stayed on.

Use the pinned local native probe with `gauge` as last mode, then `python demos/mite-yard/jack-warning/gauge-proof.py /tmp/jack-native-...` to produce a numeric receipt. Retain original screenshots only in private scratch. The reference checkout, Fable gameplay, native release and public assets were unchanged.

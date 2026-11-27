# Reframe the counter instead of only widening the lens

Ran one live Rook sword counter against one normal Pallet Jack in the pinned reference build at 402 × 874. The stock charge passed Rook during his forward dodge; Jack was then clipped on the left at the damaging counter. At contact, Jack's posed geometry reached x = −182 px. A +12° vertical field-of-view change alone still reached x = −105 px. A fixed 12° left turn alone pulled Jack back in but clipped Rook's right side. Neither is a good default.

| Real time after damage | Stock out-of-frame Jack vertices | +12° lens only | Tapered turn and lens — both actors outside |
| --- | ---: | ---: | ---: |
| 0 ms | 961 | 287 | 0 |
| 100 ms | 936 | 176 | 0 |
| 200 ms | 320 | 0 | 0 |
| 300 ms | 0 | 0 | 0 |
| 500 ms | 0 | 0 | 0 |

The staged taper used turn / vertical-FOV offsets of +12° / +8° at contact, +8° / +8° at 100 ms, +4° / 0° at 200 ms, +2° / 0° at 300 ms, and stock at 500 ms. It kept both projected meshes inside across these five sampled poses, with a minimum ~17 CSS px horizontal margin. It did not ensure separation from the HUD: the right action controls can still overlap Rook, and the frozen overlays intentionally do not follow the edited lens. Body flash, gold timer, particle treatment, damage, game time, actor poses and physical camera placement were held fixed in the render comparison. Counts mean geometry vertices, not visual area, occlusion, or perception.

Use `native-probe.mjs FABLE_CHECKOUT DEPENDENCY_PROJECT framing` against the pinned build on loopback. It runs a no-god staged level-four dodge and measures posed robot/humanoid draw geometry and head/chest/weapon anchors. The same replay was run twice; the stock counts agreed at all five offsets. No reference image or game asset is checked in.

This is a screen-fit test, not a camera controller to ship. Try anticipation during the counter's existing motion, rather than a snap on impact. Fit both silhouettes to a playable region above/away from the touch buttons. Give manual look and sprint priority, preserve world-relative movement, and check tall and low blockers, left and right passes, and real portrait touch before adopting it. No Fable source, game release or camera settings changed.

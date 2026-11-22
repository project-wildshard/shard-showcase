# 2026-11-22: portrait sword framing

At 1.8 m the old sword hit test landed even at 36° left or right of the
402 × 874 frame. Keep the existing range, timing, forward arc and cover check,
but require the close armor volume to overlap the camera frame at impact.
An inset sphere lets a visible shoulder count even when the center is outside.
Rendering and combat share pitch, close look, dodge roll and the 65° vertical
FOV. Focused tests cover centered, left/right edge, offscreen, landscape and
looking away. This applies to the standalone yard only; enemy and native
combat are unchanged. The visual effect still represents confirmed damage,
not a blade/mesh intersection.

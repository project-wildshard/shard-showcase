# 2026-11-22: East dock court in the Mite yard

Ported the dock-outside-the-lane idea from the E01 dock-court study
to the playable yard. Reused the existing dock and haul crate GLBs.
The 2 m dock stops movement but does not act like tall cover. Three
crates replace the generic east block on its existing footprint.
The central line remains clear for the one-Mite fight.

Nine focused tests pass. In Chrome's Canvas2D fallback I walked in,
woke the Mite, took a bite, killed it and collected one Servo. The
static build is 2,743,005 staged bytes; not a network measurement.
This is a standalone yard, not native layout or mobile performance QA.

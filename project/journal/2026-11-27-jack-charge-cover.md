# Pallet Jack: does the red lane agree with cover?

Use the existing Rook, Pallet Jack, warning and combat loop from the pinned Fable source. The fixture holds Rook still in a level-4 Pallet Docks save and lets Jack pick its own attack. Two independent portrait Chromium replays stage the same spot; one adds a fixed 2.4 × 1.0 × 1.1 m box. No god mode, roll, force-attack, or damage edits.

The high eye line is clear in both. Only the low locked ram ray intersects the fixture. In the open control Rook drops from 204 to 170 HP; with the box he stays at 204. The genuine charge ray hits the fixture, emits the native crash cue and ends the charge early. Recovery still uses the native timing; this is not a new stun. The box is not an installed Pallet Docks prop.

The stock warning still paints red past the box. The frozen, presentation-only prototype draws the same width, color and pulse, ending the visible lane at the measured collision face once aim locks. It does not touch AI, damage, cover collision, or Fable files; the open control is unchanged. The near camera angle can hide some of the shorter strip behind the box. Keep a readable enemy cue and test edge approaches and moving or destructible cover before any integration. Do not treat a shortened strip as a general safety promise.

## Reproduce

From the pinned Fable checkout, run its normal build and serve `dist` on loopback (default port 5174, override with `FABLE_PROBE_PORT`). From this branch run:

```sh
node demos/mite-yard/jack-warning/charge-cover.mjs FABLE_CHECKOUT DEPENDENCY_PROJECT
```

The dependency project needs Playwright and `@sparticuz/chromium`. The script uses disposable browser storage and writes its trace and screenshots to private scratch. The public catalog contains numeric outcomes only. No live game update or iPhone hardware check.

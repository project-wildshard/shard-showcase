# W2a/E1e: six salvage parts for the PACK

The loot plan supplies six names and their actor match. The original PACK
mockup gives a small icon treatment, not equivalent 3D geometry. Two forms
here are source-derived: Servo matches the staged demo's ten-sided body,
flanges, windings, cap and plug recipe; Tine extracts one unmodified tapered
fork shape from the existing Pallet Jack, not the Big Pallet trophy. Blender
recasts coordinates to local bottom-center pivots. No donor GLBs are
replaced or copied whole.

Rotor, Nozzle, Rivet plate and Arc coil are proposals drawn from the
Plumb Drone, Welder Unit, Riveter and Arc Sentry roles and original
E03–E06 references. Rotor has a three-arm read, Nozzle an open bore,
Rivet plate an oblong chassis with four raised studs, and the Arc coil
an open copper horseshoe. They are not recovered actor parts. The
shared GLB has six separately named, selectable objects at their own
physical study scales. The contact sheet normalizes display sizes;
it is not a relative-scale chart.

Each mesh is rendered as a 48 × 48 alpha mask from the same display
orientation as its lit icon. The initial Servo/Nozzle overlap was
too high; the nozzle was lengthened and tilted in the next pass.
Numbers in validation.json compare the displayed silhouettes, not
recognition by users, color contrast, PACK layout or a shipped UI.
There is no drop, recipe, inventory or trade binding.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/salvage_parts.py -- /tmp/w2a-salvage
```

[W2a PACK](../../docs/plans/kitchen-sink-v2/slices/W2a-currency-pack-owned.md)
· [E1e salvage](../../docs/plans/kitchen-sink-v2/slices/E1e-salvage-parts.md)
· [Part table](../../docs/plans/kitchen-sink-v2/loot-economy-mini-plan.md#numbers).

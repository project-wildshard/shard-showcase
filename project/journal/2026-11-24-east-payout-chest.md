# Band 1 East: Scrip payout chest

E1d specifies two Band 1 chests, 15 Scrip each, claimed once. E13
uses two per band. This is a closed art prop, not the West PROP-049
cyan-seal cosmetic cache, and it does not implement the reward.

Round 5's archived placement recipe at ce1cf050b3 positions each
chest 3 m east and 3 m south of its associated piece of cover.
The two x/z centers recovered from that calculation are
(103.2476, -89.0561) and (102.6855, -103.4562). The reimport
keeps those offsets in a translated, flat Blender scene. The
existing haul crate is a pinned visual substitute for cover.
Terrain height, prop facing, and backdrop are staging only.

The blued shell, orange lid and physical SCRIP plaque are an art
proposal fitted to the archived 1.4 × 1.0 × 0.9 m placeholder size.
The plaque does not hard-code the payout, so later bands can reuse
the shell. Both views use the exact reimported texture-free GLB.
Neither the West chest nor the pinned crate changes. No opening
animation, collision, interaction, claim state, or native placement.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/east_payout_chest.py \
  -- /tmp/east-payout-chest
```

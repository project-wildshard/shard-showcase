# W6c · Station 6, there and back

WSC-KIT-002. The original 22.02 m swaying bridge kept all 54 visible
boards and 18 native bodies. Use normal input from the launch deck to
0.8 m onto the tank landing, wait 12 ticks and reverse on the same live
chain. Five starting offsets between −0.32 and +0.32 m. Repeat each
with a 0.75 s pause at midspan on both legs. No midrun teleport, jump,
new art, floor substitute, or collision changes.

- All 20 legs finished grounded, with no unintended stall. Normal
  traversals took 338–341 ticks; pause traversals 383–386.
- Both wide outbound pause trials lost the bridge's floor tag for one
  tick while remaining grounded. Every uninterrupted walk kept the
  tag across the interior. Lowest feet 17.157 m, max lateral 0.347 m,
  conservative remaining edge margin 0.073 m.
- The default center/save test still passes. No claims about client
  motion, chaining all five bridges, or phone performance.

[Replay and review render](../../demos/native-rope-bridge/README.md) ·
[Receipt](../layouts/w6c-station6-round-trips.json).

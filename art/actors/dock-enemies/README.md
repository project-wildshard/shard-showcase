# Wildshard dock enemies, batch 1
Four new robot types: Gate Sentry (biped), Rivet Skitter (quadruped), Beacon Wasp (hover), Ballast Ram (roller). These are original first-pass silhouettes and rigid armatures. Each GLB exports Idle, Move, Turn, Windup, Attack, Recover, Hit, Special and Defeat, with named ground, weak-point and attack sockets.

The registry proposes different behavior and timing for the upcoming yard. It does not mean AI, hitboxes, avoidance, or damage are integrated. There are zero counted variants in this commit. Blender scene and Python are editable and rebuildable. No Fable source or assets.

```sh
blender -b -t 8 --factory-startup --python-exit-code 1 --python scripts/blender/dock-enemies/build.py -- /tmp/dock-enemies
python scripts/blender/dock-enemies/verify.py art/actors/dock-enemies
```

Ballast Ram’s revised B-series chassis has a sloped ballast hood, a recessed warning eye, a steel lower plow and clad traction rollers. The other three GLBs, Ram’s three sockets, nine clips and encounter tuning were retained. See the standalone Forge Yard test receipt for actual browser play.

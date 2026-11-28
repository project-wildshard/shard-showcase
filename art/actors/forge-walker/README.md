# Walker · Forge Warden
Original portable material-only hero for the local Forge Yard. The editable `walker.blend` holds the eighteen articulated joints, NLA motion tracks, workwear, platings, gloves, visor, pack and split coat. `walker.glb` is the game-runtime export, without studio objects. Grip sockets are children of the two actual hand bones, and the root has a zero-offset ground socket.

```sh
mkdir -p /tmp/forge-walker
blender -b -t 8 --factory-startup --python-exit-code 1 --python scripts/blender/forge-walker/build.py -- /tmp/forge-walker
python scripts/blender/forge-walker/verify.py art/actors/forge-walker/walker.glb
```

Nine clips: Idle, Stride, Turn, Dodge, Hit, Defeat, Sweep, Chop and Thrust. Three body attack clips are selected by the equipped weapon's style, timed against that weapon's gameplay cycle, while the weapon separately plays its own exported animation. The actor uses rigid parented panels, not skin deformations, facial rigs or exact geometry-driven hit collision. Restore NLA track mutes before hand export.

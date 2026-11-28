# Walker · Forge Warden
Original portable material-only hero for the local Forge Yard. The editable `walker.blend` holds the eighteen articulated joints, NLA motion tracks, workwear, platings, gloves, visor, pack and split coat. `walker.glb` is the game-runtime export, without studio objects. Grip sockets are children of the two actual hand bones, and the root has a zero-offset ground socket.

```sh
mkdir -p /tmp/forge-walker
blender -b -t 8 --factory-startup --python-exit-code 1 --python scripts/blender/forge-walker/build.py -- /tmp/forge-walker
python scripts/blender/forge-walker/verify.py art/actors/forge-walker/walker.glb
```

Twelve clips: Idle, Stride, Turn, Dodge, Hit, Defeat, Sweep, Chop, Thrust, MaulDrop, SlipfinRip, and NeedleJab. The last three are original signature moves for Rivet Maul, Slipfin, and Rail Needle. The other weapons use the three shared attack poses. Frame 15 is the Blender release pose for each; the browser scrubs the Walker body clip to that pose on the simulation’s release tick. Weapon mechanisms still play their own exported clips separately. The actor uses rigid parented panels, not skin deformations, facial rigs or exact geometry-driven hit collision. Restore NLA track mutes before hand export.

The layered heat-shield pass adds a tapered rear radiator, face guard, and asymmetric shoulder shells while retaining every joint, clip and weapon socket. Runtime export: 8,840 triangles, 646,616 bytes, no textures. Front and rear studio render original editable source; browser proof is under `demos/forge-yard`.

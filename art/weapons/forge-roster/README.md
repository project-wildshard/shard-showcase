# Wildshard Forge Roster · first-pass animated geometry

Eleven new silhouette-authored weapons (WSC-WPN-015 through WSC-WPN-025). With Signal Shear, this makes twelve. Each GLB is isolated at the grip, has grip/tip sockets and a two-bone rigid rig, and carries a Ready clip and an attack in one of three motion families (chop, sweep or thrust). The motion families are shared, not eleven bespoke combat animations. Game equip, collision, balance and damage are not wired in yet.

Read `verification.json` for the exact clip names, triangles, byte counts, and head dimensions. The Blender file is the editable roster board. The Python builder reproduces every mesh, joint and action.

```sh
blender -b -t 8 --factory-startup --python-exit-code 1 --python scripts/blender/forge-roster/build.py -- /tmp/forge-roster
python scripts/blender/forge-roster/verify.py art/weapons/forge-roster
```

# Dock foundry · WSC-ENM-013–016
Four original Forge Yard enemies. The small combined Blender scene contains the editable material-only designs, parented rigs and motion tracks. The per-actor GLBs retain nine named clips and ground, weak-point and attack sockets. To regenerate:

```sh
mkdir -p /tmp/dock-foundry
blender -b -t 8 --factory-startup --python-exit-code 1 --python scripts/blender/dock-foundry/build.py -- /tmp/dock-foundry
python scripts/blender/dock-enemies/verify.py art/actors/dock-foundry foundry
```

The lineup uses display offsets and muted NLA clips. Reset each actor's X offset, unmute clips, and restore unprefixed socket names if exporting one manually. No generated diffuse textures, caches, or intermediate PNGs are needed for the game or to resume editing.

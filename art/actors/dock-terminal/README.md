# Dock terminal · WSC-ENM-017–020
The compact Blender source holds four editable models, their rigid rigs and nine named clips per actor. The runtime GLBs preserve ground, weak-point, and attack sockets.

```sh
mkdir -p /tmp/dock-terminal
blender -b -t 8 --factory-startup --python-exit-code 1 --python scripts/blender/dock-terminal/build.py -- /tmp/dock-terminal
python scripts/blender/dock-enemies/verify.py art/actors/dock-terminal terminal
```

For a hand export, neutralise the display X offset, unmute the model's NLA tracks, and retain the unprefixed socket names. This standalone material-only group needs no textures or simulation caches.

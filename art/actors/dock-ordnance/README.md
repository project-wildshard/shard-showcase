# Dock ordnance · WSC-ENM-009–012
Four original combat prototype rigs. Edit the compact authored `dock-ordnance.blend` (all four rigs and their NLA tracks), or regenerate model source, runtime GLBs and the lineup using `scripts/blender/dock-ordnance/build.py`. The generator is deterministic in scene construction. The material-only GLBs use rigid bone parenting, with nine clips and ground, weak-point and attack sockets on every actor.

```sh
mkdir -p /tmp/dock-ordnance
blender -b -t 8 --factory-startup --python-exit-code 1 --python scripts/blender/dock-ordnance/build.py -- /tmp/dock-ordnance
python scripts/blender/dock-enemies/verify.py art/actors/dock-ordnance ordnance
```

The lineup places actors at display offsets with NLA tracks muted. Neutralise each actor's object X offset and unmute its tracks before a manual individual export. Keep exact unprefixed socket names in individual GLBs. No bake caches, textures, or intermediate PNGs are required.

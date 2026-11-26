# East Threshold direction boards (W0a / WSC-SCENE-004)

The overhead East Gate nameplate identifies the masonry gate. These small
eye-level boards serve a different purpose at the industrial seam: ochre
points to the East Yard charge lanes, blue marks the return to Brasswick.
They share a 1.56 m wide iron/enamel panel, brass pins and an oak upright.
The arrow shape and copy distinguish destinations without relying on color.
Both GLBs have independent ground-centered origins; glTF +Z faces the reader.
Letters remain editable in the Blender generator and need no external font.

Rebuild with Blender 4.3:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/east-threshold-direction/build.py -- /tmp/east-direction
```

Append `--no-render` to emit just the GLBs and proof. Shapes, fonts, materials,
camera and fit each live in `build.py`. The proof imports both outputs and
hash-checks the nine existing W0a donors. Each placement clears 135 sampled
eye-to-panel rays against the staged masonry and industrial geometry,
preserves the 100 central walk-corridor sample rays, and does not intersect
the gate meshes. The anchors and yaw in the receipt are for that study only.
These are optional props, not a game install, collision spec, phone playtest
or a change to Fable's build. Keep the approach clear on any receiver map.

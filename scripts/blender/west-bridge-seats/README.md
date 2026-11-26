# W6c Climb Yard rope terminals

Two small offline art overlays for the three retained Climb Yard spans
A→B, B→C and C→Rock. Their original boards, ropes, support geometry and
placements are unchanged. Reuse the blued-iron and bronze post sleeve
on each round timber post. Center the second part on the original first
rope segment; it rotates with the authored chord at that end. This
makes the rope appear to terminate at a distinct piece of hardware
rather than disappearing directly into the post.

The sleeve origin is the collar center with its open bore vertical.
The ferrule origin is its center; its open bore runs along local +X.
The placement file uses Blender XYZ, +Z up; the conversion to Three
XYZ is (X,Z,−Y), with the yaw and unit axis interpreted in Blender.
Both assets are independently exported and reimported. A ray samples
the post and the rope at all 12 terminals; every reimported point is
outside the vertical tread-edge plane of its span. This is an
art-placement check, not structural validation, a player sweep or
collision. Station 6 and all other yard spans remain untouched. No
moving rope, server, controls or live world are changed.

Build from the art root:

```sh
out=/tmp/w6c-seat
blender -b -t 6 --python-exit-code 1 --python scripts/blender/west-climb-rock/build.py -- --output "$out/yard"
blender -b -t 6 "$out/yard/climb-rock-editable.blend" --python-exit-code 1 \
  --python scripts/blender/west-bridge-seats/build.py -- "$out/yard" "$out"
cmp "$out/fit.json" project/layouts/w6c-bridge-terminals-fit.json
```

Append `--models-only` to omit the two context renders. The script
requires the donor scene's reported semantic parity before placing
the inserts. The original yard scene is never saved or re-exported
by this script. The .blend and any scratch traces stay out of Git.

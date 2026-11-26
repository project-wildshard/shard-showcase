# E5b / WSC-MODULE-024: far yard floodlight

Optional lighter stand-in for the 8.9 m eight-lens yard floodlight. Import at the same origin and rotation as the original. The build welds only coincident vertices, dissolves low-angle flats within material boundaries, and reduces detail without turning the steel lattice into an opaque column. It retains all eight material slots including the reflector and lens finishes. Use the original close up.

| | Original | Far |
|---|---:|---:|
| Triangles | 18,028 | 5,412 |
| GLB bytes | 1,444,832 | 819,712 |

Reimport checks: overall bounding faces within 5 mm, height/base Y unchanged in glTF, lens-region bounding faces within 1 mm. Twelve sampled 132 × 200 silhouettes around the tower overlap by 97.38–99.10% (intersection over union). The two 804 × 1748 pictures swap only the model using the existing E5b shadow-study placement and a matched eye-height camera around 39 m away. Yard props and preview lighting are context, not part of the download.

Build from repository root in Blender 4.3.2. Use one thread for the reduction/export step; parallel normal evaluation can change emitted bytes.
```sh
D=scripts/blender/yard-floodlight-far
OUT=/tmp/wsc-tower
blender -b -t 1 --factory-startup --python-exit-code 1 --python "$D/build.py" -- "$OUT"
blender -b -t 6 --factory-startup --python-exit-code 1 --python "$D/render.py" -- "$OUT"
```
Two fresh single-thread builds and proofs match byte for byte. See `project/layouts/e5b-floodlight-far-proof.json`. No change to original art, collision, lighting, game placement, or automatic LOD.

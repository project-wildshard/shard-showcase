# W0b town gate nameplates

W0b asks for six named town gates. The archived Round 5 GATES array names
East, Stable, Movers, West, Park, and Range and gives their destinations.
The M07 East Gate mockup establishes a warm light board with dark letters
above the masonry crossing. West-side blockouts also show names on the
gate beams, but do not establish a final kit. The finish, typography and
pictograms here are new art choices, not recovered production geometry.

One 3.32 × 0.63 m bronze/enamel frame and six interchangeable faces are
packed as seven meshes in a single GLB. Each face carries an exact gate
name and an optional route cue. The GLB scene displays the six signs as a
swatch, with separate named parent nodes. To place a sign, take its parent
and reset the swatch translation; the local origin is centered on the
rear mounting plane. Local face normal is −Y in Blender (glTF +Z). Keep
the shared frame and that sign's face. Duplicate the parent as needed
without copying the frame geometry. Editable letters use Blender's built-in
font; no external typeface or texture assets are required.

The East Gate sign is staged on the pinned W0a lintel and towers, not the
separate industrial seam. The existing geometry is unchanged. The script
samples the lintel behind the sign and sizes four context-only stand-offs;
the brackets, wall swatch, and gatehouse are not in the GLB. The narrow
edges and other five gate hosts are not fit-tested. This is a static art
kit, not native placement, navigation, collision, or a runtime test.

Rebuild the model, validation JSON and two previews:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/town_gate_nameplates.py -- /tmp/w0b-gate-signs
```

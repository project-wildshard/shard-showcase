# Give East 01 a freight bay

The E01 reference puts the Crate Mite in a working loading court. The old rear fence was uniform behind the main orange gantry. Three center bays now give way to a closed 3.58 m steel freight shutter, with a recessed slat assembly, worn amber posts, a layered fascia, and one amber service control. The YARD 01 plaque stays tied to the beam over the door. The door isn't an exit; traversal, collision and encounter timings are unchanged.

`demos/mite-yard/yard-loading-bay.mjs` is the editable geometry recipe. The existing dock, gantry and crate assets are untouched. The bay is 1,144 triangles before subtracting the fence it replaces. Deep, subdivided backing faces prevent the software painter from covering the shutter with diagonally sorted triangles at the tested angles. There are no new texture downloads.

Verified the entry and cyan warning in 402 × 874 Chrome, then replayed the touch encounter to a 77 HP clear with the Servo salvaged. `node --test demos/mite-yard/*.test.mjs`: 28 green. This is the standalone browser yard, not a native client or a device benchmark.

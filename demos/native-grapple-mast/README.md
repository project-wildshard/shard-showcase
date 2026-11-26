# W7a hook 4: walk the tank roof, then catch the original mast

From the rim hook landing, the 28 m mast is in range but the view is not consistently clear. One matched edge start is blocked when it aims immediately on arrival. In the verified route, the stock motor walks about 1.63–1.70 m inboard on the unchanged tank roof before aiming. No steps are airborne and no pose resets occur. The original mast has no usable landing near the ring. Keep its position and add a freestanding 3.4 × 2.8 m deck, top Y=25.60 m, at Three (-202.6,0,-63.55), identity rotation. The model is an exposed calibration deck, not final guarded art.

All 25 ground starts land four consecutive hops in one SimHost. The fourth reach is 26.83 m (rounded), contact takes 147–149 ticks at 60 Hz, and the settled capsule has at least 0.319 m of spare distance to the deck edge. With the receiver removed, the same grounded reposition leaves the fourth ring visible but unable to lock. Exact W08 mast triangles and reimported receiver geometry participate. No rope, mast, tank or engine change.

Both surveyed fifth references are inside 38 m from the new deck: the archive tower centre is 36.20–36.32 m; the W08 visible proxy is 37.32–37.45 m. This is **distance only**, not line-of-sight, lock, collision, or fifth-hop proof. The benchmark is not an installed course, timer or iPhone playtest.

The standalone receiver is 88,124 bytes / 1,548 triangles, no textures. The ground-centred GLB contains the deck and support frame. The floor collider in the test is exactly the measured box; the rest is reimported triangles. Gold dots in the render show actual roof steps; ribbons are overlaid observed hops.

## Rebuild
Complete the [three-hop rebuild](../native-grapple-tank/README.md) through generation of its hulls in directory `T`. With `B` pointing at the same rebuilt W08 blend:

```sh
D=demos/native-grapple-mast
blender -b "$B" -t 4 --python-exit-code 1 --python "$D/extract.py" -- "$T/mast.json"
blender -b "$B" -t 4 --python-exit-code 1 --python "$D/model.py" -- "$T"
node --experimental-transform-types demos/native-grapple-two/sample.mjs "$T" "$T/native-four.json" --mast
blender -b "$B" -t 12 --python-exit-code 1 --python "$D/model.py" -- "$T" "$T/native-four.json"
```

Compact readback, including offset grid and controls: [w7a-mast-hop-proof.json](../../project/layouts/w7a-mast-hop-proof.json).

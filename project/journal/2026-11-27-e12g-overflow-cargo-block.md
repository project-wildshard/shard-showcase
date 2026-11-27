# E12g · Overflow cargo block

The phase-three block now has a separate moving-prop mesh: worn oxide
freight doors in a blue-black frame, with low amber end fittings. The
plan gives a 4 × 8 m footprint. This proposal uses 8 m across the lane,
4 m along it and a 3.2 m height. The geometric center is the shared
roll pivot; in Blender the X axis is the axle and +Y is forward. In
glTF the same directions are +X and −Z. The asset is static.

One 138,200-byte GLB contains 2,124 triangles in six material primitives,
without textures or animation. Reimport measured all three dimensions.
From a center radius of 14 to 44 m, each of the four existing 10 m lanes
leaves 1 m to either side. For any roll angle the horizontally swept
radius about the axle is bounded by 2.562 m. The resulting band clears
the four cover groups by at least 13.867 m on a separating axis and
stays at least 5.267 m inside the nominal 52 m rim. All 5,236 downward
samples hit the existing floor, with at most 75 mm of visual relief.

The tilted Blender pose is staged. This does not implement the mover,
dynamic collision, telegraph, timing, hits, knockback or a playable boss.

```sh
blender -b -t 8 --factory-startup --python-exit-code 1 \
  --python scripts/blender/titan-overflow-block/build.py -- /tmp/overflow
cmp /tmp/overflow/e12g-overflow-cargo-block.glb public/assets/wildshard-art/e12g-overflow-cargo-block.glb
cmp /tmp/overflow/e12g-overflow-cargo-block-proof.json project/layouts/e12g-overflow-cargo-block-proof.json
```

Append `--proof-only` to skip staged render output.

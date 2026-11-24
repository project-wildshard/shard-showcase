# W11a: light the obelisk without changing its stone

W11a asks for the landmark to read at night. Keep the original
22 m shaft, clock and basin unchanged, and stage four copies of one
optional bronze fixture with hooded amber lenses. The west-facing
dial proposal uses the known 14.6 m art mounting height; its position
is sampled on the actual shaft. The plaza layout is a visual stage.

The fixture-only GLB is 31,676 bytes and 388 triangles. It reimports
without cameras or lights. All four feet are at grade; every fixture
vertex lies at least 0.535 m farther from the center than the
outermost basin vertex. Four preview spots use test-only colors and
power. Their center rays reach existing stone at roughly 8.46 or
12.51 m. The near detail shows the hood, not a basin replacement.

The first two matching images retain exactly the same geometry,
camera, and color settings. Only the four preview spots and
the stage's copied fixture lens emission change. The original
model and lights are not changed in game. No W11a day clock,
runtime emitter rows, photo-mode, collision or night-state test.

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/showcase-studies/obelisk_lighting.py -- /tmp/obelisk-night
```

[W11a plan](../../docs/plans/kitchen-sink-v2/slices/W11a-day-night-weather.md)
· [Original W01 plaza art](https://github.com/Raynos/project-wildshard-singleplayer/blob/8c56c4616b2bc26dbd9da03945dfd340e875ecce/art/showcase-template/round-11-remaster/west/w01.jpg).

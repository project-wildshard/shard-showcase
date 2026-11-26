# W7a hook 3: tank rim to the original roof

The archived plan fixes the tank centre at Three (-206,18,-104), with a radius of 16 m. It does not give an exact ring offset. A ring at the centre does not work from the second perch: it is 49.41 m from the player's eye (default reach 38 m) and the near wall blocks sight. Fit an optional raised cantilever to the northeast rim instead. The ring centre is the model origin, Three (-193.2,21.35,-91.2) at identity rotation. The original shell, roof, guard and bridge are unchanged. The raised ring keeps the pull clear of the bracket and original fence; a 20.5 m ring on the lower candidate bracket locked but did not settle on the roof.

The pinned native grapple and actual Rapier player motor complete all **three** hops without resetting the player. The third locks at 32.49–32.71 m, touches down in 159–160 ticks from fire, and leaves at least 0.54 m between the settled capsule and a conservative roof-edge radius. All 25 start offsets use the exact W08 geometry (18,070 triangles in the tank extraction envelope), first and second landing fixtures and reimported saddle triangles. A named lock matches the centred camera replay, and removing just the rendered saddle while keeping the candidate anchor does not change arrival times or positions. The failed centre anchor control keeps the original guard and roof. The next mast lies 27.06 m from the centre trial's final eye; that is a distance check, not proof of a fourth hop.

The optional GLB is 51,952 bytes, 1,160 triangles, four material primitives, no textures. Path ribbons are overlays generated from actual simulation positions, not part of the model. This is a headless assembly proof only: no published gameplay, course timer, fourth/fifth hop, or phone controls.

From the repository root, build the corridor, first perch and second tower in a common output directory as described in [the two-hop proof](../native-grapple-two/README.md). With that directory set as `T` and its W08 scene as `B`:

```sh
D=demos/native-grapple-tank
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/extract.py" -- "$T/tank.json"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/model.py" -- "$T"
node --experimental-transform-types demos/native-grapple-two/sample.mjs "$T" "$T/native-three.json" --tank
blender -b "$B" -t 10 --python-exit-code 1 --python "$D/model.py" -- "$T" "$T/native-three.json"
```

Small proof: [w7a-tank-rim-proof.json](../../project/layouts/w7a-tank-rim-proof.json). Generate full motion traces with the commands above.

# WSC-PROP-008: yard barrier

First model for the existing generic yard-barrier catalogue row. The
provisional four-view sheet suggests straight charcoal panels, orange
end caps and front gussets, a top rail and two dark feet. It does not
establish exact reuse from W06 or E02. This is not the curved segmented
WSC-PROP-067, the orange movable WSC-PROP-066 or the E07 pit liner.

The reimport is 2.56 m wide, 0.47 m deep and 0.95 m tall; it uses a
centered ground-level pivot. Raw GLB is 61,236 B under a 65,536 B
target, 1,108 triangles, four material primitives and no textures.
Five horizontal sampled rays hit the mid-height visible mesh and three
at the lower center cleared the footprint between the feet. No collider,
physics behavior, cover or exact historic scene placement is shipped.

Run from the repository root with Blender 4.3.2:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
 --python scripts/blender/showcase-studies/yard_barrier.py -- /tmp/yard-barrier
```

The local script recreates the model, visual geometry checks, measurement
JSON and the two-sided studio render; no external donors or large source
files are necessary.

# E5b: container-yard shadow pools

The E5b plan asks for readable shadow pools on a phone even without
dynamic shadow maps. This is an art-only A/B comparison, not stealth
behavior or a phone performance measurement. The same Blender camera,
lighting and scene are used with decals enabled/disabled; donor objects
are set not to cast shadows into the comparison. Soft fill, slab art and
layout are studio proposals, not a new authored level.

Five donor GLBs reimport unchanged: shipping container (PROP-058),
orange cover (PROP-066), fence bay (MODULE-023), eight-lens floodlight
(MODULE-024), and Keycard shed (PROP-065). They were already present, so no
replacement models are made. The placement manifest records the source
hashes, actual dimensions, reuse transforms, and five pool placements.
The props from other East frames are used for context, not claims about
where they belong in the final E5b layout.

The only new GLB is `wsc-kit-006-shadow-pool-decal.glb`, a compact
6 × 3.1 m directional vertex-alpha mesh. Its Y-up floor datum sits about
8 mm above a plane, fades to transparent on its boundaries, and uses no
textures. The drawn shadow extends from local Blender +Y (glTF −Z).
Repurpose it at different scales rather than duplicate its vertices.
It is alpha-blended, not a gameplay trigger or native shading pass.
The dark shapes do not govern hidden state. Mobile overdraw, height
alignment, placement, collision, patrol sight, alarm and pickup are not
validated.

Rebuild from repository root with Blender 4.3.2:

```sh
blender -b -t 6 --factory-startup --python-exit-code 1 \
 --python scripts/blender/showcase-studies/east_shadow_pools.py -- /tmp/east-shadow
```

That rebuilds/reimports the decal, renders both states, and writes the
asset and placement report. All props remain separate reusable donors;
the composed scene is not stored as a duplicate GLB or .blend.

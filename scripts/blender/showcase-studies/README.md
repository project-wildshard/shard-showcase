# Showcase asset sources

The Python files are the editable source of truth. Blender 4.3.2 rebuilds the
five exact tracked static GLBs without textures, a prior checkout, or a .blend.
Run from the repo root:

```sh
out="$(mktemp -d)"
for part in crate_mite pallet_jack trophy_mounts verge_kit; do
  blender -b --python-exit-code 1 \
    --python "scripts/blender/showcase-studies/$part.py" -- "$out"
done
for asset in "$out"/*.glb; do
  cmp "$asset" "public/assets/wildshard-art/${asset##*/}" || exit 1
done
```

Edit the recipe, rebuild the renamed or existing canonical asset, validate it,
then commit the source and final export together. The trophy mounts share one
mesh across 12 authored placements; the verge contains two reusable meshes.
These robot exports are static studies, not runtime enemies or rigs.

Keep only canonical sources, minimal required dependencies and current exports
in Git. Scratch scenes, Blender autosaves, caches, local fixture packages,
unneeded interim GLBs and report renders are not branch dependencies. Delete
superseded branch outputs only once the verified replacement is present. Do not
rewrite history for cleanup. Preserve a native source privately when a compact
recipe can't yet reconstruct it.

## Crate Mite rig checkpoint

Build the separate skinned actor with
`blender -b --python-exit-code 1 --python scripts/blender/showcase-studies/mite_rig.py -- "$out"`.
The script derives the rig from the canonical phone-budget Mite source. It
produces a standalone rig GLB and an editable .blend in the output directory.
The .blend is reproducible and is not versioned. With the repository's Three
dependency installed, run
`node scripts/blender/showcase-studies/check_mite_rig.mjs "$out/wsc-actor-001-crate-mite-rig.glb"`.
The GLB has eleven clips, including two named attacks and sleep/wake. Actor
movement, hit timing, clip selection, collision and spawn state are runtime
responsibilities; the rig checkpoint alone does not implement those.

The 1.3 s death clip scatters the lid and four legs while the chassis
settles. The recipe computes final ground contact from the rigid mesh,
not joint heights. It keeps the same mesh, weights, seven joints and clip
IDs. The loader test checks the separated lid, debris width, six grounded
modules and eye shutoff on the exported animation.

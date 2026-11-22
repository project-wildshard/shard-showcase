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

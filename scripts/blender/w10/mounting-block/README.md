# WSC-PLAN-008 mounting block: art-only WIP

Fills the existing plan-only mounting-block row, not a new catalog ID.
Existing sandstone/industrial steps and pallets are not a compact three-rise
mounting platform. No gameplay, rider, collision or safety qualification.

Reproduce from repository root with Blender (tested with 4.3.2):
`blender -b --python scripts/blender/w10/mounting-block/build.py -- /absolute/scratch/output`
then
`python3 scripts/blender/w10/mounting-block/validate_glb.py /absolute/scratch/output`.

Generator creates GLB, editable native, validation and two clean-reimport
studio renders outside tracked source. Only the screened GLB is committed.
5264 triangles, 263288 bytes, Blender Z-up bounds 0.86 x 1.16 x 0.541 m.
Stored receipts describe the screened export. Regeneration may differ in
export metadata; compare geometry, counts, bounds and renders, not only bytes.

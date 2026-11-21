# West linked precinct r02: source-only WIP scene recipe

Art-only reconstruction of the reviewed r02 scene. Not a gameplay, collision, horse-fit, performance or final-quality acceptance. No assembled GLB, native .blend, render, downloaded package or duplicate shared prop is tracked here.

## Rebuild

Requires Blender 4.3.2 with bundled glTF exporter/importer and built-in Bfont; no Python third-party dependencies, downloads or external private inputs. From repository root:

```sh
blender -b -t 6 --python scripts/blender/west-scene-r02/build.py -- --output /tmp/west-r02
```

Add `--render` for the reviewed camera set (including1.75 m player-eye and2.6 m mounted arrival). Output must be outside this checkout. Generated GLBs/natives/QA go there. The driver checks SHA256 of all 10 tracked asset dependencies before creating files or changing the Blender scene, creates the unique stable architecture, assembles the baseline, applies r02 routes/frontage, roundtrips the final GLB and validates it.

`dependencies.json` pins assets at art parent d22027d1b0baa5172c6fc056ecfa5435d6958582. If a shared input changes, the build stops: review/re-render deliberately before updating its hash. Do not delete the guard to make an unrelated asset revision pass.

## Files and ownership

- stable.py: unique procedural stable/portal source, inferred architecture, exact source lot and gate anchor. No new catalogue ID implied.
- assemble.py: scene-owned ground/walls/track and transforms for shared catalogue assets; no source-model rescaling.
- finish.py: proxy replacement, source-aligned streets, inferred apron/curbs/planting and timer mounting correction.
- views.py: full overview and historical mounted camera; other context/player cameras are in finish.py.
- validate.py / semantic_glb.py: GLB integrity and an order-independent fingerprint of positions, normals, UVs, triangle winding/topology, material contents and instance transforms against the reviewed r02 output. Does not confuse arbitrary exporter ordering with a changed scene. No pixels are claimed freshly rendered unless --render was used.

Reproducibility is scene-semantic, not byte-for-byte GLB identity: Blender may reorder equivalent triangles/buffer records. The validator requires the same 1291 primitive instances and canonical fingerprint 7428d16f297dd3399d8f9735e1123168422af3722362d18d949097a999d0067b. Output hash is recorded separately.

## Provenance and constraints

Current project plans: docs/plans/kitchen-sink-v2/map-layout-mini-plan.md and slices/W10a-loaner-horse-paddock.md, W10b-riding-course.md. Layout source: Raynos/project-wildshard-singleplayer, ce1cf050b3, art/showcase-template/round-5-blockout/layout.js; current plan says round5 left West unchanged. Source anchors are frozen numerically in assemble.py; no network lookup is needed to build.

Map metres(x,y,z) become Blender(x,-z,y). Stable Gate (-36,-60); stable lot x[-28,-10],z[-56,-38]; paddock 48×60m; oval centre(-122,-186),halfstraight60m,radius38m,track 12m,outer 208×88m. Gate final clear opening 12m. North back alley x[-127,-42],z[-36,-32] and crosslane x[-99,-91] are plan-backed. Chute width, exact ring/jump placements, stable architectural form, gardens, footpaths and curbs remain inferred WIP. D24 riding remains paddock/oval only, no horse introduced.

Measured footprints remain intact. Dark inner gate timber, sparse landscape, source wall obscuring north stable arcade,3.12m ring diameter versus horse fit, and4.1m jump rail versus12m track are known unresolved art/gameplay questions. This is a useful linked scene checkpoint, not a complete epic town.

"""Fit the existing Gold GLB to the existing cave. Pass the cave donor .blend
and run with '-- /absolute/output' as for rock_squeeze_cave.py.
"""
import hashlib
import json
import os
from pathlib import Path
import runpy

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

source = Path(__file__).resolve().parent
os.environ["WILDSHARD_CAVE_SKIP_RENDER"] = "1"
state = runpy.run_path(str(source / "rock_squeeze_cave.py"), run_name="cave_recipe")
scene, out = state["scene"], state["out"]
gold_path = source.parents[2] / "public/assets/wildshard-art/w9b-gold-find-cube.glb"
old = (-200, -5.5, 44)
candidate = (-201.8, -5.5, 40)


def import_gold(name, world):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(gold_path))
    objects = [o for o in bpy.data.objects if o not in before]
    for o in objects:
        if o.parent not in objects:
            o.location += Vector((world[0], -world[2], world[1]))
        o.name = name + " | " + o.name
    bpy.context.view_layer.update()
    return objects


def geometry(objects):
    verts, faces = [], []
    for o in objects:
        if o.type != "MESH":
            continue
        offset = len(verts)
        verts.extend(o.matrix_world @ v.co for v in o.data.vertices)
        o.data.calc_loop_triangles()
        faces.extend(tuple(offset + i for i in f.vertices) for f in o.data.loop_triangles)
    return verts, faces


def measure(objects):
    verts, faces = geometry(objects)
    low, high = ([f(v[i] for v in verts) for i in range(3)] for f in (min, max))
    pickup = BVHTree.FromPolygons(verts, faces, all_triangles=True)
    floor_hits, roof_hits = [], []
    for fx in (.03, .25, .5, .75, .97):
        for fy in (.03, .25, .5, .75, .97):
            x, y = [lo + (hi - lo) * f for lo, hi, f in zip(low[:2], high[:2], (fx, fy), strict=True)]
            p = Vector((x, y, -5.7))
            floor, _, _, _ = state["full"].ray_cast(p, Vector((0, 0, -1)), 2)
            roof, _, _, _ = state["full"].ray_cast(p, Vector((0, 0, 1)), 8)
            if floor is not None:
                floor_hits.append(low[2] - floor.z)
            if roof is not None:
                roof_hits.append(roof.z - high[2])
    return {
        "liner_triangle_pairs": len(state["full"].overlap(pickup)),
        "dressing_triangle_pairs": len(dressing.overlap(pickup)),
        "bounds_blender_m": [[round(i, 4) for i in a] for a in (low, high)],
        "minimum_base_to_floor_m": round(min(floor_hits), 4),
        "minimum_top_to_liner_above_m": round(min(roof_hits), 4),
        "footprint_samples_floor_roof": [len(floor_hits), len(roof_hits)],
        "nearest_edge_to_centerline_m": round(max(0, low[0] + 200, -200 - high[0]), 4),
    }


dressing = BVHTree.FromPolygons(*geometry([o for o in scene.objects
    if o.name.startswith(("Loose shale", "Quartz fleck"))]), all_triangles=True)
archive_objects = import_gold("Archived pose", old)
proposed_objects = import_gold("Chamber pose", candidate)
archived = measure(archive_objects)
proposed = measure(proposed_objects)
assert archived["liner_triangle_pairs"] > 0
assert archived["minimum_top_to_liner_above_m"] < -.37
assert proposed["liner_triangle_pairs"] == proposed["dressing_triangle_pairs"] == 0
assert proposed["minimum_top_to_liner_above_m"] > 2
assert proposed["nearest_edge_to_centerline_m"] >= 1.29
assert proposed["footprint_samples_floor_roof"] == [25, 25]
assert all(abs(m["minimum_base_to_floor_m"] - .5) < .03 for m in (archived, proposed)), (archived, proposed)
receipt = {
    "readiness": "static placement study only; no pickup relocation in game, collision, light timing or player test",
    "archive_reference": "Raynos/project-wildshard-singleplayer@ce1cf050b3:art/showcase-template/round-5-blockout/layout.js#L300",
    "model_sha256": hashlib.sha256(gold_path.read_bytes()).hexdigest(),
    "proof_method": "exact GLB triangles vs generated liner and dressing BVHs; 25 footprint floor and overhead ray samples",
    "archived": {"world_base_xyz_m": old, **archived},
    "proposed": {"world_base_xyz_m": candidate, **proposed},
}
(out / "w9a-squeeze-cave-gold-fit.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt))
if os.getenv("WILDSHARD_VALIDATE_ONLY") != "1":
    camera, data = state["camera"], state["data"]
    world, liner = state["world"], state["liners"][1]
    crag, bench = state["crag"], state["bench"]
    bounce, edge, area = state["cave_bounce"], state["edge"], state["area"]
    accent = area("Preview-only wall bounce", (-200.15, -39.15, -2.2),
                  (-201.8, -40, -4.95), 110, 1.55, (.92, .81, .64))
    separation = area("Section fill", (-190, -44, 1.7),
                      (-201, -42, -5), 1850, 6, (.82, .9, 1))
    scene.cycles.samples = 72
    scene.cycles.use_denoising = False
    for name, p, target, res, lens in [
        ("chamber", (-199.30, -35.7, -4.37), (-200.72, -41.3, -4.86), (1320, 910), 25),
        ("section", (-180, -42, -.32), (-201, -42, -4.30), (1360, 790), 50),
    ]:
        section = name == "section"
        liner.hide_render = section
        crag.hide_render = True
        for o in bench + state["cut_lights"]:
            o.hide_render = True
        separation.hide_render = not section
        for o in archive_objects:
            o.hide_render = not section
        world.node_tree.nodes["Background"].inputs[1].default_value = .29 if section else .055
        camera.location = p
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
        data.type = "ORTHO" if section else "PERSP"
        data.ortho_scale = 12.6
        data.lens = lens
        scene.render.resolution_x, scene.render.resolution_y = res
        scene.render.filepath = str(out / ("nov24-squeeze-gold-" + name + ".jpg"))
        bpy.ops.render.render(write_still=True)

"""Extract and validate one reusable D7 wall from the tracked-only Hover Park build."""
import argparse
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

p = argparse.ArgumentParser()
p.add_argument("--park-build", required=True, type=Path)
p.add_argument("--output", required=True, type=Path)
args = p.parse_args(sys.argv[sys.argv.index("--") + 1:])
out = args.output.absolute()
out.mkdir(parents=True, exist_ok=True)
src = args.park_build / "hover-park-editable.blend"
assert src.is_file() and (args.park_build / "parity.json").is_file(), "Run west-hover/build.py first."
bpy.ops.wm.open_mainfile(filepath=str(src))


def verts(o):
    return [o.matrix_world @ v.co for v in o.data.vertices]


def donor(suffix):
    o, = [o for o in bpy.context.scene.objects if o.type == "MESH"
          and o.name == f"HOVER | {suffix}"]
    return o


east, west = [donor(f"launch wall {side} 45m") for side in ("east", "west")]
center = donor("launch channel flat center")
sources = [verts(east), verts(west)]
east_pos, west_pos = [Vector((x, -142.5, 0)) for x in (-216, -224)]
center_vs = verts(center)
assert min(v.x for v in center_vs) == -224 and max(v.x for v in center_vs) == -216

# Pull the exact east geometry into a ground-level toe-center coordinate frame.
data = east.data.copy()
data.name = "D7 profile and coping"
data.transform(Matrix.Translation(-east_pos) @ east.matrix_world)
copy = bpy.data.objects.new("D7_Launch_Wall_45m", data)
bpy.context.collection.objects.link(copy)
bpy.ops.object.select_all(action="DESELECT")
copy.select_set(True)
bpy.context.view_layer.objects.active = copy
target = out / "wsc-kit-003-d7-launch-wall.glb"
bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB", use_selection=True,
                          export_animations=False, export_texcoords=False)

for o in tuple(bpy.context.scene.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(target))
wall, = [o for o in bpy.context.scene.objects if o.type == "MESH"]
assert wall.location.length < 1e-7
local = verts(wall)
bounds = [[min(v[i] for v in local) for i in range(3)], [max(v[i] for v in local) for i in range(3)]]
assert math.isclose(bounds[1][1] - bounds[0][1], 45, abs_tol=.001)
assert math.isclose(bounds[0][0], 0, abs_tol=.001)
assert math.isclose(bounds[0][2], 0, abs_tol=.001)
assert 4.5 < bounds[1][2] < 4.56
assert 9 < bounds[1][0] < 9.06

# Test both placements against the already verified scene, in both nearest-neighbour
# directions because glTF splits vertices at hard material and normal seams.
def gap(a, b):
    tree = KDTree(len(b))
    for i, v in enumerate(b):
        tree.insert(v, i)
    tree.balance()
    return max(tree.find(v)[2] for v in a)


def bvh(o):
    return BVHTree.FromPolygons(verts(o), [tuple(f.vertices) for f in o.data.polygons])


clone = bpy.data.objects.new("D7_Launch_Wall_45m_Reuse", wall.data)
bpy.context.collection.objects.link(clone)
wall.location = east_pos
clone.location = west_pos
clone.rotation_euler.z = math.pi
bpy.context.view_layer.update()
errors, gradients = [], []
for ob, source, orig, direction in zip((wall, clone), sources, (east_pos, west_pos), (1, -1)):
    v = verts(ob)
    errors.append(max(gap(v, source), gap(source, v)))
    tree = bvh(ob)
    heights = []
    for i in range(89):
        x = orig.x + direction * (.05 + i*.10)
        point, *_ = tree.ray_cast(Vector((x, orig.y+3.5, 5)), Vector((0,0,-1)), 5.01)
        assert point is not None
        heights.append(point.z)
    assert heights[-1] > 4.28 and heights[0] < .01
    gradients.append(max((b-a)/.1 for a,b in zip(heights, heights[1:])))
assert max(errors) < .00015, errors
assert max(gradients) <= 1.0005, gradients
wall.data.calc_loop_triangles()
report = dict(asset=target.name, model_bytes=target.stat().st_size, triangles=len(wall.data.loop_triangles),
              bounds_blender_m=bounds, placement_error_m=errors, max_gradients=gradients,
              design_crest_m=4.5, span_m=45, run_m=9, separate_center_m=8,
              scope="Static source parity only. No movement, collision, or rideability.")
(out/"launch-wall-qa.json").write_text(json.dumps(report, indent=2)+"\n")
print(report)

if os.getenv("WSC_D7_RENDER") == "1":
    wall.location -= Vector((-220,-142.5,0))
    clone.location -= Vector((-220,-142.5,0))
    def box(name, position, size, color):
        bpy.ops.mesh.primitive_cube_add(location=position, size=1)
        o=bpy.context.object;o.name=name;o.dimensions=size
        m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);o.data.materials.append(m)
    box("Separate center for comparison",(0,0,-.013),(8,45,.026),(.31,.143,.065))
    box("Studio display base",(0,0,-.23),(27.5,46.8,.42),(.082,.104,.111))
    bpy.ops.mesh.primitive_plane_add(size=300,location=(0,0,-.45))
    m=bpy.data.materials.new("Studio dark teal");m.diffuse_color=(.078,.115,.117,1)
    bpy.context.object.data.materials.append(m)
    s=bpy.context.scene;s.world.color=(.255,.285,.3)
    def aim(o, pos):
        o.rotation_euler=(Vector(pos)-o.location).to_track_quat("-Z","Y").to_euler()
    for pwr,radius,loc,col in [
        (16000,20,(-19,-21,36),(1,.87,.69)),
        (14000,22,(21,8,29),(.69,.84,1)),
        (23000,25,(-3,29,31),(1,.71,.47)),
    ]:
        bpy.ops.object.light_add(type="AREA",location=loc)
        o=bpy.context.object;o.data.energy=pwr;o.data.size=radius;o.data.color=col;aim(o,(0,0,0))
    bpy.ops.object.camera_add(location=(42,-60,37))
    s.camera=bpy.context.object;aim(s.camera,(0,0,.9));s.camera.data.type="ORTHO";s.camera.data.ortho_scale=54
    s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
    s.render.resolution_x=1440;s.render.resolution_y=1060;s.render.resolution_percentage=100
    s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=90
    s.render.filepath=str(out/"d7-launch-wall-pair-reimport.jpg")
    bpy.ops.render.render(write_still=True)

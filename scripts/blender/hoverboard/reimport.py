"""Reimport the hoverboard and verify the static geometry; optional studio comparison."""
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector

folder = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(folder/"wsc-prop-032-hoverboard.glb"))
board, = [o for o in bpy.context.scene.objects if o.type == "MESH"]
assert len(board.data.materials) == 4
assert board.location.length < 1e-7
bpy.context.view_layer.update()
board.data.calc_loop_triangles()
counts = [0]*4
for t in board.data.loop_triangles:
    counts[t.material_index] += 1
assert counts == [524,140,376,192],counts
name = "Cyan rim, inlay and nose lamp"
faces = [p for p in board.data.polygons if board.data.materials[p.material_index].name == name]
pts = [board.matrix_world @ board.data.vertices[i].co for p in faces for i in p.vertices]
# The nose lamp sits near native Z=-.375: Blender front converts to +Y.
assert any(.36<v.y<.39 and v.z>.087 for v in pts)
assert len([v for v in pts if v.y<-.34 and v.z>.087])==0
vs = [board.matrix_world@v.co for v in board.data.vertices]
bounds = [(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)]
assert abs(bounds[2][0]-.014) < 1e-6, bounds
assert abs(bounds[0][1]-bounds[0][0]-.30)<1e-6 and abs(bounds[1][1]-bounds[1][0]-.92)<1e-6
print("Static GLB reimport passed:", counts, bounds, "floor reference offset +0.061 m")

if os.getenv("WSC_HOVERBOARD_RENDER") != "1":
    raise SystemExit(0)

second = bpy.data.objects.new("Hoverboard underside view",board.data)
bpy.context.collection.objects.link(second)
board.location = (-.60,.03,.28)
board.rotation_euler = (math.radians(11),math.radians(-12),math.radians(-21))
second.location = (.60,-.03,.29)
second.rotation_euler = (math.radians(8),math.radians(158),math.radians(21))
def mat(name,color,r=.65):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    q=m.node_tree.nodes.get("Principled BSDF")
    q.inputs["Base Color"].default_value=(*color,1);q.inputs["Roughness"].default_value=r
    return m
def plinth(x):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.48,depth=.064,location=(x,0,.011))
    o=bpy.context.object;o.scale.y=1.27;o.data.materials.append(mat("Stone display",(.072,.078,.092)))
    b=o.modifiers.new("Soft display edge","BEVEL");b.width=.014;b.segments=2
plinth(-.60);plinth(.60)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.022))
bpy.context.object.data.materials.append(mat("Studio dark steel",(.037,.056,.070)))
s=bpy.context.scene;s.world.color=(.20,.22,.25)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
for p,power,size,color in [
    ((-1.5,-2,3.1),115,2.1,(1,.86,.70)),((2,.3,2.5),77,1.9,(.71,.86,1)),
    ((0,2,2.1),132,2.2,(.69,.85,1))]:
    bpy.ops.object.light_add(type="AREA",location=p)
    o=bpy.context.object;o.data.energy=power;o.data.size=size;o.data.color=color;aim(o,(0,0,.1))
bpy.ops.object.camera_add(location=(.87,-3.75,3.5))
s.camera=bpy.context.object;aim(s.camera,(0,0,.24))
s.camera.data.type="ORTHO";s.camera.data.ortho_scale=2.6
s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
s.render.resolution_x=1440;s.render.resolution_y=960;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=90
s.render.filepath=str(folder/"wsc-prop-032-hoverboard-reimport.jpg")
bpy.ops.render.render(write_still=True)

"""Blender proof from the four selections resolved out of the same GLB."""
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

folder=Path(sys.argv[-1]).resolve()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cache_finishes import FINISHES, linear
s=bpy.context.scene
def matte(n,c,rough=.71,emission=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    q=m.node_tree.nodes.get("Principled BSDF");q.inputs["Base Color"].default_value=(*c,1)
    q.inputs["Roughness"].default_value=rough;q.inputs["Emission Color"].default_value=(*c,1)
    q.inputs["Emission Strength"].default_value=emission
    return m
base=matte("Dark concrete display",(.036,.064,.078))
ground=matte("Studio backdrop",(.029,.047,.062))
ink=matte("Pale stencil",(.856,.87,.80),.67,.23)
def label(word,size,p,ma):
    c=bpy.data.curves.new(word,"FONT");c.body=word;c.align_x="CENTER";c.size=size
    o=bpy.data.objects.new(word,c);bpy.context.collection.objects.link(o)
    o.location=p;o.rotation_euler.x=.65;c.materials.append(ma)
    return o
def slab(n,p,dim,ma,r=.017):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
    if r:
        b=o.modifiers.new("Studio chamfer","BEVEL");b.width=r;b.segments=2
    return o
boards=[]
for x,style in zip((-.893,-.298,.298,.893),FINISHES):
    seen=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(folder/f'{style["tag"]}-preview.glb'))
    board,=[o for o in set(s.objects)-seen if o.type=='MESH']
    board.data.calc_loop_triangles()
    actual={m.name:0 for m in board.data.materials}
    for t in board.data.loop_triangles:actual[board.data.materials[t.material_index].name]+=1
    assert sorted(actual.values())==[140,192,376,524] and all(k.startswith(style["name"]) for k in actual)
    boards.append(board)
    board.location=(x,.10,.19)
    board.rotation_euler=(math.radians(8),math.radians(-29),math.radians(-8))
    slab(style["name"]+" stand",(x,0,-.031),(.541,1.26,.062),base)
    accent=matte(style["name"]+" accent",tuple(linear(style["lamp"])),.54,.25)
    slab(style["name"]+" label bar",(x,-.447,.009),(.117,.012,.007),accent,.004)
    label(style["name"].upper(),.050,(x,-.548,.017),ink)
slab("Gallery ground",(0,0,-.116),(170,150,.100),ground,0)
label("WEST CACHE  /  HOVERBOARD FINISHES",.103,(0,.79,.35),ink)
sub=label("TOP     ·     FOUR PALETTES, ONE BOARD",.049,(0,.76,.22),
      matte("Cool secondary stencil",(.26,.62,.61),.7,.24))
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
for p,power,r,c in [((-2,-3,4.3),720,4.6,(1,.90,.81)),((3,-1.2,4.8),510,4.2,(.71,.87,1)),((.2,3.2,3.4),610,3.1,(.75,.92,1))]:
    bpy.ops.object.light_add(type="AREA",location=p)
    o=bpy.context.object;o.data.energy=power;o.data.size=r;o.data.color=c;aim(o,(0,0,.24))
bpy.ops.object.camera_add(location=(0,-3.22,4.4))
s.camera=bpy.context.object;aim(s.camera,(0,0,.135));s.camera.data.type="ORTHO";s.camera.data.ortho_scale=2.75
s.world.color=(.17,.18,.21)
s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
s.render.resolution_x=1500;s.render.resolution_y=1010;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=91
s.render.filepath=str(folder/"nov23-west-cache-hoverboard-finishes.jpg")
bpy.ops.render.render(write_still=True)

for b in boards:b.rotation_euler=(math.radians(7),math.radians(158),math.radians(-8))
sub.data.body="UNDERSIDE     ·     SAME FOUR FINISHES"
s.render.filepath=str(folder/"nov23-west-cache-hoverboard-undersides.jpg")
bpy.ops.render.render(write_still=True)

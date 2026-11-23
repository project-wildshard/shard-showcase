"""Fresh reimports of seven tracked catalogue assets with misleading or missing statuses."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

out=output_directory()
src=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
inventory=[
    ("WSC-PROP-002","Safety bollard","utility-bollard.glb",22816),
    ("WSC-PROP-003","Cargo crate","haul-crate.glb",103504),
    ("WSC-PROP-004","Wall lantern","wall-lantern.glb",206356),
    ("WSC-PROP-005","Market stall","market-awning-stall.glb",500480),
    ("WSC-MODULE-029","Shuttered window","window-shutter-module.glb",370596),
    ("WSC-PLAN-007","Jump-pad casing","wsc-plan-007-mover-jump-pad-casing.glb",244676),
    ("WSC-PLAN-008","Mounting block","wsc-plan-008-horse-mounting-block-wip.glb",263288),
]
places=[(-4.50,1.57),(-1.50,1.57),(1.50,1.57),(4.50,1.57),(-3.04,-1.76),(0,-1.76),(3.04,-1.76)]
clear_scene()

def mat(name,color,rough=.70,emission=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    q=m.node_tree.nodes.get("Principled BSDF")
    q.inputs["Base Color"].default_value=(*color,1);q.inputs["Roughness"].default_value=rough
    q.inputs["Emission Color"].default_value=(*color,1);q.inputs["Emission Strength"].default_value=emission
    return m

plinth=mat("Studio dark slate",(.041,.062,.072))
floor=mat("Studio background",(.066,.095,.107),.92)
text=mat("Slate plate letters",(.70,.83,.83),.79,.25)
muted=mat("Catalogue ID highlight",(.78,.45,.17),.73,.18)

def label(s,size,p,m):
    c=bpy.data.curves.new(s,"FONT");c.body=s;c.align_x="CENTER";c.size=size
    o=bpy.data.objects.new(s,c);bpy.context.collection.objects.link(o)
    o.location=p;o.rotation_euler.x=math.radians(39)
    c.materials.append(m)

def tile(x,y):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,-.075))
    o=bpy.context.object;o.dimensions=(2.61,2.56,.15)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(plinth)
    b=o.modifiers.new("Display edges","BEVEL");b.width=.035;b.segments=1

info=[]
for (key,name,filename,n),(x,y) in zip(inventory,places):
    path=src/filename
    blob=path.read_bytes()
    assert len(blob)==n and blob.startswith(b"glTF")
    seen=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    added=set(bpy.context.scene.objects)-seen
    meshes=[o for o in added if o.type=="MESH"]
    assert meshes
    xyz=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    lo=[min(v[k] for v in xyz) for k in range(3)];hi=[max(v[k] for v in xyz) for k in range(3)]
    dims=[b-a for a,b in zip(lo,hi)]
    for o in meshes:o.data.calc_loop_triangles()
    num=sum(len(o.data.loop_triangles) for o in meshes)
    assert num>0 and min(dims)>0
    scale=min(1.91/max(dims[:2]),1.30/dims[2])
    center=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]))
    place=Matrix.Translation((x,y+.12,.017))@Matrix.Scale(scale,4)@Matrix.Translation(-center)
    for root in added:
        if root.parent not in added:root.matrix_world=place@root.matrix_world
    tile(x,y)
    label(name,.163,(x,y-1.07,.098),text)
    label(key,.101,(x,y-1.10,.014),muted)
    info.append(dict(id=key,file=filename,bytes=n,sha256=hashlib.sha256(blob).hexdigest(),
        reimport_triangles=num,blender_dimensions_m=[round(v,4) for v in dims]))

(out/"catalogue-reimport.json").write_text(json.dumps(info,indent=2)+"\n")
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.159))
bpy.context.object.data.materials.append(floor)
s=bpy.context.scene;s.world.color=(.23,.26,.28)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
for pos,pow,size,c in [((-8,-7,11),4200,10,(1,.87,.74)),((6,-1,10),2400,9,(.74,.88,1)),
                       ((0,9,9),3800,10,(.82,.93,1))]:
    bpy.ops.object.light_add(type="AREA",location=pos)
    o=bpy.context.object;o.data.energy=pow;o.data.size=size;o.data.color=c;aim(o,(0,0,.2))
bpy.ops.object.camera_add(location=(0,-8,13))
s.camera=bpy.context.object;aim(s.camera,(0,0,.36))
s.camera.data.type="ORTHO";s.camera.data.ortho_scale=12.95
s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
s.render.resolution_x=1620;s.render.resolution_y=1110;s.render.resolution_percentage=100
s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=90
s.render.filepath=str(out/"nov23-catalogue-verified-reimports.jpg")
bpy.ops.render.render(write_still=True)

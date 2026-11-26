"""Matched, reimported porch-height views in the existing E5b visual yard."""
import hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/"showcase-studies"))
from common import clear_scene,output_directory
out=output_directory();clear_scene();S=bpy.context.scene
root=D.parents[2]
refs=root/"public/assets/wildshard-art"
layout=json.loads((root/"project/layouts/e5b-shadow-study.json").read_text())
proof=json.loads((out/"floodlight-far-proof.json").read_text())

def load(file,expected):
    assert hashlib.sha256(file.read_bytes()).hexdigest()==expected
    before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(file))
    bpy.context.view_layer.update()
    return set(S.objects)-before
cache={}
for row in layout["placements"]:
    key=row["asset"]
    if key=="floodlight":
        towerrow=row
        continue
    if key not in cache:
        ref=layout["source_assets"][key];loaded=load(refs/ref["file"],ref["sha256"])
        cache[key]=[(o.data,o.matrix_world.copy()) for o in loaded if o.type=="MESH"]
        for o in loaded:bpy.data.objects.remove(o,do_unlink=True)
    for data,matrix in cache[key]:
        obj=bpy.data.objects.new(row["name"],data);S.collection.objects.link(obj)
        obj.matrix_world=Matrix.Translation(row["center_m"])@Matrix.Rotation(math.radians(row["rotation_z"]),4,'Z')@Matrix.Diagonal((*row["scale"],1))@matrix

def aim(obj,pos):obj.rotation_euler=(Vector(pos)-obj.location).to_track_quat("-Z","Y").to_euler()
mat=bpy.data.materials.new("Presentation asphalt");mat.use_nodes=True
n=mat.node_tree.nodes["Principled BSDF"];n.inputs["Base Color"].default_value=(.112,.12,.138,1);n.inputs["Roughness"].default_value=.84
bpy.ops.mesh.primitive_plane_add(size=220,location=(0,0,-.01));bpy.context.object.data.materials.append(mat)
S.world.use_nodes=True
n=S.world.node_tree.nodes["Background"];n.inputs[0].default_value=(.092,.167,.25,1);n.inputs[1].default_value=.52
for name,p,energy,size,c in [("Cool sky card",(-7,4,17),18000,16,(.59,.75,1)),("Warm soft horizon",(-15,-18,12),20000,21,(1,.70,.45)),("Blue back edge",(5,9,13),16000,18,(.54,.77,1))]:
    l=bpy.data.lights.new(name,'AREA');l.energy=energy;l.size=size;l.color=c
    o=bpy.data.objects.new(name,l);S.collection.objects.link(o);o.location=p;aim(o,(-5,4,4.2))
cam=bpy.data.cameras.new("Yard match");o=bpy.data.objects.new("Yard match",cam);S.collection.objects.link(o);S.camera=o
o.location=(-15,-34,1.70);aim(o,(-6.7,4.5,4.3))
cam.sensor_fit='VERTICAL';cam.sensor_height=24;cam.lens=43
S.render.engine='CYCLES';S.cycles.samples=26;S.cycles.use_denoising=False
S.view_settings.view_transform='AgX'
S.render.resolution_x=804;S.render.resolution_y=1748;S.render.resolution_percentage=100
S.render.image_settings.file_format='WEBP';S.render.image_settings.quality=88
for n,p,sha in [("source",refs/layout["source_assets"]["floodlight"]["file"],proof["original"]["sha256"]),
                ("far",out/"wsc-module-024-floodlight-tower-far.glb",proof["far"]["sha256"])]:
    loaded=load(p,sha)
    for ob in loaded:
        if ob.parent not in loaded:
            ob.matrix_world=Matrix.Translation(towerrow["center_m"])@Matrix.Rotation(math.radians(towerrow["rotation_z"]),4,'Z')@ob.matrix_world
    S.render.filepath=str(out/f"nov26-e5b-floodlight-{n}.webp")
    bpy.ops.render.render(write_still=True)
    for ob in loaded:bpy.data.objects.remove(ob,do_unlink=True)

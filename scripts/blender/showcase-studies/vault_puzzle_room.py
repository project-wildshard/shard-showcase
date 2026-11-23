"""WSC-KIT-008 / room one. Source-backed visual composition, not gameplay."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out=output_directory()
assets=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art"
sources={
    "tile":"wsc-prop-064-metal-floor-plates.glb",
    "door":"wsc-prop-063-round-vault-bulkhead.glb",
    "plate":"wsc-plan-006-pressure-plate.glb",
    "crate":"haul-crate.glb",
    "bay":"wsc-arch-002-industrial-wall-bay.glb",
}
clear_scene()
templates={}
placements=[]

for key,n in sources.items():
    pre=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(assets/n))
    bpy.context.view_layer.update()
    obs=set(bpy.context.scene.objects)-pre
    templates[key]=[(o.data,o.matrix_world.copy()) for o in sorted(obs,key=lambda o:o.name) if o.type=="MESH"]
    for o in obs:bpy.data.objects.remove(o,do_unlink=True)

def place(asset, name, p, yaw=0, size=1, vertical=None, tread_mm=0):
    transform=Matrix.Translation(p) @ Matrix.Rotation(math.radians(yaw),4,'Z')
    if vertical is not None:transform=transform@Matrix.Rotation(math.radians(vertical),4,'X')
    transform=transform@Matrix.Scale(size,4)
    placed=[]
    for mesh, local in templates[asset]:
        ob=bpy.data.objects.new(f"{name} · {mesh.name}",mesh)
        bpy.context.collection.objects.link(ob)
        ob.matrix_world=transform@local
        if tread_mm and mesh.name.startswith('Cube.028'):
            ob.location.z-=tread_mm/1000
        placed.append(ob)
    placements.append(dict(asset=asset,name=name,origin_m=p,z_yaw_deg=yaw,uniform_scale=size,
                           x_tilt_deg=vertical or 0,tread_travel_mm=tread_mm))
    return placed

def material(name,color,rough=.48,metal=.13,emit=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    q=m.node_tree.nodes.get("Principled BSDF")
    q.inputs["Base Color"].default_value=(*color,1)
    q.inputs["Metallic"].default_value=metal;q.inputs["Roughness"].default_value=rough
    q.inputs["Emission Color"].default_value=(*color,1);q.inputs["Emission Strength"].default_value=emit
    return m

cladding=material("Vault graphite enamel",(.072,.094,.105))
reveal=material("Recessed oxidised steel",(.026,.043,.053))
silver=material("Vault zinc edge",(.25,.31,.32),.42,.43)
amber=material("Safety enamel amber",(.79,.237,.044),.54)
pale=material("Warm ivory decals",(.84,.81,.69),.61,.04,.16)
cyan=material("Cyan room wayfinding",(.075,.69,.89),.33,.08,2.15)
green=material("Active plate luminance",(.045,.67,.16),.34,.12,2.35)
unlit=material("Unpowered warm plate outline",(.79,.27,.039),.41,.15, .32)
white=material("Ceiling panel lamp",(.63,.79,.82),.4,.06,2.6)

def box(name,p,d,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=name;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new("Soft manufactured edges","BEVEL");b.width=bevel;b.segments=2
        o.modifiers.new("Weighted face normals","WEIGHTED_NORMAL")
    return o

def text(name, body, p, size, mat, rot=(math.pi/2,0,0)):
    curve=bpy.data.curves.new(name,"FONT");curve.body=body;curve.size=size;curve.align_x="CENTER"
    ob=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(ob);ob.location=p;ob.rotation_euler=rot
    curve.materials.append(mat)
    return ob

def signal(p, m):
    # Reusable low-cost enclosure with one emissive insert and end caps.
    x,y,z=p
    return [
        box("Indicator · back shell",(x,y,z),(.57,.125,.23),reveal,.033),
        box("Indicator · rail",(x,y-.065,z),(.45,.034,.135),silver,.018),
        box("Indicator · status insert",(x,y-.088,z),(.38,.013,.093),m,.014),
        *[box("Indicator · fastener",(x+dx,y-.076,z),(.032,.023,.064),cladding,.008)
          for dx in (-.246,.246)],
    ]

def light(name,p,aim_at,power,size,c, width=None):
    data=bpy.data.lights.new(name,"AREA");data.energy=power;data.color=c
    data.shape="DISK" if width is None else "RECTANGLE";data.size=size
    if width is not None:data.size_y=width
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    obj.location=p;obj.rotation_euler=(Vector(aim_at)-obj.location).to_track_quat("-Z","Y").to_euler()
    return obj

# One export with two named indicator states, at the same floor and identical scaled construction.
indicator=signal((-.38,0,.115),green)+signal((.38,0,.115),unlit)
for o in indicator:
    bpy.context.view_layer.objects.active=o
    for mod in tuple(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=mod.name)
asset_path=out/"wsc-kit-008-puzzle-indicators.glb"
export(indicator,asset_path)
for ob in indicator:bpy.data.objects.remove(ob,do_unlink=True)
before=set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=str(asset_path))
checks=set(bpy.context.scene.objects)-before
assert len(checks)==10 and all(o.type=="MESH" for o in checks)
bpy.context.view_layer.update()
for o in checks:o.data.calc_loop_triangles()
indicator_tris=sum(len(o.data.loop_triangles) for o in checks)
assert 120<indicator_tris<2000
assert {green.name,unlit.name}<={m.name.rsplit(".",1)[0] if m.name.rsplit(".",1)[-1].isdigit() else m.name for o in checks for m in o.data.materials}
xyz=[o.matrix_world@v.co for o in checks for v in o.data.vertices]
dims=[round(max(v[k] for v in xyz)-min(v[k] for v in xyz),3) for k in range(3)]
assert dims==[1.33,.157,.23],dims
for ob in checks:bpy.data.objects.remove(ob,do_unlink=True)

# Actual model reuse. Each repeated asset keeps the original Blender mesh datablock.
walls=[];ceiling=[]
W=4.73; D=6.31; F=.112
box("Floor root",(0,0,-.15),(2*W,2*D,.28),reveal,.039)
for i in range(3):
    for j in range(4):
        place("tile",f"Floor tile {i+1}-{j+1}",((i-1)*3.154,(j-1.5)*3.154,0),90*((i+j)%4))
assert len({id(mesh) for mesh,_ in templates['tile']})==8

for sign in (-1,1):
    wallx=sign*W
    walls.append(box("Exterior service wall",(wallx,0,2.18),(.26,12.62,4.36),reveal,.052))
    for j,y in enumerate((-4.71,-1.57,1.57,4.71)):
        # Spec bay is 3.60 m wide; fit each inner lining to 3.15 m.
        walls+=place("bay",f"Wall {'west' if sign<0 else 'east'} bay {j+1}",(wallx-sign*.18,y,F),sign*90,.875)
        walls.append(box("Amber acoustic cassette",(wallx-sign*.161,y,2.64),(.18,3.02,1.52),amber,.055))
        walls.append(box("Cassette upper lip",(wallx-sign*.26,y,3.425),(.03,3.03,.05),silver,.008))
        walls.append(box("Cassette inlay",(wallx-sign*.26,y,2.023),(.028,2.8,.033),cladding,.005))
        walls.append(box("Side light tube",(wallx-sign*.23,y,3.68),(.09,2.80,.09),white,.017))
        light("Concealed side light",(wallx-sign*.38,y,3.66),(0,y,1.10),90,2.60,(.66,.86,1),.12)
    walls.append(box("Running floor crash rail",(wallx-sign*.27,0,.29),(.15,12.46,.16),silver,.031))

box("Locked service bulkhead recess",(0,D-.18,2.22),(3.86,.40,4.24),reveal,.16)
box("Return wall skin",(0,D+.12,2.20),(9.48,.18,4.4),cladding,.045)
for x in (-3.39,3.39):
    place("bay","Rear return wall bay",(x,D-.25,F),0,.72)
    box("Rear high surround",(x,D-.15,2.76),(2.80,.31,2.34),cladding,.07)
    box("Rear field amber stripe",(x,D-.33,2.53),(1.46,.07,.12),amber,.022)
place("door","Locked round vault bulkhead",(0,D-.51,F),0,1.04)
for x,m,letter in [(-.65,green,"A"),(.65,unlit,"B")]:
    signal((x,D-.47,3.48),m)
    text(f"Status {letter}",letter,(x,D-.570,3.69),.157,pale)
text("Door legend","TRAINING VAULT   /   01",(0,D-.416,3.89),.21,pale)
for x in (-1.93,1.93):
    box("Door flanking lock mark",(x,D-.463,1.42),(.06,.035,1.40),amber,.011)
text("Circuit instructions","WEIGH BOTH PLATES",(0,D-.417,.30),.151,pale)

plate_y=2.35
for x,word,m in [(-2.20,"A",green),(2.20,"B",unlit)]:
    plate=place("plate",f"Plate {word}",(x,plate_y,F),0,.50,tread_mm=25 if word=="A" else 0)
    assert len(plate)==2
    for dx in (-1.047,1.047):box("Plate side inlay",(x+dx,plate_y,F+.032),(.072,2.02,.057),m,.013)
    for dy in (-1.047,1.047):box("Plate front inlay",(x,plate_y+dy,F+.032),(2.02,.072,.057),m,.013)
    box("Number plate",(x,plate_y-1.21,F+.036),(.54,.33,.050),reveal,.038)
    text("Floor marker",word,(x,plate_y-1.32,F+.066),.23,pale,(0,0,0))
place("crate","Crate on plate A",(-2.20,plate_y,F+.3425*.50-.025),0)
place("crate","Spare crate at start",(1.25,-2.32,F),0)

for x,m in [(-2.20,green),(2.20,unlit)]:
    # Indicative inset conduits, laid on the visible top of the exact checked floor tile.
    for i in range(8):
        box("Paced inset route marker",(x,-3.86+i*.52,F+.014),(.037,.29,.027),m,.008)

for y in (-4.8,-1.6,1.6,4.8):
    for x in (-3.18,0,3.18):
        ceiling.append(box("Service ceiling cassette",(x,y,4.21),(3.115,3.11,.15),cladding,.043))
    ceiling.append(box("Overhead spine",(0,y,4.095),(.29,3.15,.11),reveal,.028))
    span=2.28 if y>4 else 2.86
    ceiling.append(box("Overhead strip optic",(0,y-.19 if y>4 else y,4.025),(.15,span,.057),white,.014))
    light("Ceiling strip",(0,y,3.97),(0,y,.12),220,2.80,(.72,.89,1),.15)

light("Bulkhead key",(0,3.2,3.86),(0,D,2.04),200,3.0,(.72,.86,1))
light("Entrance reflection",(-1,-6.2,2.12),(0,4.0,.9),280,3.8,(1.0,.80,.61))
light("Active feedback bounce",(-2.20,plate_y-.1,.65),(-2.20,plate_y+1.0,.2),22,.9,(.23,1.0,.60))
light("Amber feedback bounce",(2.22,plate_y-.1,.48),(2.2,plate_y+1.1,.2),8,.75,(1.0,.49,.17))
s=bpy.context.scene;s.world.color=(.12,.14,.16)
s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.055;s.cycles.use_denoising=False
s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=91

def render(file,p,at,wh,lens,ortho=None):
    bpy.ops.object.camera_add(location=p)
    s.camera=bpy.context.object
    s.camera.rotation_euler=(Vector(at)-s.camera.location).to_track_quat('-Z','Y').to_euler()
    s.camera.data.lens=lens
    if ortho:s.camera.data.type='ORTHO';s.camera.data.ortho_scale=ortho
    s.render.resolution_x,s.render.resolution_y=wh
    s.render.filepath=str(out/file)
    bpy.ops.render.render(write_still=True)

report={
    "blender_axes":"X across room, Y toward exit, Z up",
    "wall_reference_m":[9.46,12.62,4.025],
    "indicators":{"triangles":indicator_tris,"dimensions_m":dims,"bytes":asset_path.stat().st_size},
    "plate_clear_gap_m":2.40,
    "logic":"Illustrated state: A weighted, B empty, door locked. Static reference only.",
    "sources":{k:{"file":n,"sha256":hashlib.sha256((assets/n).read_bytes()).hexdigest()} for k,n in sources.items()},
    "placements":placements,
}
(out/"vault-room-01-layout.json").write_text(json.dumps(report,indent=2)+"\n")
if os.environ.get('VAULT_CUTAWAY_ONLY') != '1':
    render('nov23-vault-room-01-entry.jpg',(0,-5.95,1.72),(0,5.6,2.18),(1500,1080),23)
for ob in ceiling+walls:ob.hide_render=True
# Roofing is hidden only for the analysis view. Keep the main four visibility anchors.
for ob in bpy.context.scene.objects:
    if ob.type=="LIGHT" and ob.name.startswith(("Ceiling strip","Concealed side light")):ob.hide_render=True
box("Cutaway backdrop",(0,0,-.42),(200,200,.17),material("Cutaway dark background",(.026,.047,.053)),.0)
light("Cutaway key",(-6,-6,11),(0,0,0),1800,11,(.88,.93,1))
light("Cutaway fill",(5,7,10),(0,0,0),1350,9,(.7,.87,1))
render('nov23-vault-room-01-layout.jpg',(8,-11,13),(0,.18,1.73),(1440,1080),42,19.30)

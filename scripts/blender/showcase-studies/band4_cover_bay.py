"""Exact Round 5 bay envelope; render existing foundry donors as a fit study."""
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
assets=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art'
bay=out/'e4-cover-bay-shell.glb'
furnace=assets/'wsc-prop-057-foundry-furnace.glb'
slag=assets/'e4-ground-slag-decal.glb'
for f,h in [
    (furnace,'0c47183c8f38699661f527d01b8e85a4891e03ec898cabd028b07568e32b8530'),
    (slag,'5e4ff946ef5291df0d08ff0e5d7ed8f07a3a13c60716606da410604f774487c8'),
]:
    assert hashlib.sha256(f.read_bytes()).hexdigest()==h
x,z,a=186.43627261251038,-116.5796015237363,1.6166407742660256
def map_point(u,v):
    # v is the original local forward +Z; Blender local forward is −Y.
    return [x+math.cos(a)*u+math.sin(a)*v,z-math.sin(a)*u+math.cos(a)*v]
entry=(224,-122)
assert 37.95<math.dist((x,z),entry)<37.96
floor_p=map_point(0,1.2)
sample_p=map_point(0,6)

def load(p,off=(0,0,0),yaw=0):
    prior=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    parts=sorted(set(bpy.context.scene.objects)-prior,key=lambda o:o.name)
    T=Matrix.Translation(off)@Matrix.Rotation(yaw,4,'Z')
    for o in parts:
        if o.parent is None:o.matrix_world=T@o.matrix_world
    bpy.context.view_layer.update()
    return parts

def mat(n,rgb,rough=.69,metal=0,emit=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    for k,v in [('Base Color',(*rgb,1)),('Roughness',rough),('Metallic',metal),
                ('Emission Color',(*rgb,1)),('Emission Strength',emit)]:
        p.inputs[k].default_value=v
    return m

def box(n,p,d,m,b=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if b:
        v=o.modifiers.new('Cast edge','BEVEL');v.width=b;v.segments=1
        bpy.ops.object.modifier_apply(modifier=v.name)
    o.data.materials.append(m);return o

clear_scene()
grey=mat('Weathered foundry concrete',(.183,.207,.216),.83)
ink=mat('Folded iron shielding',(.054,.083,.089),.51,.48)
rust=mat('Worn iron red',(.255,.087,.038),.66,.25)
ochre=mat('Ochre service paint',(.51,.239,.053),.68,.13)
steel=mat('Stamped steel',(.244,.275,.266),.58,.55)
slab=mat('Foundry grade / stage',(.130,.151,.153),.78)
paint=mat('Measured proxy ring / stage',(.42,.72,.66),.65,0,.22)

parts=[
    box('6 m rear wall',(0,2,1.50),(6,.50,3.00),grey,.03),
    box('Rear flashing',(0,2,2.92),(5.93,.49,.12),ink,.016),
]
for i in (-1,1):
    side=3*i
    parts += [
        box('4 m side return',(side,0,1.5),(.50,4.00,3.00),grey,.03),
        box('Side flashing',(side,0,2.927),(.466,3.94,.12),ink,.016),
        box('Mouth jamb facing',(side,-1.953,1.54),(.432,.075,2.83),rust,.025),
        box('Yellow corner stripe',(side,-1.996,2.37),(.34,.007,.10),ochre),
        box('Steel boot plate',(side,-1.99,.30),(.43,.015,.48),ink,.005),
    ]
    for y in (-1.43,-.78,-.13,.52,1.17,1.82):
        parts.append(box('Panel rib',(side+i*.232,y,1.66),(.032,.102,2.41),steel,.011))
    for h in (1.47,1.64,1.81):
        o=box('Jamb paint slash',(side,-1.992,h),(.25,.010,.04),ochre)
        o.rotation_euler.y=.35
for u in [-2.79,-1.86,-.93,0,.93,1.86,2.79]:
    parts.append(box('Rear panels outside face',(u,2.23,1.54),(.066,.032,2.70),ink,.008))
export(sorted(parts,key=lambda o:o.name),bay)

def pts(o):
    return [q.matrix_world @ v.co for q in o if q.type=='MESH' for v in q.data.vertices]

def rr(fr,to):
    s=bpy.context.scene; aa,bb=Vector(fr),Vector(to);d=bb-aa
    return s.ray_cast(bpy.context.evaluated_depsgraph_get(),aa,d.normalized(),distance=d.length)

clear_scene()
b=pts(load(bay))
assert abs(max(v.z for v in b)-3)<1e-5
assert abs(max(abs(v.x) for v in b)-3.25)<1e-5
for y in (-1.85,-1,0,1):
    a0=rr((0,y,1.36),(-3.5,y,1.36))
    b0=rr((0,y,1.36),(3.5,y,1.36))
    assert a0[0] and b0[0] and abs((b0[1].x-a0[1].x)-5.5)<1e-5
fr=pts(load(furnace,(.52,.56,0)))
sl=pts(load(slag,(0,-1.2,.003),math.pi))
back=1.75-max(v.y for v in fr)
side=2.75-max(abs(v.x) for v in fr)
between=min(v.y for v in fr)-max(v.y for v in sl)
assert abs(min(v.z for v in fr))<1e-6
assert abs(min(v.z for v in sl)-.003)<1e-6
assert back>.059 and side>.86 and between>.013,(back,side,between)
box('Ground stage',(0,0,-.08),(110,110,.16),slab)
for v in sl[::max(1,len(sl)//20)]:
    # No underside claim for one-sided meshes; test actual floor from just below decal.
    hit,p,_,_,obj,_=rr((v.x,v.y,.002),(v.x,v.y,-.10))
    assert hit and abs(p.z)<1e-6
proof={'map_anchor_x_z':[x,z],'world_yaw':a,'arch_x_z':entry,
       'marker_x_z':floor_p,'inspection_x_z':sample_p,'original_proxy_radius_m':1.4,
       'mouth_m':5.5,'height_m':3,'floor_offset_m':.003,
       'furnace_editorial_local_blender':[.52,.56,0],
       'furnace_bounds_margins':{'back':back,'side':side,'slag_y':between},
       'native_placement_or_gameplay':False}
(out/'e4-cover-bay-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print(proof)
if os.getenv('WILDSHARD_VALIDATE_ONLY')=='1':
    sys.exit(0)

def aim(o,target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

s=bpy.context.scene
w=s.world;w.use_nodes=True
bg=w.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.143,.266,.35,1);bg.inputs[1].default_value=.45
for p,t,watt,c,r in [
    ((-4,-6,8),(0,.5,1),2400,(.58,.79,1),6),
    ((4,1,6),(0,-1,1),2150,(1,.50,.23),5),
    ((.55,-.93,1.1),(.2,-1.35,.1),94,(1,.44,.13),1.3),
]:
    bpy.ops.object.light_add(type='AREA',location=p)
    ob=bpy.context.object;ob.data.energy=watt;ob.data.size=r;ob.data.color=c;aim(ob,t)

# Archived 2.8 m proxy shown as a non-exported thin ring in the overhead study.
N=80
pv=[(r*math.cos(i*math.tau/N),-1.2+r*math.sin(i*math.tau/N),.011)
    for r in (1.38,1.40) for i in range(N)]
faces=[(i,i+N,(i+1)%N+N,(i+1)%N) for i in range(N)]
data=bpy.data.meshes.new('Archive proxy comparison ring')
data.from_pydata(pv,[],faces);data.update();data.materials.append(paint)
ring=bpy.data.objects.new('Archive overlay only',data);s.collection.objects.link(ring)

bpy.ops.object.camera_add()
s.camera=bpy.context.object
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False
s.render.resolution_x=1320;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=90
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
for label,eye,target,lens in [
    ('e4-bay-mouth',(0,-6,1.7),(.03,-.40,1.25),32),
    ('e4-bay-overview',(-7,-8,10),(0,0,.8),42),
]:
    ring.hide_render=label=='e4-bay-mouth'
    s.camera.location=eye;aim(s.camera,target);s.camera.data.lens=lens
    s.render.filepath=str(out/(label+'.jpg'))
    bpy.ops.render.render(write_still=True)

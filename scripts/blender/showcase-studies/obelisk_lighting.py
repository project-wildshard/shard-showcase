"""W11a obelisk lighting comparison, with an optional separate fixture GLB."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import struct
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,export,output_directory

root=Path(__file__).resolve().parents[3]
out=output_directory()
L=json.loads((root/'project/layouts/w11a-obelisk-lighting.json').read_text())
origin=Vector(L['obelisk_world_xyz'])
assets=root/'public/assets/wildshard-art'
s=bpy.context.scene
clear_scene()

def mat(n,c,rough=.62,metal=0,em=0,emc=None):
    m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1)
    b=m.node_tree.nodes['Principled BSDF']
    for k,v in (('Base Color',(*c,1)),('Roughness',rough),('Metallic',metal),
                ('Emission Color',(*(c if emc is None else emc),1)),('Emission Strength',em)):
        b.inputs[k].default_value=v
    return m

iron=mat('Forged black bronze',(.042,.036,.024),.46,.56)
brass=mat('Brushed brass trim',(.36,.212,.068),.41,.51)
ceramic=mat('Limestone bracket',(.38,.30,.18),.72)
glass=mat('Fixture clear amber',(.58,.29,.08),.33,.05,0,(1,.43,.094))

def box(n,m,p,d,b=0,rz=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.scale=d;o.rotation_euler.z=rz
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if b:
        mo=o.modifiers.new('Soft machined edge','BEVEL');mo.width=b;mo.segments=1
        bpy.ops.object.modifier_apply(modifier=mo.name)
    return o

ps=[
    box('Stone mount',ceramic,(0,0,.047),(.52,.456,.094),.018),
    box('Forged body',iron,(0,0,.132),(.415,.364,.154),.027),
    box('Brass bezel',brass,(0,-.025,.214),(.367,.277,.048),.024),
    box('Recessed lens',glass,(0,-.028,.241),(.302,.215,.018),.012),
]
for x in (-.156,.156):
    ps.append(box('Baffle rail',iron,(x,-.012,.255),(.024,.248,.026),.006))
ps.append(box('Rear anti-glare hood',iron,(0,.090,.271),(.357,.058,.059),.012))
for x,y in itertools.product((-.195,.195),(-.135,.135)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.011,depth=.020,location=(x,y,.183))
    o=bpy.context.object;o.name='Base fastener';o.data.materials.append(brass);ps.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in ps:o.select_set(True)
bpy.context.view_layer.objects.active=ps[0]
bpy.ops.object.join()
fixture=ps[0];fixture.name='Hooded obelisk uplight'
s.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
dst=out/'w11a-obelisk-uplight.glb'
export([fixture],dst)
raw=dst.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tri=sum(d['accessors'][p['indices']]['count']//3 for m in d['meshes'] for p in m['primitives'])
assert len(d['meshes'])==1 and len(raw)<45000 and tri<900
assert not any(d.get(k) for k in ('images','skins','animations')) and 'KHR_lights_punctual' not in d.get('extensionsUsed',[])

clear_scene()
def import_mesh(path):
    old=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(path));bpy.context.view_layer.update()
    all=set(s.objects)-old
    seq=[(o.data,o.matrix_world.copy()) for o in sorted(all,key=lambda o:o.name) if o.type=='MESH']
    for o in all:bpy.data.objects.remove(o,do_unlink=True)
    assert seq,path
    return seq
templates={'fixture':import_mesh(dst)}
for k,(f,h) in L['pins'].items():
    p=assets/f
    assert hashlib.sha256(p.read_bytes()).hexdigest()==h,f
    templates[k]=import_mesh(p)

def obj(n,d):
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);return o

def place(k,n,p=(0,0,0),heading=0,scale=1):
    M=Matrix.Translation(p)@Matrix.Rotation(heading,4,'Z')@Matrix.Scale(scale,4)
    seq=[]
    for data,t in templates[k]:
        o=obj(n,data);o.matrix_world=M@t;seq.append(o)
    bpy.context.view_layer.update()
    return seq

def tree(seq):
    vs,fs=[],[]
    for o in seq:
        st=len(vs)
        vs.extend(o.matrix_world@v.co for v in o.data.vertices)
        fs.extend(tuple(st+i for i in f.vertices) for f in o.data.polygons)
    return BVHTree.FromPolygons(vs,fs)
def worldpoints(seq):return [o.matrix_world@v.co for o in seq for v in o.data.vertices]

shaft=place('shaft','Original 22 m shaft',origin)
sv=worldpoints(shaft)
assert abs(max(q.z for q in sv)-22)<.0001
shaft_bvh=tree(shaft)
outward=Vector((-1,0,0))
clock_sample=origin+outward*6+Vector((0,0,L['clock_center_height_m']))
hit,n,_,_=shaft_bvh.ray_cast(clock_sample,-outward,6)
assert hit is not None and abs(n.x)>.9
clock=place('clock','Original clock, west-facing art pose',hit+.03*outward,-math.pi/2)
basin=place('basin','Original basin',origin+Vector((0,0,L['basin_visual_raise_m'])))
basin_r=max((q-origin).xy.length for q in worldpoints(basin))

for x,y,rz,k in ((-39,12,-.12,.90),(-29.5,12.4,.06,.98),(-20,12.7,-.08,.92),
                 (-19,-8.6,math.pi*.43,.88)):
    place('house','Illustrative plaza facade',(x,y,0),rz,k)
for x,y,k in ((-26,7.8,.95),(-43,8.8,.83),(-42,-8,.89)):
    place('tree','Existing far canopy',(x,y,.01),0,k)
for x,y in ((-43,5),(-39,-6.7),(-24,4.6)):
    place('planter','Original flower planter',(x,y,.022),0,.9)
pavers=[mat('Warm plaza pavers '+str(i),c) for i,c in enumerate((
    (.26,.231,.184),(.31,.282,.221),(.226,.216,.174),(.33,.274,.204),
    (.279,.235,.178)))]
soil=mat('Plaza grout',(.099,.092,.079))
box('Plaza base',soil,(-34,0,-.11),(195,187,.20))
rng=random.Random(227)
# Pavers are stage-only. Joining each material subset makes the render cheap.
batches={m:([],[]) for m in pavers}
for row in range(-15,17):
    for col in range(-18,21):
        x=-34+col*1.42+(row%2)*.71;y=row*.96
        z=-.030+rng.random()*.002
        verts,faces=batches[rng.choice(pavers)]
        off=len(verts)
        verts.extend((x+i*.701,y+j*.471,z+k*.0275)
                     for k in (-1,1) for j in (-1,1) for i in (-1,1))
        faces.extend(tuple(off+i for i in face) for face in (
            (0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)))
for material,(verts,faces) in batches.items():
    me=bpy.data.meshes.new('Plaza stage pavers')
    me.from_pydata(verts,[],faces);me.update();me.materials.append(material)
    obj('Plaza stage pavers',me)

def aim(o,target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def light(typ,n,p,t,power,color,size):
    d=bpy.data.lights.new(n,typ);d.energy=power;d.color=color
    if typ=='AREA':d.shape='DISK';d.size=size
    if typ=='SPOT':d.spot_size=size;d.spot_blend=.88;d.shadow_soft_size=.105
    o=obj(n,d);o.location=p;aim(o,t);return o

newlights=[];clearance=[];targets=[]
# Fixture's open lip faces inward. Preview spots start ahead of the
# model and aim up, not through the back of the housing.
for dx,dy in L['fixture_quadrant_offsets_m']:
    center=origin+Vector((dx,dy,0))
    horizontal=(origin-center).normalized()
    yaw=math.atan2(horizontal.x,-horizontal.y)
    cases=place('fixture','Matching reimported hood',center,yaw)
    pts=worldpoints(cases)
    assert abs(min(q.z for q in pts))<.00005
    clearance.append(min((q-origin).xy.length for q in pts)-basin_r)
    assert clearance[-1]>.32
    ep=center+.25*horizontal+Vector((0,0,.303))
    t=origin+Vector((dx*.092,dy*.092,15.2 if dx<0 else 11.2))
    ray=t-ep
    q,_,_,_=shaft_bvh.ray_cast(ep,ray.normalized(),ray.length+1)
    assert q is not None
    targets.append(q.z)
    newlights.append(light('SPOT','Preview obelisk uplight',ep,t,12500 if dx<0 else 5100,
                 (1,.67,.32) if dy<0 else (1,.74,.43),.48 if dx<0 else .58))

ambient=light('AREA','Existing night horizon wash',(-53,5,24),origin+Vector((0,0,9)),5800,(.46,.64,1),29)
fill=light('AREA','Sky reflection',(-16,18,17),origin,4700,(.43,.65,1),31)
light('AREA','Stage path safety light',(-47,-10,6),(-49,-9,0),300,(1,.75,.44),4)
world=bpy.data.worlds.new('Blue hour obelisk')
world.use_nodes=True
n=world.node_tree.nodes;links=world.node_tree.links
base=n['Background']
base.inputs[0].default_value=(.05,.082,.161,1);base.inputs[1].default_value=.68
# Camera-only blue band, not an added source of diffuse light.
cam_bg=n.new('ShaderNodeBackground');cam_bg.inputs[1].default_value=.65
tc=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ')
links.new(tc.outputs['Normal'],sep.inputs[0])
ab=n.new('ShaderNodeMath');ab.operation='ABSOLUTE';links.new(sep.outputs['Z'],ab.inputs[0])
r=n.new('ShaderNodeValToRGB')
r.color_ramp.elements[0].position=.02;r.color_ramp.elements[0].color=(.11,.17,.27,1)
r.color_ramp.elements[1].position=.61;r.color_ramp.elements[1].color=(.018,.039,.097,1)
links.new(ab.outputs[0],r.inputs[0]);links.new(r.outputs[0],cam_bg.inputs[0])
mix=n.new('ShaderNodeMixShader');lp=n.new('ShaderNodeLightPath')
links.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);links.new(base.outputs[0],mix.inputs[1]);links.new(cam_bg.outputs[0],mix.inputs[2])
links.new(mix.outputs[0],n['World Output'].inputs[0]);s.world=world

def same_geometry():
    return sorted((o.name,tuple(round(t,6) for row in o.matrix_world for t in row)) for o in s.objects if o.type=='MESH')
bpy.context.view_layer.update()
geometry=same_geometry()
# Use the original fixture lens reimport for the presentation only.
lampmat=next(m for o in s.objects if o.name.startswith('Matching reimported hood')
             for m in o.data.materials if m.name.startswith('Fixture clear amber'))
lamp_node=next(t for t in lampmat.node_tree.nodes if t.type=='BSDF_PRINCIPLED')
cam=obj('W11a Main Street camera',bpy.data.cameras.new('W11a Main Street camera'));s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=91
def shot(name,eye,target,wh,lens,lit):
    for o in newlights:o.hide_render=not lit
    lamp_node.inputs['Emission Color'].default_value=(1,.48,.11,1)
    lamp_node.inputs['Emission Strength'].default_value=2.35 if lit else 0
    cam.location=eye;aim(cam,target);cam.data.lens=lens
    s.render.resolution_x,s.render.resolution_y=wh
    bpy.context.view_layer.update()
    assert same_geometry()==geometry
    if wh[0]==1220:
        top=world_to_camera_view(s,cam,origin+Vector((0,0,22)))
        low=world_to_camera_view(s,cam,origin+Vector((0,0,0)))
        assert .04<low.y<top.y<.96,(list(low),list(top))
    s.render.filepath=str(out/(name+'.jpg'));bpy.ops.render.render(write_still=True)

(out/'validation.json').write_text(json.dumps({
    'fixture_bytes':len(raw),'fixture_triangles':tri,'fixture_count':4,
    'shaft_height_m':max(q.z for q in sv),'sample_basin_radius_m':basin_r,
    'minimum_fixture_clearance_m':min(clearance),'shaft_probe_height_m':targets,
    'comparison_geometry_unchanged':True,'runtime_lights':False,
},indent=2)+'\n')
eye=(-66,-16,1.70)
q=origin+Vector((0,0,9.7))
shot('nov24-obelisk-uplight-off',eye,q,(1220,1420),38,False)
shot('nov24-obelisk-uplight-on',eye,q,(1220,1420),38,True)
shot('nov24-obelisk-uplight-detail',(-44,-7.4,2.65),(-35.8,-1.55,1.42),(1280,910),38,True)

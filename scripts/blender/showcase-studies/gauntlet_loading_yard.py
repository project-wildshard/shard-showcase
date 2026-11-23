"""Build E11c C1 Loading Yard around the pinned Round 5 layout."""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

root = Path(__file__).resolve().parents[3]
L = json.loads((root/'project/layouts/wsc-scene-007-c1-loading.json').read_text())
X,Y,Z=L['origin_world_x_y_z']
out=output_directory()
s=bpy.context.scene
clear_scene()
pieces=defaultdict(lambda:([],[]))
rng=random.Random(128)

def local(x,z,y):return Vector((x-X,Z-z,y-Y))

def mat(name,c,rough=.7,metal=.0,emit=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    bs=m.node_tree.nodes['Principled BSDF']
    for k,v in {'Base Color':(*c,1),'Roughness':rough,'Metallic':metal,
                'Emission Color':(*c,1),'Emission Strength':emit}.items():
        bs.inputs[k].default_value=v
    return m

base=mat('Sand-dusted concrete',(.226,.179,.127))
plaza=[mat('Weathered aggregate '+str(i),c) for i,c in enumerate((
    (.27,.217,.164),(.243,.195,.147),(.282,.218,.158),
    (.306,.251,.189),(.240,.185,.137),(.291,.230,.174)))]
gap=mat('Join lines and blackened steel',(.067,.061,.053),.66,.30)
shell=mat('Slate blue retaining steel',(.092,.135,.146),.53,.58)
rib=mat('Worn pressed steel ribs',(.154,.196,.201),.55,.54)
rust=mat('Burnt orange portal frame',(.541,.175,.049),.48,.43)
ochre=mat('Faded loading stencil',(.79,.381,.042),.74)
lamp=mat('Warm ceramic lens',(.98,.592,.282),.4,.1,1.2)
mist=mat('Pale work lane edge',(.54,.49,.34))
soil=mat('Outer brown aggregate',(.16,.119,.082))

def poly(g,ma,verts,faces):
    v,f=pieces[(g,ma)]
    n=len(v)
    v.extend(local(*p) for p in verts)
    f.extend(tuple(n+i for i in ids) for ids in faces)

def box(g,ma,x,z,y,w,d,h,angle=0):
    co,si=math.cos(angle),math.sin(angle)
    p=[(x+co*i*w/2-si*j*d/2,z+si*i*w/2+co*j*d/2,y+k*h/2)
       for k in (-1,1) for j in (-1,1) for i in (-1,1)]
    poly(g,ma,p,((1,3,2,0),(6,7,5,4),(4,5,1,0),(3,7,6,2),(2,6,4,0),(5,7,3,1)))

def slab(g,ma,x1,x2,z1,z2,y1,y2):
    box(g,ma,(x1+x2)/2,(z1+z2)/2,(y1+y2)/2,x2-x1,z2-z1,y2-y1)

def ramp(g,x,z1,z2,w,h1,h2):
    a,b=x-w/2,x+w/2
    v=[(a,z1,-.2),(b,z1,-.2),(a,z2,-.2),(b,z2,-.2),
       (a,z1,h1),(b,z1,h1),(a,z2,h2),(b,z2,h2)]
    poly(g,base,v,((1,3,2,0),(6,7,5,4),(4,5,1,0),(3,7,6,2),(2,6,4,0),(5,7,3,1)))
    for k,d in enumerate((.22,.42,.62, .79,.90)):
        z=z1+d*(z2-z1); h=h1+d*(h2-h1)
        box(g,ochre if k!=1 else mist,x,z,h+.018,w*.78,.048,.010)
    for q in (-1,1):
        x2=x+q*(w/2-.10)
        poly(g,rust,[(x2-.09,z1,h1+.016),(x2+.09,z1,h1+.016),(x2+.09,z2,h2+.016),(x2-.09,z2,h2+.016)],
             [(3,2,1,0)])

slab('Floor datum',base,*L['floor_x0_x1_z0_z1'],-.56,0)
slab('Entry terrace datum',base,*L['entry_terrace'],-.52,L['entry_y'])
for ix in range(12):
    a,b=14+82*ix/12,14+82*(ix+1)/12
    for iz in range(6):
        c,d=150+34*iz/6,150+34*(iz+1)/6
        slab('Ground slab panels',rng.choice(plaza),a+.018,b-.018,c+.018,d-.018,-.02,.012)
    for c,d in ((142,145.9),(146,150)):
        slab('Entry terrace panels',rng.choice(plaza),a+.018,b-.018,c+.019,d-.019,2.98,3.012)
for a in L['ramp_center_x']:
    ramp('North descent ramps',a,*L['staged_ramp_front_back_width'],3,0)
for i in range(24):
    x=15.5+i*3.36
    if all(abs(x-r)>3.55 for r in L['ramp_center_x']):
        box('Terrace edge paint',ochre,x,149.76,3.03,2.9,.22,.021)
for x in (29.3,30.7,54.3,55.7,78.8,81.2):
    for k in range(8):
        z=159+k*3.10
        if abs(x-55)<1 and k in (0,1,5,6):continue
        box('Marshalling and G1 stripes',ochre if x<31 else mist,x,z,.026,.115,1.63,.022)
for x,z in ((55,160),(55,177),(24,178)):
    for a in (-2.26,2.26):
        box('Cargo stack paint',ochre,x+a,z,.025,.11,2.5,.022)
    for a in (-1.24,1.24):
        box('Cargo stack paint',ochre,x,z+a,.025,4.51,.11,.022)

# Field panels and ribs stop exactly at the opening edges. The visible paint
# and recesses are static; no gate or spawn state is implied.
def wall(g,x1,x2,z1,z2,y0=0,y1=5):
    slab(g,shell,x1,x2,z1,z2,y0,y1)
    slab(g,rib,x1-.11,x2+.11,z1-.11,z2+.11,y1-.20,y1-.026)
    slab(g,rust,x1-.073,x2+.073,z1-.073,z2+.073,y1-.459,y1-.309)
    vertical=z2-z1>x2-x1
    start,end=(z1,z2) if vertical else (x1,x2)
    n=max(1,round((end-start)/2.3))
    for i in range(n):
        a=start+(i+.5)*(end-start)/n
        x,z=((x1+x2)/2,a) if vertical else (a,(z1+z2)/2)
        box(g,rib,x,z,(y0+y1)/2,1.02 if vertical else .19,.19 if vertical else 1.02,y1-y0-.39)
        box(g,gap,x,z,y0+.31,1.06 if vertical else .64,.64 if vertical else 1.06,.61)
        if i%3==0:
            box(g,ochre,x,z,y1-.74,1.031 if vertical else .20,.20 if vertical else 1.031,.21)

wall('North terrace wall',14,58,142,142.63,3,5)
wall('North terrace wall',66,96,142,142.63,3,5)
for side,x in (('West',14.34),('East',95.66)):
    for a,b in ((142,164.24),(169.76,184)):
        wall(side+' retaining run',x-.34,x+.34,a,b,0,5)
wall('South wall around G1',14,25,183.36,184)
wall('South wall around G1',35,96,183.36,184)

for key,(x,z) in L['door_x_z'].items():
    g=key+' recessed dock'
    a,b,c,d=L['door_closets'][key]
    ox=a if key=='D1' else b
    dx=1 if key=='D1' else -1
    slab(g,plaza[2],a,b,c,d,-.5,0)
    slab(g,shell,a,b,c,c+.38,0,4.8)
    slab(g,shell,a,b,d-.38,d,0,4.8)
    box(g,gap,ox+dx*.18,z,2.18,.36,11.64,4.36)
    for i in range(-5,6):
        box(g,rib,ox+dx*.40,z+i*.95,2.13,.096,.047,3.73)
    for off in (-2.63,2.63):
        box(g,rust,x,z+off,1.90,1.38,.41,3.80)
        box(g,shell,x+dx*.74,z+off,2.51,.16,.32,.75)
        box(g,lamp,x+dx*.835,z+off,2.64,.055,.19,.35)
    box(g,shell,x,z,4.10,1.57,5.84,.71)
    box(g,rust,x+dx*.77,z,4.09,.11,5.70,.33)
    for i in range(5):
        box(g,ochre,x+dx*.48,z+(i-2)*.83,.021,.72,.25,.015)

# Reinforce the loading bays with recessed shutter detail, exterior signage
# housings and narrow grated drains. Keep the route bodies untouched.
for key,(x,z) in L['door_x_z'].items():
    g=key+' cargo hardware'
    sign=1 if key=='D1' else -1
    box(g,gap,x+sign*.46,z,.025,.50,4.36,.025)
    for i in range(10):
        box(g,rib,x+sign*.46,z+(i-4.5)*.43,.045,.47,.065,.028)
    for off in (-3.66,3.66):
        box(g,shell,x+sign*.74,z+off,1.33,.27,.81,1.74)
        box(g,rust,x+sign*.89,z+off,1.43,.10,.55,.88)
        for i in range(3):
            box(g,gap,x+sign*.951,z+off,1.28+i*.21,.039,.42,.057)
    box(g,gap,x+sign*.83,z,4.21,.071,2.00,.31)
    for zoff in (-1.92,1.92):
        box(g,lamp,x+sign*.83,z+zoff,4.16,.095,.47,.15)
for x in (44,54,64,74,84):
    # Flush drains on the service edge, not additional cover.
    box('South drainage line',gap,x,181.95,.012,4.96,.32,.024)
    for i in range(12):
        box('South drainage line',rib,x+(i-5.5)*.40,181.95,.021,.087,.30,.019)

ramp('G1 grade',30,184,190,10,0,L['c2_landing_height'])
for x in (25.34,34.66):
    wall('G1 side parapet',x-.34,x+.34,184.0,190,0,4.1)
for x in (25.61,34.39):
    box('G1 transit header',rust,x,184.25,2.25,.7,1.19,4.50)
    box('G1 transit header',lamp,x,183.61,3.53,.19,.066,.58)
box('G1 transit header',shell,30,184.25,4.54,10.0,1.40,.58)
box('G1 transit header',rust,30,183.53,4.54,9.4,.12,.26)
for i in range(9):
    box('G1 transit header',lamp if i in (0,8) else gap,26+i,183.45,4.54,.31,.024,.11)

for kind,x,z in L['cover']:
    if kind=='half':
        g='Marshalling half walls'
        box(g,base,x,z,.49,4.5,.93,.98)
        box(g,rib,x,z,1.04,4.61,1.01,.12)
        for d in (-1.89,1.89):
            box(g,rust,x+d,z,.56,.32,1.02,.74)
    elif kind=='pillar':
        g='Six-meter service pier'
        box(g,base,x,z,.20,2.34,2.34,.40)
        box(g,shell,x,z,2.96,1.72,1.72,5.52)
        box(g,rib,x,z,5.84,2.06,2.06,.32)
        for dx in (-.82,.82):
            box(g,rust,x+dx,z,.64,.17,1.81,.79)
            box(g,rib,x+dx,z,3.37,.10,1.83,.24)

# Repeated scene parts are batched by region/material, not separate trim nodes.
parts=[]
for (n,ma),(verts,faces) in sorted(pieces.items(),key=lambda row:(row[0][0],row[0][1].name)):
    me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();me.materials.append(ma)
    ob=bpy.data.objects.new(n,me);s.collection.objects.link(ob)
    parts.append(ob)

path=out/'wsc-scene-007-c1-loading-yard.glb'
export(parts,path)
raw=path.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tri=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])
assert len(raw)<600000 and tri<10000, (len(raw),tri)
assert not any(doc.get(k) for k in ('images','animations','skins'))
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(path))
structure=[o for o in s.objects if o.type=='MESH']
bpy.context.view_layer.update()

def bvh(objs):
    vertices,polygons=[],[]
    for o in objs:
        off=len(vertices)
        vertices.extend(o.matrix_world@v.co for v in o.data.vertices)
        polygons.extend(tuple(off+i for i in f.vertices) for f in o.data.polygons)
    return BVHTree.FromPolygons(vertices,polygons)

static=bvh(structure)
def elevation(x,z,bvh_tree=static):
    hit=bvh_tree.ray_cast(local(x,z,12),(0,0,-1),20)[0]
    assert hit is not None,(x,z)
    return hit.z

assert abs(elevation(62,146)-3)<.017
for x in L['ramp_center_x']:
    assert all(abs(elevation(x,z)-v)<.032 for z,v in ((150.1,2.9647),(154.25,1.5),(158.4,.0353)))
assert abs(elevation(30,189.9)-2.4583)<.023
assert abs(elevation(86,158)-6)<.001
for x,z in ((34,166),(76,172)):assert abs(elevation(x,z)-1.10)<.002
for x,z,dx in ((15.2,167,-1),(94.8,167,1)):
    for dz in (-1.6,0,1.6):
        assert static.ray_cast(local(x,z+dz,1.5),(dx,0,0),3)[0] is None
for x in (27,30,33):
    assert static.ray_cast(local(x,181,2.2),(0,-1,0),4.25)[0] is None

# Recoverably stage the original crate via component instances, not a copied
# vertex stream embedded in the architecture export.
crate=root/'public/assets/wildshard-art/haul-crate.glb'
assert hashlib.sha256(crate.read_bytes()).hexdigest()==L['crate_sha256']
present=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(crate))
bpy.context.view_layer.update()
extras=set(s.objects)-present
files=[(o.data,o.matrix_world.copy()) for o in sorted(extras,key=lambda o:o.name) if o.type=='MESH']
vv=[m@v.co for data,m in files for v in data.vertices]
assert files and vv
lower=[min(v[i] for v in vv) for i in range(3)]
upper=[max(v[i] for v in vv) for i in range(3)]
T=Matrix.Translation((-((lower[0]+upper[0])/2),-((lower[1]+upper[1])/2),-lower[2]))
Q=Matrix.Diagonal((1.28/(upper[0]-lower[0]),1.40/(upper[1]-lower[1]),1.2/(upper[2]-lower[2]),1))
for o in extras:bpy.data.objects.remove(o,do_unlink=True)
for kind,x,z in L['cover']:
    if kind!='crates':continue
    for k,(dx,dz,h) in enumerate(((-1.4,0,0),(0,0,0),(1.4,0,0),(-1.4,0,1.2),(1.4,0,1.2))):
        for mesh,base_t in files:
            o=bpy.data.objects.new(f'Linked cargo {x} / {z} / {k}',mesh);s.collection.objects.link(o)
            o.matrix_world=Matrix.Translation(local(x+dx,z+dz,h+.013))@Q@T@base_t

(out/'validation.json').write_text(json.dumps({
    'scope':'static art export plus independently linked cargo preview',
    'bytes':len(raw),'triangles':tri,'mesh_count':len(doc['meshes']),
    'native':False,'entry_height_m':elevation(62,146),
    'ramp_midpoints_m':[elevation(x,154.25) for x in L['ramp_center_x']],
    'g1_top_near_end_m':elevation(30,189.9),
    'measured_pier_m':elevation(86,158),'crate_placements':15,
    'd1_d2_clear_rays':6,'g1_clear_rays':3,
},indent=2)+'\n')

# Lighting, stencil typography and horizon belong only to the proof renders.
def aim(o,target):o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
def obj(n,m):
    o=bpy.data.objects.new(n,m);s.collection.objects.link(o);return o

bpy.ops.mesh.primitive_plane_add(size=540,location=(0,0,-.62))
bpy.context.object.data.materials.append(soil)
for n,x,z,h,rot in (('D1',14.89,167,4.21,math.pi/2),('D2',95.11,167,4.21,-math.pi/2),('G1',30,183.41,4.54,math.pi)):
    c=bpy.data.curves.new(n,'FONT');c.body=n;c.align_x='CENTER';c.align_y='CENTER';c.size=.31;c.materials.append(mist)
    ob=obj(n,c);ob.location=local(x,z,h);ob.rotation_euler=(math.pi/2,0,rot)
world=bpy.data.worlds.new('Eastern desert rim')
world.use_nodes=True
n=world.node_tree.nodes;sky=n.new('ShaderNodeTexSky')
sky.sky_type='NISHITA';sky.sun_elevation=.51;sky.sun_rotation=1.53;sky.sun_size=.034;sky.sun_intensity=.70
world.node_tree.links.new(sky.outputs['Color'],n['Background'].inputs[0]);n['Background'].inputs[1].default_value=.20
s.world=world
camd=bpy.data.cameras.new('C1 review');cam=obj('C1 review',camd);s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=90
def render(n,eye,where,wh,ortho=None,lens=30):
    cam.location=local(*eye);aim(cam,local(*where))
    camd.type='ORTHO' if ortho else 'PERSP'
    if ortho:camd.ortho_scale=ortho
    camd.lens=lens
    s.render.resolution_x,s.render.resolution_y=wh
    s.render.filepath=str(out/(n+'.jpg'))
    bpy.ops.render.render(write_still=True)
render('nov23-c1-loading-overlook',(114,115,86),(55,165,1.9),(1470,1020),116)
render('nov23-c1-loading-terrace',(73,147,5.15),(36,175,1.9),(1390,900),None,25)
render('nov23-c1-loading-dock',(29,174,1.73),(14,166.7,1.95),(1200,870),None,35)

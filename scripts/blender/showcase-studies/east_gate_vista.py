"""W9b vista 6: grounded bench scan and two seated East framing renders."""
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys

import bpy
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,output_directory

out=output_directory()
clear_scene()
s=bpy.context.scene
root=Path(__file__).resolve().parents[3]
assets=root/'public/assets/wildshard-art'
pins=json.loads((root/'project/layouts/w0a-east-gate-boundary-donors.json').read_text())
pins['bench']={'file':'wsc-prop-044-lookout-bench.glb','sha256':'9109111c13a27c81981839237b9f1880c9e964930f5888e24c1054ac819bfeb1'}
pins.update({
    'shed':{'file':'wsc-prop-054-yard-shed.glb','sha256':'fd3f5e9c0964375df9e54cf342fa9707ce2fba4e8d7df763ab258c33c195d291'},
    'tank':{'file':'wsc-prop-041-industrial-tank.glb','sha256':'d23b541afae7415a170f00782047fd1761558df7148fd396e2495d7544e5feed'},
    'container':{'file':'wsc-prop-058-shipping-container.glb','sha256':'8bd1c2bca075256315a8bf5a76b5da489b3e42fca0def63d06088031695232af'},
    'crate':{'file':'haul-crate.glb','sha256':'d7a5f8fcb2b835d0c0c77c3051ebd950ed449dc2c563e10779fdc5f01cc6bb44'},
})
L=json.loads((root/'project/layouts/w9b-east-gate-vista.json').read_text())
cached={}
def load(key):
    if key in cached:return cached[key]
    row=pins[key];p=assets/row['file']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.view_layer.update()
    new=sorted(set(s.objects)-before,key=lambda o:o.name)
    cached[key]=[(o.name,o.data,o.matrix_world.copy()) for o in new if o.type=='MESH']
    for o in new:bpy.data.objects.remove(o,do_unlink=True)
    assert cached[key],key
    return cached[key]

def place(key,n,t):
    seq=[]
    for name,mesh,m in load(key):
        o=bpy.data.objects.new(n+' | '+name,mesh);s.collection.objects.link(o);o.matrix_world=t@m;seq.append(o)
    bpy.context.view_layer.update()
    return seq

def transform(p,depth,width,height):
    # Match the tracked November East Gate boundary transform exactly.
    return Matrix(((0,-depth,0,p[0]),(width,0,0,p[1]),(0,0,height,p[2]),(0,0,0,1)))
span=place('span','East span',transform((-8,0,6.245),.67,1.78,.236))
towers=[]
for sign in (-1,1):
    towers+=place('tower','East tower',transform((-8,sign*7.84,0),.65,.94,7.19/5.275))

def tree(objs):
    verts,faces=[],[]
    for o in objs:
        off=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
        faces.extend(tuple(off+i for i in q.vertices) for q in o.data.polygons)
    return BVHTree.FromPolygons(verts,faces)

all_gate=tree(span+towers)
# Upper horizontal surfaces only, with full geometry in a separate obstacle BVH.
roof=tree([o for o in span if 'head datum' in o.name])
assert roof
yaw=math.radians(130)
rotation=Matrix.Rotation(yaw,3,'Z')
facing=rotation@Vector((0,-1,0))
centers=[]
for x in (-.7205,.7205):
    for y in (-.2485,.2485):
        centers.append(Vector((x,y,0)))
pad=[[rotation@(p+Vector((dx,dy,0))) for dx,dy in ((0,0),(-.075,-.051),(-.075,.051),(.075,-.051),(.075,.051))] for p in centers]

def rays(q,offsets):
    hits=[]
    for b in offsets:
        h,n,_,_=roof.ray_cast(q+b,(0,0,-1),10)
        if h is None or n.z<.92:return None
        g,gn,_,_=all_gate.ray_cast(q+b,(0,0,-1),10)
        if g is None or gn.z<.92 or abs(g.z-h.z)>.014:return None
        hits.append(g.z)
    return hits if max(hits)-min(hits)<.015 else None

arch=Vector((-10,10,9))
h,_,_,_=roof.ray_cast(arch+Vector((0,0,4)),(0,0,-1),12)
assert h is None
candidates=[]
for i in range(21):
    for j in range(113):
        q=Vector((-8.99+.099*i,-5.60+.10*j,12))
        heights=rays(q,[x for p in pad for x in p])
        if not heights or max(heights)-min(heights)>.003:continue
        z=sum(heights)/len(heights)
        floor=Vector((q.x,q.y,z))
        # Test full bench envelope separately from contact feet; bench back
        # cannot sit on a decorative raised roof edge or a corner tower.
        lateral=[rotation@Vector((x,y,0)) for x in (-.96,-.49,0,.49,.96) for y in (-.36,0,.36)]
        if not rays(q,lateral):continue
        eye=floor+.18*facing+Vector((0,0,1.43))
        checks={}
        for key,(x,z0) in L['band_centers_world_xz'].items():
            t=Vector((x,-z0,L['illustrative_target_height_m'][key]))
            d=t-eye
            checks[key]=all_gate.ray_cast(eye,d.normalized(),d.length)[0] is None
        candidates.append((sum(checks.values()),-(Vector((q.x,q.y,0))-Vector((arch.x,arch.y,0))).length,floor,heights,checks))
assert candidates,'No roof supports all pads plus envelope with this facing'
score,_,seat,support,checks=max(candidates,key=lambda row:row[:2])
eye=seat+.18*facing+Vector((0,0,1.43))
bench=place('bench','Exact lookout bench',Matrix.Translation(seat)@rotation.to_4x4())
bounds=lambda d:max(d)-min(d)

def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def obj(n,d):o=bpy.data.objects.new(n,d);s.collection.objects.link(o);return o

def mat(name,color,rough=.72):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough
    return m

ground=mat('Study ground',(.213,.165,.116))
road=mat('Study road',(.117,.114,.104))
tone=[mat(n,c) for n,c in [
    ('Red-brown foothills',(.22,.142,.102)),('Saw grass hills',(.158,.167,.122)),
    ('High slate',(.131,.146,.154)),('Dun rock',(.237,.198,.157)),
]]
rng=random.Random(96)

def cube(n,p,wh,ma,rz=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.scale=wh;o.rotation_euler.z=rz;o.data.materials.append(ma);return o

cube('Unmapped illustration ground',(95,42,-.35),(490,520,.64),ground)
cube('East approach context',(113,0,-.022),(240,14,.04),road)
# Industrial seam remains at its verified atlas line; this uses existing
# design metal bays as foreground context only, not a new boundary model.
for sign in (-1,1):
    for j in range(14):
        y=sign*(8.85+j*3.595)
        place('bay','Seam context',Matrix.Translation((7.5,y,0))@Matrix.Rotation(math.pi/2,4,'Z'))
# A staging apron uses unchanged catalogue models, not reconstructed map placements.
for k,x,y,z,a in (
    ('shed',24,31,0,-10),('tank',37,49,0,0),('tank',41,51,0,0),('tank',42,46,0,18),
    ('container',29,15,0,-5),('container',29,19,0,5),('container',47,22,0,-17),
    ('crate',18,20,0,8),('crate',19.2,20.7,0,28),('crate',21,20.3,0,14),('crate',20.1,19.2,0,43),
    ('crate',28,34,0,9),('crate',29.25,34.3,0,-18),
):
    place(k,'Illustrative East apron',Matrix.Translation((x,y,z))@Matrix.Rotation(math.radians(a),4,'Z'))
for width,depth,x,y in [(17,14,29,19),(15,13.4,26,33),(19,16,41,48.5)]:
    cube('Preview apron',(x,y,-.02),(width,depth,.07),road)
for j in range(28):
    cube('Tarmac divider preview',(7+j*7,0,-.001),(2.37,.13,.012),tone[3])
# Each group is explicitly a silhouette/staging proxy, not live terrain.
for i,(key,(x,z0)) in enumerate(L['band_centers_world_xz'].items()):
    y=-z0
    for j in range(8):
        ux=x+(j-3.5)*8.9+rng.uniform(-3,3)
        uy=y+rng.uniform(-15,16)
        hh=rng.uniform(3,8)*(1+i*.11)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(ux,uy,-1.3))
        o=bpy.context.object;o.name=key+' terrain silhouette';o.scale=(rng.uniform(8,18),rng.uniform(9,20),hh)
        o.data.materials.append(tone[i])
    for j in range(6):
        ux=x+(j-2.5)*4.2;uy=y+math.sin(j*2.5)*4.7
        hh=2.3+((j*3+i)%7)*.54
        cube(key+' yard mass',(ux,uy,hh/2),(3.2,4.3,hh),tone[i])
        if j%3==1:cube(key+' raised ridge',(ux,uy,hh+.22),(3.34,4.42,.44),tone[(i+2)%4])
    h=L['illustrative_target_height_m'][key]
    # Distinct silhouettes expose framing and bearings without suggesting a
    # recovered native placement. Distant marker volumes are non-game props.
    for dx,dy,w,dep,k in {
        'B1':[(0,0,4,5,1),(-4,2,4,5,.60),(4,-1,3,4,.68)],
        'B2':[(0,0,5,4,1),(-2,-6,7,4,.43),(4,3,3,4,.76)],
        'B3':[(0,0,5,5,1),(-4,0,3,4,.68),(4,0,3,4,.79)],
        'B4':[(0,0,9,5,.76),(0,0,5,3,1),(-6,4,4,5,.57)],
     }[key]:
        cube(key+' illustrative marker mass',(x+dx,y+dy,h*k/2),(w,dep,h*k),tone[(i+2)%4])
for i in range(27):
    x=rng.uniform(105,360);y=rng.uniform(-30,335)
    if x<243 and y<242:continue
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,y,-4))
    o=bpy.context.object;o.name='Off-map backdrop only';o.scale=(rng.uniform(11,48),rng.uniform(17,58),rng.uniform(7,25))
    o.data.materials.append(tone[rng.choice((1,2,3))])

d=bpy.data.cameras.new('Vista 6 review');cam=obj('Vista 6 review',d);s.camera=cam
w=bpy.data.worlds.new('East morning');w.use_nodes=True
n=w.node_tree.nodes;sky=n.new('ShaderNodeTexSky')
sky.sky_type='NISHITA';sky.sun_elevation=.31;sky.sun_rotation=2.50;sky.sun_size=.035;sky.sun_intensity=.78
w.node_tree.links.new(sky.outputs['Color'],n['Background'].inputs[0]);n['Background'].inputs[1].default_value=.19
s.world=w
s.render.engine='CYCLES';s.cycles.samples=36;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=91

bearings={k:math.degrees(math.atan2(-z-eye.y,x-eye.x)) for k,(x,z) in L['band_centers_world_xz'].items()}
wide,high=804,1748
v=math.radians(80)
f=2*math.atan(math.tan(v/2)*wide/high)
yawset={'north':(bearings['B2']+bearings['B3'])/2,'east':(bearings['B1']+bearings['B4'])/2}
for k,ks in {'north':('B2','B3'),'east':('B1','B4')}.items():
    assert all(abs(yawset[k]-bearings[j])<math.degrees(f)/2-4 for j in ks)
ground_tests={}
for key,(x,z0) in L['band_centers_world_xz'].items():
    dr=Vector((x,-z0,0))-eye
    hit=all_gate.ray_cast(eye,dr.normalized(),dr.length)[0]
    ground_tests[key]=hit is None
metrics={
    'archive_world_xyz':[-10,9,-10],
    'tested_seat_world_xyz':[seat.x,seat.z,-seat.y],
    'seat_horizontal_shift_m':math.hypot(seat.x-arch.x,seat.y-arch.y),
    'pad_support_m':[support[i:i+5] for i in range(0,20,5)],
    'pad_height_spread_m':bounds(support),'seat_footprint_candidates':len(candidates),
    'eye_world_xyz':[eye.x,eye.z,-eye.y],
    'bearing_degrees':bearings,'bearing_span_degrees':bounds(list(bearings.values())),
    'vertical_fov_degrees':80,'horizontal_fov_degrees':math.degrees(f),
    'camera_pitch_degrees':math.degrees(math.atan(-.255)),
    'camera_yaws_degrees':yawset,'raised_marker_clear_of_gate_mesh':checks,
    'ground_centers_clear_of_gate_mesh':ground_tests,'terrain':'art-only silhouettes',
}
d.sensor_fit='VERTICAL';d.lens=d.sensor_height/(2*math.tan(v/2))
s.render.resolution_x,s.render.resolution_y=wide,high
metrics['projected_markers']={}
for k,a in yawset.items():
    aa=math.radians(a)
    cam.location=eye
    aim(cam,eye+Vector((math.cos(aa),math.sin(aa),-.255)))
    bpy.context.view_layer.update()
    ks=('B2','B3') if k=='north' else ('B1','B4')
    metrics['projected_markers'][k]={}
    for bid in ks:
        x,z0=L['band_centers_world_xz'][bid]
        q=world_to_camera_view(s,cam,Vector((x,-z0,L['illustrative_target_height_m'][bid])))
        assert .09<q.x<.91 and .11<q.y<.88 and q.z>0,(k,bid,list(q))
        metrics['projected_markers'][k][bid]=[q.x,q.y]
    if not os.environ.get('WILDSHARD_VALIDATE_ONLY'):
        s.render.filepath=str(out/('nov23-east-vista-'+k+'.jpg'))
        bpy.ops.render.render(write_still=True)
(out/'validation.json').write_text(json.dumps(metrics,indent=2)+'\n')
if not os.environ.get('WILDSHARD_VALIDATE_ONLY'):
    # Third shot establishes seat and feet on original roof with no native rig.
    d.sensor_fit='HORIZONTAL';d.lens=36
    cam.location=seat-3.4*facing+Vector((0,-1.5,2.2))
    aim(cam,seat+.28*facing+Vector((0,0,.47)))
    s.render.resolution_x,s.render.resolution_y=1200,880
    s.render.filepath=str(out/'nov23-east-vista-seat.jpg')
    bpy.ops.render.render(write_still=True)

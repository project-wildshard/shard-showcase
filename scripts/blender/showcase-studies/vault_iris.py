"""WSC-ARCH-007 optional active iris, with no gameplay or donor modification."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,output_directory

root=Path(__file__).resolve().parents[3]
out=output_directory()
donor=root/'public/assets/wildshard-art/wsc-arch-007-training-vault-portal.glb'
assert hashlib.sha256(donor.read_bytes()).hexdigest()=='41ef3e827971d3c80d4a89287b865a0934002ca50f160997defafe9c80f8e714'
s=bpy.context.scene
clear_scene()
FPS=24
LAST=72
s.render.fps=FPS
s.frame_start=0
s.frame_end=LAST
CZ=1.75
RX,RZ=1.06,1.47
dst=out/'wsc-arch-007-vault-iris.glb'

def material(name,color,emission=0,alpha=1,rough=.5):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,alpha)
    bs=m.node_tree.nodes['Principled BSDF']
    for k,v in {'Base Color':(*color,1),'Emission Color':(*color,1),'Emission Strength':emission,
                'Alpha':alpha,'Roughness':rough}.items():bs.inputs[k].default_value=v
    if alpha!=1:m.surface_render_method='BLENDED'
    return m

palette=[
    material('Deep edge tide',(.025,.355,.435),.97,.47),
    material('Mint curl',(.04,.76,.84),1.30,.72),
    material('Cold crest',(.48,.93,.95),1.60,.78),
    material('Soft edge halo',(.025,.31,.61),.66,.20),
]
faces=[]
slots=[]
params=[]
# Each strip tapers at both ends. The phases move around the oval in
# aperture-normalized coordinates, where radial distances remain bounded.
for j, (start, sweep, inrad, outrad, width, layer, n) in enumerate((
    (.10,2.23,.53,.93,.059,0,25),(2.18,2.18,.58,.91,.052,0,25),
    (4.26,2.26,.54,.95,.059,0,25),(.61,1.51,.61,.90,.033,1,19),
    (2.75,1.42,.61,.88,.032,1,19),(4.83,1.65,.67,.93,.033,1,19),
    (1.02,.73,.71,.87,.015,2,13),(3.21,.66,.74,.87,.015,2,13),
    (5.32,.64,.74,.90,.014,2,13),(.82,.77,.51,.66,.015,1,12),
    (3.97,.75,.52,.66,.014,1,12),
    (.24,2.57,.915,.939,.021,3,26),(2.49,2.72,.918,.945,.020,3,26),
    (4.62,2.42,.917,.940,.022,3,26),(.15,1.24,.78,.899,.006,2,16),
    (2.24,1.24,.79,.908,.007,2,16),(4.28,1.28,.80,.916,.006,2,16),
    (.25,.34,.57,.61,.0065,2,6),(1.57,.28,.72,.79,.007,2,6),
    (2.61,.37,.58,.60,.006,2,6),(3.64,.32,.64,.71,.006,2,6),
    (4.81,.35,.58,.63,.007,2,6),(5.73,.21,.67,.69,.006,2,6),
)):
    first=len(params)
    for i in range(n+1):
        u=i/n
        for edge in (-1,1):
            params.append((j,start,sweep,inrad,outrad,width,layer,u,edge))
    for p in range(n):
        i=first+2*p
        faces.append((i,i+1,i+3,i+2));slots.append(layer)

def vertex(row,phase):
    j,start,sweep,inrad,outrad,w,layer,u,edge=row
    a=start+phase+u*sweep
    taper=.06+.94*math.sin(math.pi*u)**.63
    r=inrad+u*(outrad-inrad)+edge*w*taper + .007*math.sin(phase*2+a*3+j)
    return (RX*r*math.cos(a),-.131-.03*layer+.038*math.sin(a*1.7+u*2.1+j),CZ+RZ*r*math.sin(a))

mesh=bpy.data.meshes.new('Swirling iris strips')
mesh.from_pydata([vertex(p,0) for p in params],[],faces)
for m in palette:mesh.materials.append(m)
for f,i in zip(mesh.polygons,slots):f.material_index=i
mesh.update()
o=bpy.data.objects.new('Vault iris overlay',mesh);s.collection.objects.link(o)
o.shape_key_add(name='Iris neutral')
# Twelve equidistant poses: only two neighboring weights are active;
# interpolate on the chord, without the large midarc collapse of 4 poses.
N=12
keys=[]
for k in range(N):
    q=o.shape_key_add(name='Flow phase '+str(k+1))
    for i,r in enumerate(params):q.data[i].co=vertex(r,-math.tau*k/N)
    keys.append(q)
for j in range(N+1):
    for i,k in enumerate(keys):
        k.value=float(i==j%N)
        k.keyframe_insert(data_path='value',frame=(LAST//N)*j)
action=o.data.shape_keys.animation_data.action
action.name='Vault_Iris_Loop_3s'
for fc in action.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(0)
bpy.ops.export_scene.gltf(filepath=str(dst),export_format='GLB',
    export_animations=True,export_animation_mode='ACTIONS',export_frame_step=2,
    export_morph_normal=False,export_normals=False)

raw=dst.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n])
assert len(doc['nodes'])==len(doc['meshes'])==len(doc['animations'])==1
assert not any(doc.get(k) for k in ('images','skins','extensionsRequired'))
prims=doc['meshes'][0]['primitives']
assert len(prims)==4 and all(len(p['targets'])==N for p in prims)
assert all(m.get('alphaMode')=='BLEND' for m in doc['materials'])
tri=sum(doc['accessors'][p['indices']]['count']//3 for p in prims)
assert len(raw)<175000 and tri<800,(len(raw),tri)
A=doc['animations'][0]
ch=A['channels'][0];assert len(A['channels'])==1 and ch['target']['path']=='weights'
ac=doc['accessors'][A['samplers'][ch['sampler']]['input']]
assert ac['min']==[0] and ac['max']==[3]

clear_scene()
bpy.ops.import_scene.gltf(filepath=str(donor))
frame=[o for o in s.objects if o.type=='MESH']
assert len(frame)==3
def tree(objs):
    vs,fs=[],[]
    for ob in objs:
        n=len(vs)
        vs.extend(ob.matrix_world@v.co for v in ob.data.vertices)
        fs.extend(tuple(n+i for i in f.vertices) for f in ob.data.polygons)
    return BVHTree.FromPolygons(vs,fs)
g=tree(frame)
bpy.ops.import_scene.gltf(filepath=str(dst))
fx=s.objects['Vault iris overlay']

def evaluate(f):
    s.frame_set(f)
    bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    ob=fx.evaluated_get(graph)
    return [ob.matrix_world@v.co for v in ob.data.vertices]
start,end=evaluate(0),evaluate(LAST)
assert len(start)==len(end)==len(params) and max((a-b).length for a,b in zip(start,end))<.0002
assert max((a-b).length for a,b in zip(evaluate(12),evaluate(40)))>.9
vcount=0
min_center=100.0
for f in range(0,LAST+1,3):
    for p in evaluate(f):
        min_center=min(min_center,math.hypot(p.x/RX,(p.z-CZ)/RZ))
        assert g.ray_cast((p.x,-2,p.z),(0,1,0),4)[0] is None,(f,list(p))
        vcount+=1
assert min_center>.46
(out/'validation.json').write_text(json.dumps({
    'bytes':len(raw),'triangles':tri,'nodes':len(doc['nodes']),'duration_s':3,
    'morph_poses':N,'shape_rays_clear':vcount,'perspective_free_core_normalized_radius':min_center,
    'first_and_last_pose_match':True,'native_portal':False},indent=2)+'\n')

def aim(o,q):o.rotation_euler=(Vector(q)-o.location).to_track_quat('-Z','Y').to_euler()
def place(n,d):
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);return o
def area(n,p,target,watts,col,w):
    d=bpy.data.lights.new(n,'AREA');d.energy=watts;d.color=col;d.shape='DISK';d.size=w
    o=place(n,d);o.location=p;aim(o,target);return o
def cube(n,p,wh,ma):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.scale=wh;o.data.materials.append(ma);return o

base=material('Dark granite',(.068,.079,.085),0,1,.73)
stone=material('Concrete apron',(.169,.181,.166),0,1,.82)
bronze=material('Oxidized trim',(.132,.091,.043),0,1,.55)
cube('Stage stone',(0,0,-.15),(100,100,.3),base)
for row in range(7):
    for col in range(-5,6):
        cube('Stage apron paver',((col+.5*(row%2))*.7,-.2-row*.38,-.003),(.68,.363,.020),stone)
cube('Stage wall behind gate',(0,3.4,2.28),(13,.25,4.56),base)
for k in (-1,1):
    cube('Rear stage recess flank',(k*2.6,3.245,1.69),(1.1,.09,3.36),stone)
    cube('Rear stage dark rib',(k*.91,3.243,1.64),(.07,.095,3.28),bronze)
for x in (-3.4,3.4):
    cube('Stage marker base',(x,.22,.11),(.97,.95,.22),base)
    cube('Stage marker',(x,.18,.85),(.61,.61,1.68),bronze)
    cube('Stage marker cap',(x,.18,1.72),(.76,.75,.17),stone)
s.world=bpy.data.worlds.new('Vault blue-hour ambient')
s.world.color=(.077,.106,.16)
area('Warm light',(-5,-3.5,6),(0,0,2),450,(1,.71,.43),3.4)
area('Weak blue light',(3.7,-4,4.5),(0,0,1.9),215,(.53,.75,1),3.9)
area('Warm rim',(-1,3.5,4.8),(0,0,2),345,(1,.61,.32),2.8)
aura=area('Preview-only turquoise bounce',(0,.2,1.84),(0,-3,1.5),58,(.09,.77,1),1.6)

cam=place('Vault review',bpy.data.cameras.new('Vault review'));s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=36;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=91
def shot(name,frame,active,eye,target,wh,lens):
    s.frame_set(frame)
    fx.hide_render=not active
    aura.hide_render=not active
    cam.location=eye;aim(cam,target);cam.data.lens=lens
    s.render.resolution_x,s.render.resolution_y=wh
    s.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)

if os.environ.get('WSC_VAULT_IRIS_CLIP')=='1':
    # Silent art review clip from GLB reimport, not live renderer capture.
    s.cycles.samples=12
    s.render.image_settings.file_format='PNG'
    d=out/'clip';d.mkdir(exist_ok=True)
    cam.location=(.2,-9.4,2.47);aim(cam,(0,0,1.92));cam.data.lens=49
    s.render.resolution_x,s.render.resolution_y=576,582
    for i in range(48):
        f=i*1.5
        s.frame_set(int(f),subframe=f%1)
        s.render.filepath=str(d/f'{i:03}.png')
        bpy.ops.render.render(write_still=True)
else:
    shot('nov24-vault-iris-off',0,False,(.2,-9.4,2.47),(0,0,1.92),(1050,1060),49)
    shot('nov24-vault-iris-on',12,True,(.2,-9.4,2.47),(0,0,1.92),(1050,1060),49)
    shot('nov24-vault-iris-oblique',43,True,(4.8,-8.7,3.06),(0,0,1.86),(1300,960),51)

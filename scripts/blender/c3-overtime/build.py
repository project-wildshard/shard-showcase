"""Foreman Overtime phase art, selectively reusing the exact C3 floor."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'showcase-studies'))
from common import clear_scene,export,output_directory

out=output_directory()
clear_scene()
S=bpy.context.scene
A=HERE.parents[2]/'public/assets/wildshard-art'
pins=[
    ('e11c-g2-c3-threshold.glb','777bed81fd7369c604faf6e666cd33d0c5c826c93e02d136a58e672ea2b5d101',Matrix.Translation((-36,-28,0))),
    ('c3-office-sector.glb','631f39353d7eed6d4bba196f71a30342f7a5aac1fb1d3579560807c8db971f31',Matrix.Rotation(math.pi/4,4,'Z')),
    ('e11c-c3-fitted-floor.glb','45d1b496abc771448ff93ee20b2a4f7d21d6431cf122c1010841b9aef0c4b926',Matrix.Identity(4)),
]

def load(path,transform):
    before=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects=sorted(set(S.objects)-before,key=lambda o:o.name)
    for o in objects:
        if o.parent not in objects:o.matrix_world=transform@o.matrix_world
    bpy.context.view_layer.update()
    return [o for o in objects if o.type=='MESH']

def bvh(objects):
    verts,faces=[],[]
    deps=bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        e=obj.evaluated_get(deps)
        m=e.to_mesh()
        offset=len(verts)
        verts.extend(e.matrix_world@v.co for v in m.vertices)
        faces.extend(tuple(offset+i for i in f.vertices) for f in m.polygons)
        e.to_mesh_clear()
    return BVHTree.FromPolygons(verts,faces)

donors=[]
for name,sha,T in pins:
    p=A/name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
    donors+=load(p,T)
base=bvh(donors)
W,D=7.6,2.8
V,F,C=[],[],[]
dark=(.032,.037,.041,1)
amber=(.83,.475,.085,1)
warm=(.39,.186,.050,1)
mid=(.24,.104,.040,1)

def face(points,z,col,noise=0):
    area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points,points[1:]+points[:1]))
    assert abs(area)>1e-8
    if area<0:points=list(reversed(points))
    start=len(V)
    for x,y in points:
        V.append((x,y,z))
        t=1+noise*math.sin(x*11.7+y*15.2)
        C.append((col[0]*t,col[1]*t,col[2]*t,1))
    F.append(tuple(range(start,len(V))))

def rectangle(x,y,a,b,z,color,noise=0):
    face([(x-a/2,y-b/2),(x+a/2,y-b/2),(x+a/2,y+b/2),(x-a/2,y+b/2)],z,color,noise)

# Dark floor-tape rails bracket transparent center so floor marks remain legible.
for side in (-1,1):
    y=side*(D/2-.226)
    rectangle(0,y,W,.452,.004,dark,.15)
    for i in range(11):
        x=-3.67+i*.64
        face([(x-.10,y-.157),(x+.18,y-.157),(x+.40,y+.157),(x+.12,y+.157)],.006,amber,.17)
    # Subdued broken lane marks within the zone to avoid a bright solid fill.
    for i in range(7):
        x=-2.9+i*.96
        rectangle(x,side*.27,.63,.038,.004,warm if i%2 else mid,.12)
for side in (-1,1):
    x=side*(W/2-.108)
    rectangle(x,0,.216,D-.902,.004,dark,.15)
    rectangle(x,0,.062,D-1.08,.006,amber,.11)
    for sy in (-1,1):
        # Inward chevrons at both short ends, independent of hue.
        y=sy*.41
        face([(x-side*.20,y), (x-side*.38,y-.20),(x-side*.50,y-.20),
              (x-side*.33,y),(x-side*.50,y+.20),(x-side*.38,y+.20)],.006,amber,.11)
d=bpy.data.meshes.new('Overtime tape and boundary')
d.from_pydata(V,[],F);d.update()
attr=d.color_attributes.new(name='Baked mineral colors',type='FLOAT_COLOR',domain='POINT')
for c,v in zip(attr.data,C):c.color=v
mat=bpy.data.materials.new('Matte hazard tape');mat.use_nodes=True
bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.92
VC=mat.node_tree.nodes.new('ShaderNodeVertexColor');VC.layer_name=attr.name
mat.node_tree.links.new(VC.outputs['Color'],bs.inputs['Base Color'])
d.materials.append(mat)
o=bpy.data.objects.new(d.name,d);S.collection.objects.link(o)
file=out/'e11d-c3-overtime-tape.glb'
export([o],file)
bpy.data.objects.remove(o,do_unlink=True)
raw=file.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
g=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert not any(k in g for k in ('images','animations','skins','cameras'))
assert len(g['meshes'])==len(g['meshes'][0]['primitives'])==1
tris=g['accessors'][g['meshes'][0]['primitives'][0]['indices']]['count']//3

# The two proposed patches leave the established G2 to G3 ground corridor separate.
spots=[(11,7.5,math.radians(-16)),(9.2,-7.1,math.radians(19))]
course=[(112.4,214),(118.5,210.84),(128,202.25),(136.5,194.9),(145.2,186.8),(156,186),(174,186),(191,186)]
samples=[Vector((x-146,186-z-off)) for off in (-1.3,-.65,0,.65,1.3)
         for a,b in zip(course,course[1:]) for x,z in
         [(a[0]+(b[0]-a[0])*t/240,a[1]+(b[1]-a[1])*t/240) for t in range(241)]]
proof=[]
for x,y,yaw in spots:
    T=Matrix.Translation((x,y,.05))@Matrix.Rotation(yaw,4,'Z')
    models=load(file,T)
    heights=[]
    for i,j in itertools.product(range(29),range(13)):
        p=T@Vector((-W/2+W*i/28,-D/2+D*j/12,0))
        h,n,_,_=base.ray_cast(Vector((p.x,p.y,3.5)),Vector((0,0,-1)),4)
        assert h is not None and abs(h.z-.05)<3e-5 and abs(n.z)>.99,(x,y,p,h)
        heights.append(h.z)
    mesh=bvh(models)
    assert not mesh.overlap(base)
    vertices=[ob.matrix_world@v.co for ob in models for v in ob.data.vertices]
    assert min(v.z for v in vertices)>.0539 and max(v.z for v in vertices)<.0561
    co,si=math.cos(yaw),math.sin(yaw)
    unsigned=[]
    for p in samples:
        dx,dy=p.x-x,p.y-y
        tx,ty=abs(co*dx+si*dy),abs(-si*dx+co*dy)
        unsigned.append(math.hypot(max(tx-W/2,0),max(ty-D/2,0)))
    # Each route subsegment is at most 0.08 m long; deduct half that plus capsule radius.
    clear=min(unsigned)-.04-.38
    assert clear>2.5,clear
    proof.append(dict(origin_three=[round(146+x,4),.05,round(186-y,4)],yaw_three=yaw,
        floor_samples=len(heights),deck_height_m=.05,nonoverlap=True,
        clearance_lower_bound_to_tested_corridor_m=round(clear,4)))

luminance=lambda rgb:sum(a*b for a,b in zip(rgb,(.2126,.7152,.0722)))
worst=(luminance(amber)*.83+.05)/(luminance(dark)*1.15+.05)
assert worst>4.5
receipt=dict(scope='Two static proposed Overtime zones. No movement modifier, triggers, entity, damage, collider or game deployment.',
    dimensions_m=[W,D],placement=proof,source_donors={p[0]:p[1] for p in pins},
    unlit_palette_contrast_lower_bound=round(worst,3),texture_count=0,
    bytes=len(raw),triangles=tris,mesh_sha256=hashlib.sha256(raw).hexdigest())
(out/'e11d-c3-overtime-tape.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt)
if __import__('os').environ.get('WSC_VALIDATE_ONLY')=='1':raise SystemExit(0)

world=bpy.data.worlds.new('Warm industrial sky');world.use_nodes=True
b=world.node_tree.nodes['Background'];b.inputs[0].default_value=(.37,.50,.63,1);b.inputs[1].default_value=.53
S.world=world
key=bpy.data.lights.new('West afternoon','SUN');key.energy=2.25;key.angle=.15;key.color=(1,.91,.76)
light=bpy.data.objects.new(key.name,key);S.collection.objects.link(light);light.rotation_euler=(.38,-.42,-.76)
camera=bpy.data.cameras.new('C3 Overtime review')
ob=bpy.data.objects.new(camera.name,camera);S.collection.objects.link(ob);S.camera=ob
S.render.engine='CYCLES';S.cycles.samples=38;S.cycles.use_denoising=False
S.cycles.use_adaptive_sampling=True;S.cycles.adaptive_threshold=.035
S.view_settings.view_transform='AgX';S.render.resolution_percentage=100
S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=93
for file,p,target,lens,w,h in [
    ('overtime-eye',(5.2,1.15,1.75),(14.2,8.6,1.0),26,1350,940),
    ('overtime-court',(-11,-17,26),(16,4,1.4),27,1350,940),
]:
    ob.location=p;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    camera.lens=lens;S.render.resolution_x=w;S.render.resolution_y=h
    S.render.filepath=str(out/(file+'.jpg'));bpy.ops.render.render(write_still=True)

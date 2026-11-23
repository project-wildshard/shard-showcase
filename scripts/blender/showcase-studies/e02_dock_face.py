"""E02 face treatment on exact E03 dock, retaining the original separately."""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,export,output_directory

assets=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art'
donor=assets/'wsc-prop-053-robot-dock.glb'
assert hashlib.sha256(donor.read_bytes()).hexdigest()=='24550d532c55a98de78abd2df3c1adde9885554242e2be7ecff625ecb9ddafac'
out=output_directory()
dst=out/'wsc-prop-053-e02-dock-face.glb'
s=bpy.context.scene
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(donor))
bpy.context.view_layer.update()
original=list(s.objects)
assert len(original)==6
vol=[]
for o in original:
    b=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get())
    vol.append((o,o.matrix_world.inverted(),b))
def side_y(x,z):
    hits=[]
    for o,m,b in vol:
        p=b.ray_cast(m@Vector((x,-2,z)),m.to_3x3()@Vector((0,1,0)),2)[0]
        if p is not None:hits.append((o.matrix_world@p).y)
    if not hits:raise ValueError((x,z))
    return min(hits)
def mean_face(x,z):
    return side_y(x,z)
probe=[(z,side_y(0,z)) for z in (.15,.27,.39,.47,.51)]
print(probe,flush=True)

def mat(n,c,metal=.0,rough=.52,emit=0):
    m=bpy.data.materials.new(n);m.use_nodes=True
    n=m.node_tree.nodes['Principled BSDF']
    for k,v in {'Base Color':(*c,1),'Metallic':metal,'Roughness':rough,
                'Emission Color':(*c,1),'Emission Strength':emit}.items():
        n.inputs[k].default_value=v
    return m
gun=mat('E02 blue-gray steel',(.176,.238,.266),.61,.40)
edge=mat('E02 machined frame',(.335,.419,.44),.70,.37)
deep=mat('E02 graphite pocket',(.025,.047,.053),.33,.53)
orange=mat('E02 orange enamel',(.86,.255,.018),.22,.54)
cyan=mat('E02 cold cyan diffuser',(.002,.47,.57),.16,.34,1.55)
silver=mat('E02 pale fasteners',(.42,.52,.53),.75,.32)
buckets=defaultdict(lambda:[[],[]])

# Four identical sides. Each front piece follows measured side profiles
# at the panel center instead of moving or stretching the original shell.
def block(group,m,x,w,z,h,y_bottom,y_top,depth):
    v,f=buckets[(group,m)]
    faces=((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5))
    ix=len(v)
    for k,y in ((-1,y_bottom),(1,y_top)):
        for j in (-1,1):
            for a in (-1,1):
                v.append((x+a*w/2,y+j*depth/2,z+k*h/2))
    f.extend(tuple(ix+j for j in face) for face in faces)

def panel(g,m,x,w,z,h,offset,depth):
    block(g,m,x,w,z,h,mean_face(x,z-h/2)+offset,mean_face(x,z+h/2)+offset,depth)

panel('Frame',deep,0,.88,.302,.173,-.010,.031)
for x in (-.42,.42):
    # Jambs embedded partly into the donor (an intentional 10–20 mm seam).
    panel('Frame',gun,x,.126,.30,.298,-.008,.082)
    panel('Frame',edge,x,.055,.302,.268,-.046,.035)
    panel('Feet',orange,x,.184,.109,.138,-.024,.120)
    panel('Feet',deep,x,.096,.123,.025,-.088,.019)
for z in (.201,.405):
    panel('Frame',gun,0,.831,z,.047,-.036,.070)
    panel('Frame',edge,0,.712,z+.010,.019,-.067,.022)
for z in (.258,.294,.33):
    panel('Bands',cyan,0,.58,z,.021,-.040,.019)
for x in (-.42,.42):
    for z in (.231,.385):
        panel('Frame',silver,x,.031,z,.028,-.076,.029)

# Low stacked crown outboard of the landing pad. Corner seams intentionally
# end short of the original chamfer. The cyan stripe is below the top lip.
for z,h,y,g,m,w,depth in ((.546,.057,-.724,'Crown',gun,1.23,.101),
                         (.536,.024,-.776,'Bands',cyan,1.236,.026),
                         (.584,.040,-.712,'Crown',edge,1.23,.123),
                         (.610,.022,-.702,'Crown',deep,1.17,.105)):
    block(g,m,0,w,z,h,y,y,depth)

gs=defaultdict(list)
for (name,m),(v,f) in buckets.items():
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.materials.append(m);mesh.update()
    o=bpy.data.objects.new(name+' | '+m.name,mesh);s.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o
    k=o.modifiers.new('Machine bevel','BEVEL');k.width=.005;k.segments=1
    bpy.ops.object.modifier_apply(modifier=k.name)
    gs[name].append(o)
parts=[]
for name,os in gs.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in os:o.select_set(True)
    bpy.context.view_layer.objects.active=os[0]
    if len(os)>1:bpy.ops.object.join()
    os[0].name=name+' 1';parts.append(os[0])
    for i in range(1,4):
        o=bpy.data.objects.new(name+' '+str(i+1),os[0].data)
        s.collection.objects.link(o)
        o.rotation_euler.z=math.pi/2*i
        parts.append(o)
export(parts,dst)
for o in parts:bpy.data.objects.remove(o,do_unlink=True)
before=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(dst))
bpy.context.view_layer.update()
kit=list(set(s.objects)-before)
assert {o.name for o in kit}=={f'{name} {i}' for name in ('Feet','Frame','Bands','Crown') for i in range(1,5)}
meshpts=[o.matrix_world@p.co for o in kit for p in o.data.vertices]
top=[p for p in meshpts if p.z>=.542]
assert min(max(abs(p.x),abs(p.y)) for p in top)>.62
assert all(p.z>=0 and p.z<=.63 for p in meshpts)
span=max(max(abs(p.x),abs(p.y)) for p in meshpts)*2
assert span<2.26
raw=dst.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tris=sum(d['accessors'][q['indices']]['count']//3 for m in d['meshes'] for q in m['primitives'])
assert len(raw)<90000 and len(d['meshes'])==4 and len(d['nodes'])==16 and not any(d.get(k) for k in ('images','skins','animations'))
(out/'validation.json').write_text(json.dumps({'id':'WSC-PROP-053','bytes':len(raw),'triangles':tris,
    'source_side_probes':probe,'kit_outer_span_m':span,'crown_pad_edge_clearance_m': min(max(abs(p.x),abs(p.y)) for p in top)-.513677,
    'same_origin':True,'original_changed':False,'runtime':False},indent=2)+'\n')

all_components=sorted(kit,key=lambda o:o.name)
base=sorted(original,key=lambda o:o.name)
for o in all_components+base:o.hide_render=True
def put(objs,at):
    new=[]
    for src in objs:
        o=bpy.data.objects.new('Study '+src.name,src.data);s.collection.objects.link(o)
        o.matrix_world=Matrix.Translation(at)@src.matrix_world
        new.append(o)
    return new

left=put(base,(-1.30,0,0))
right=put(base+all_components,(1.30,0,0))
floor=mat('Muted East yard slate',(.088,.112,.113),.12,.85)
bpy.ops.mesh.primitive_plane_add(size=150,location=(0,0,-.006));bpy.context.object.data.materials.append(floor)
def aim(o,q):o.rotation_euler=(Vector(q)-o.location).to_track_quat('-Z','Y').to_euler()
def area(n,p,q,e,c,sz):
    l=bpy.data.lights.new(n,'AREA');l.energy=e;l.color=c;l.shape='DISK';l.size=sz
    o=bpy.data.objects.new(n,l);s.collection.objects.link(o);o.location=p;aim(o,q)
s.world=bpy.data.worlds.new('Cool warehouse bounce');s.world.color=(.18,.22,.26)
area('Hot sodium rim',(-3,1.3,4.3),(0,0,.4),930,(1,.61,.33),3.3)
area('Overcast blue key',(1,-4.7,4.1),(0,0,.37),1000,(.68,.85,1),4)
area('High gray fill',(2,2.3,3.55),(0,0,.35),620,(.82,.95,1),2.3)
c=bpy.data.cameras.new('E02 matched camera')
s.camera=bpy.data.objects.new(c.name,c);s.collection.objects.link(s.camera);c.type='ORTHO'
s.render.engine='CYCLES';s.cycles.samples=46;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=91;s.render.resolution_percentage=100
def render(n,p,q,scale,wh):
    s.camera.location=p;aim(s.camera,q);c.ortho_scale=scale
    s.render.resolution_x,s.render.resolution_y=wh
    s.render.filepath=str(out/(n+'.jpg'));bpy.ops.render.render(write_still=True)
render('nov23-e02-dock-compare',(0,-6,3.3),(0,0,.22),5.16,(1500,795))
for o in left:o.hide_render=True
render('nov23-e02-dock-detail',(3.3,-4.5,2.01),(1.30,-.10,.30),2.78,(1240,940))

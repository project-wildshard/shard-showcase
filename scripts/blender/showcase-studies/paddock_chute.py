"""W10a paddock-to-oval visual exit: exact archive footprint and one waymarker."""
import hashlib
import json
import math
import os
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Matrix, Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import clear_scene, export, output_directory
out=output_directory()
clear_scene()
scene=bpy.context.scene
assets=HERE.parents[2]/'public/assets/wildshard-art'
donors={
 'rail':('wsc-module-011-riding-fence.glb','4b080d634287a167eba8cc4690b7fbedd0323244154a7bb96402262b71c4afe0'),
 'block':('wsc-plan-008-horse-mounting-block-wip.glb','efc0615bfb51f527545bee0d5b36fff8856559928ddaf87a963955333867bf7a'),
 'trough':('w10a-paddock-trough-wip.glb','ff0e65ffce361608b0872bd9368bdcced1b19f00d635c460dc6c3dcb6430d56d'),
 'oak':('wsc-prop-012-deciduous-tree.glb','83685e45bd4ef2af08941de87909aaf0f7078dbecfe784bc06a9fc8fc4d8a355'),
}
def load(file):
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(file))
    bpy.context.view_layer.update()
    new=set(scene.objects)-before
    data=[(o.data,o.matrix_world.copy()) for o in sorted(new,key=lambda x:x.name) if o.type=='MESH']
    for o in new: bpy.data.objects.remove(o,do_unlink=True)
    return data
templates={}
for key,(name,sha) in donors.items():
    f=assets/name
    assert hashlib.sha256(f.read_bytes()).hexdigest()==sha
    templates[key]=load(f)
def place(key,n,p,yaw=0,sx=1):
    transform=Matrix.Translation(Vector(p))@Matrix.Rotation(yaw,4,'Z')@Matrix.Diagonal((sx,1,1,1))
    obs=[]
    for d,m in templates[key]:
        o=bpy.data.objects.new(n,d)
        scene.collection.objects.link(o)
        o.matrix_world=transform@m
        obs.append(o)
    return obs
def mat(n,rgb,rough=.6,metal=0):
    m=bpy.data.materials.new(n)
    m.use_nodes=True
    p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    return m
def mesh(n,v,f,m):
    d=bpy.data.meshes.new(n)
    d.from_pydata(v,[],f)
    d.update()
    d.materials.append(m)
    o=bpy.data.objects.new(n,d)
    scene.collection.objects.link(o)
    return o
def box(n,p,dim,m,r=0):
    x,y,z=[v*.5 for v in dim]
    o=mesh(n,[(i*x,j*y,k*z) for k in (-1,1) for j in (-1,1) for i in (-1,1)],
           [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m)
    o.location=p
    if r:
        b=o.modifiers.new('Worn corner radius','BEVEL')
        b.width,b.segments=r,2
        o.modifiers.new('Face normals','WEIGHTED_NORMAL')
    return o
ivory=mat('Lime linen paint',(.82,.77,.57),.57)
teal=mat('Course petrol enamel',(.055,.254,.262),.49,.15)
wood=mat('Honey cedar grain tone',(.24,.122,.043),.72)
iron=mat('Burnished corner iron',(.096,.126,.130),.44,.62)
yellow=mat('Patinated bronze trim',(.47,.26,.084),.43,.48)
parts=[
    box('Waymarker · stone shoe',(0,0,.095),(.76,.50,.19),iron,.034),
    box('Waymarker · cedar upright',(0,0,1.06),(.24,.25,2.01),wood,.018),
    box('Waymarker · white cap',(0,0,2.065),(.35,.34,.10),ivory,.022),
    box('Waymarker · border',(0,-.047,1.48),(1.28,.19,.73),yellow,.044),
    box('Waymarker · enamel face',(0,-.152,1.48),(1.18,.054,.64),teal,.036),
]
for side in (-1,1):
    for z in (1.25,1.71):
        parts.append(box('Waymarker · stud',(side*.50,-.183,z),(.048,.036,.048),ivory,.007))
# The left and right signs share the same upright and inscription.
d=bpy.data.curves.new('OVAL lettering','FONT')
d.body='OVAL'
d.align_x='CENTER'
d.align_y='CENTER'
d.size=.25
d.resolution_u=4
d.materials.append(ivory)
o=bpy.data.objects.new('Waymarker · OVAL',d)
scene.collection.objects.link(o)
o.location=(0,-.184,1.63)
o.rotation_euler.x=math.pi/2
bpy.ops.object.select_all(action='DESELECT')
o.select_set(True)
bpy.context.view_layer.objects.active=o
bpy.ops.object.convert(target='MESH')
parts.append(bpy.context.object)
# Upright arrow in graphic space; the board faces the approach at local −Y.
pts=[(-.035,1.20),(.035,1.20),(.035,1.36),(.112,1.36),
     (0,1.475),(-.112,1.36),(-.035,1.36)]
parts.append(mesh('Waymarker · arrow',[(x,-.184,z) for x,z in pts],[tuple(range(7))],ivory))
file=out/'w10a-oval-waymarker.glb'
export(parts,file)
raw=file.read_bytes()
d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tri=sum(d['accessors'][p['indices']]['count']//3 for m in d['meshes'] for p in m['primitives'])
assert len(raw)<75000 and tri<1800 and not d.get('images')
for o in parts:bpy.data.objects.remove(o,do_unlink=True)
templates['marker']=load(file)

# Three.js (-40,-132) is local (0,0), Three -Z forward is Blender +Y.
# Fence footprints use the source endpoints; texture, siding and signs are proposals.
pts=[m@v.co for d,m in templates['rail'] for v in d.vertices]
lo,hi=min(v.x for v in pts),max(v.x for v in pts)
span=hi-lo
assert 2.8<span<3.6 and abs(lo+hi)<.05
rail_groups=[]
def edge(a,b,n=None,check=False):
    a,b=Vector(a),Vector(b)
    direction=b-a
    length=direction.length
    yaw=math.atan2(direction.y,direction.x)
    n=n or max(1,round(length/span))
    group=[]
    for i in range(n):
        x,y=a+direction*((i+.5)/n)
        obs=place('rail','Linked riding fence',(x,y,0),yaw,length/n/span)
        group.extend(obs)
        if check:rail_groups.extend(obs)
    return group
for x in (-6.,6.):
    edge((x,0),(x,14),5,True)
entrance_rails=edge((-22,0),(-6,0))+edge((6,0),(26,0))
for a,b in (((-22,0),(-22,-60)),((26,0),(26,-60)),
            ((-22,-60),(-2,-60)),((10,-60),(26,-60))):
    edge(a,b)
signs=[]
for x in (-7.22,7.22):
    signs+=place('marker','Oval approach waymarker',(x,-.55,0))
place('block','Existing mounting block',(4,-36,0))
place('trough','Existing paddock trough',(-12,-32,0))
bpy.context.view_layer.update()
rr=[o.matrix_world@v.co for o in rail_groups for v in o.data.vertices]
left=max(p.x for p in rr if p.x<0)
right=min(p.x for p in rr if p.x>0)
assert abs(right-left-11.67)<.0002 and min(v.y for v in rr)>-.05 and max(v.y for v in rr)<14.05,(left,right,min(v.y for v in rr),max(v.y for v in rr))
sg=[o.matrix_world@v.co for o in signs for v in o.data.vertices]
front=min((o.matrix_world@v.co).y for o in entrance_rails for v in o.data.vertices)
sign_clearance=front-max(p.y for p in sg)
assert sign_clearance>.125,sign_clearance
assert min(abs(p.x) for p in sg)>6.4 and abs(min(p.z for p in sg))<.0001 and max(p.y for p in sg)<-.295

# Ground styling stays in the preview, with an explicitly inferred track strip.
dirt=mat('Paddock umber',(.34,.247,.147),.92)
lane=mat('Chute ochre sand',(.48,.351,.198),.86)
grass=mat('Late meadow green',(.188,.232,.092),.94)
track=mat('Archive oval context only',(.32,.235,.14),.89)
box('Wide meadow',(0,-6,-.11),(320,270,.19),grass)
box('Original paddock footprint',(2,-30,-.039),(48,60,.08),dirt)
box('Chute sand surface',(0,7,.002),(12,14,.011),lane)
box('Illustrative oval surface beyond chute',(0,20,.001),(110,12,.008),track)
for j,(x,y) in enumerate(((-19,11),(21,14),(-37,23),(32,24),(-9,32),(12,37))):
    place("oak","Existing oak backdrop",(x,y,0),j*.89)
# Low scattered grass blades outside the 12 m lane; no texture or external donors.
rng=random.Random(72)
for k in range(3):
    vg,fg=[],[]
    for i in range(165):
        x=rng.choice((-1,1))*rng.uniform(6.4,12)
        y=rng.uniform(-2,14)
        for _ in range(3):
            a=x+rng.uniform(-.18,.18);b=y+rng.uniform(-.18,.18);h=rng.uniform(.05,.23)
            j=len(vg)
            vg += [(a-.028,b,.002),(a+.028,b,.002),(a+rng.uniform(-.055,.055),b+.025,h)]
            fg.append((j,j+1,j+2))
    mesh('Meadow grass stubble',vg,fg,mat('Stubble '+str(k),(.22+k*.05,.25+k*.026,.10),.97))

world=bpy.data.worlds.new('Paddock daylight')
world.use_nodes=True
bg=world.node_tree.nodes['Background']
bg.inputs[0].default_value=(.45,.58,.77,1)
bg.inputs[1].default_value=.57
scene.world=world
d=bpy.data.lights.new('Morning light','SUN')
d.energy=2.5
d.angle=math.radians(5)
d.color=(1,.84,.60)
sun=bpy.data.objects.new(d.name,d)
scene.collection.objects.link(sun)
sun.rotation_euler=Vector((.53,.56,-.9)).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
cam.data.clip_end=320
scene.render.engine='CYCLES'
scene.cycles.samples=36
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.078
scene.cycles.use_denoising=False
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.render.resolution_x,scene.render.resolution_y=1380,920
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG'
scene.render.image_settings.quality=91
for tag,eye,target,lens in (
    ('approach',(.75,-15,2.6),(0,4,1.32),30),
    ('plan',(-13,-13,17),(0,5,.7),35),
):
    cam.location=eye
    cam.data.lens=lens
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/f'nov24-w10a-chute-{tag}.jpg')
    if not os.environ.get('WILDSHARD_VALIDATE_ONLY'):bpy.ops.render.render(write_still=True)
(out/'chute-verify.json').write_text(json.dumps({
    'archive':'Raynos/project-wildshard-singleplayer@ce1cf050b3','three_threshold_xz':[-40,-132],
    'footprint_m':[48,60],'chute_m':[12,14],'measured_clear_width_m':round(right-left,4),
    'sign_to_entrance_fence_m':round(sign_clearance,4),'donor_fence_span_m':round(span,5),'longitudinal_fence_scale':round(14/5/span,5),
    'waymarker_bytes':len(raw),'waymarker_triangles':tri,'sha256':hashlib.sha256(raw).hexdigest(),
    'source_hashes':{k:x[1] for k,x in donors.items()},'native':False,
},indent=2)+'\n')

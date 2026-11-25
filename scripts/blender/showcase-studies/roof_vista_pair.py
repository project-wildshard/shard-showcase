"""W9b roof vista seat treatment and camera fit, in canonical whole-town art."""
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,export

stage,out=(Path(p).resolve() for p in sys.argv[sys.argv.index('--')+1:])
out.mkdir(parents=True,exist_ok=True)
parity=json.loads((stage/'parity.json').read_text())['matched_signature']
expected=json.loads((root/'scripts/blender/west-town/expected.json').read_text())
assert parity in [v for v in expected.values() if isinstance(v,list)]
bench=root/'public/assets/wildshard-art/wsc-prop-044-lookout-bench.glb'
pin='9109111c13a27c81981839237b9f1880c9e964930f5888e24c1054ac819bfeb1'
assert hashlib.sha256(bench.read_bytes()).hexdigest()==pin
clear_scene()
s=bpy.context.scene

def mat(n,c,rough=.6,metal=0):
    m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1)
    p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m

steel=mat('Parkerized bracket',(.088,.119,.123),.49,.64)
face=mat('Pressed green enamel',(.046,.196,.201),.37,.25)
bronze=mat('Burnished bronze keyline',(.42,.22,.061),.37,.68)
cream=mat('Warm stamp enamel',(.86,.76,.54),.53,.18)

def box(n,p,d,m,w=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.scale=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if w:
        v=o.modifiers.new('Rounded edge','BEVEL');v.width=w;v.segments=1
        bpy.ops.object.modifier_apply(modifier=v.name)
    return o

def face_text(t,at,size,yaw=0):
    cu=bpy.data.curves.new(t,'FONT');cu.body=t;cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER'
    cu.resolution_u=3;cu.materials.append(cream)
    o=bpy.data.objects.new(t,cu);s.collection.objects.link(o)
    o.location=at;o.rotation_euler=(0,0,yaw)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    return o

def badge(n,x):
    parts=[box('Integral bronze keyline',(x,0,.018),(.57,.39,.034),bronze,.012),
        box('Raised enamel panel',(x,0,.041),(.53,.35,.027),face,.012)]
    parts.append(face_text(n,(x,.018,.058),.202))
    parts.append(face_text('VISTA',(x,-.103,.058),.046))
    for dx in (-.228,.228):
        for yy in (-.138,.138):
            bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.019,depth=.012,location=(x+dx,yy,.054))
            o=bpy.context.object;o.data.materials.append(steel);parts.append(o)
    o=parts[0]
    bpy.ops.object.select_all(action='DESELECT')
    for part in parts:part.select_set(True)
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.join()
    bpy.context.view_layer.update()
    o.data.transform(Matrix.Translation((-x,0,0))@o.matrix_world)
    o.matrix_world=Matrix.Translation((x,0,0))
    o.name=o.data.name='Vista '+n+' · flush badge'
    return o

tags=[badge('02',-.42),badge('03',.42)]
glb=out/'w9b-roof-vista-badges.glb'
export(tags,glb)
raw=glb.read_bytes()
layout=json.loads(raw[20:20+int.from_bytes(raw[12:16],'little')])
tri=sum(layout['accessors'][p['indices']]['count']//3 for m in layout['meshes'] for p in m['primitives'])
assert len(layout['nodes'])==len(layout['meshes'])==2 and tri<1200 and len(raw)<76000

bpy.ops.wm.open_mainfile(filepath=str(stage/'whole-town-editable.blend'))
s=bpy.context.scene
s.render.use_compositing=False
originals=[o for o in s.objects if o.type=='MESH']
def bvh(obs):
    vs=[];fs=[]
    for o in obs:
        n=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
        fs.extend(tuple(n+i for i in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(vs,fs)
roof=bvh(o for o in originals if o.name.startswith('JUNCTION |'))
tower=bvh(o for o in originals if o.name.startswith(('MODULE-001','PROP-033 | launch')))
world=bvh(originals)

def import_new(path):
    before=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(path))
    return [o for o in set(s.objects)-before if o.type=='MESH']

tag_parts=import_new(glb)
rows=[
    {'id':'02','anchor':(-206,18,-104),'legacy_proxy':(-206,18,-102),
     'fit':(-206,102,18),'look':(-218.67,35.22,48.6),'tree':roof,'floor':18,
     'target':'Grapple tower facet','near':59.0,'desc':'Movers Tank roof'},
    {'id':'03','anchor':(-212,45,-34),'legacy_proxy':(-212,45,-32),
     'fit':(-214.5,31.9,45.05),'look':(-115,16.5,14),'tree':tower,'floor':45.05,
     'target':'Zip-house roof','near':88.0,'desc':'Grapple tower top'},
]
review={}
for row in rows:
    bp=Vector(row['fit']);dst=Vector(row['look'])
    d=Vector((dst.x-bp.x,dst.y-bp.y,0)).normalized()
    side=Vector((-d.y,d.x,0))
    yaw=math.atan2(d.x,-d.y)
    rot=Matrix.Rotation(yaw,4,'Z')
    direction=lambda o:rot@Vector(o)
    cast=lambda p:row['tree'].ray_cast((p.x,p.y,bp.z+2.6),(0,0,-1),3.6)[0]
    proxy=Vector((row['legacy_proxy'][0],-row['legacy_proxy'][2],row['legacy_proxy'][1]))
    proxy_h=cast(proxy)
    if row['id']=='03':assert proxy_h is None,proxy_h
    count=0
    for a in (-.95,-.55,0,.55,.95):
        for b in (-.32,0,.32):
            p=bp+direction((a,b,0))
            h=cast(p)
            assert h is not None and abs(h.z-row['floor'])<.0015,(row['id'],tuple(p),h)
            count+=1
    new=import_new(bench)
    tr=Matrix.Translation(bp)@rot
    for o in new:o.matrix_world=tr@o.matrix_world
    bpy.context.view_layer.update()
    actual=[o.matrix_world@v.co for o in new for v in o.data.vertices]
    assert abs(min(p.z for p in actual)-bp.z)<.00004
    tp=bp-d*.73+side*.38
    for u,v in [(-.24,-.16),(-.24,.16),(.24,.16),(.24,-.16),(0,0)]:
        h=cast(tp+direction((u,v,0)))
        assert h is not None and abs(h.z-bp.z)<.0015,(row['id'],tuple(tp),h)
    matches=[o for o in tag_parts if o.name.startswith('Vista '+row['id'])]
    assert matches
    for o in matches:o.matrix_world=Matrix.Translation(tp)@rot
    eye=bp+d*.18+Vector((0,0,1.48))
    delta=dst-eye
    hit=world.ray_cast(eye,delta.normalized(),min(delta.length,row['near']))[0]
    assert hit is None,(row['id'],hit)
    target_hit=world.ray_cast(eye,delta.normalized(),delta.length+4)[0]
    assert target_hit is not None and (target_hit-dst).length<2,(row['id'],target_hit)
    row['bp'],row['d'],row['side'],row['dst']=bp,d,side,dst
    review[row['id']]={'anchorWorld':row['anchor'],'legacyProxyWorld':row['legacy_proxy'],
        'legacyProxyDeckHeight':None if proxy_h is None else round(proxy_h.z,5),
        'fittedBenchWorld':[bp.x,bp.z,-bp.y],'benchOffsetHorizontalMeters':(bp.xy-proxy.xy).length,
        'badgePoseWorld':[tp.x,tp.z,-tp.y],'seatedEyeWorld':[eye.x,eye.z,-eye.y],'benchFloorRays':count,'badgeFloorRays':5,
        'clearCenterMeters':min(delta.length,row['near']),'target':row['target'],
        'firstHitWorld':None if target_hit is None else [target_hit.x,target_hit.z,-target_hit.y]}

(out/'validation.json').write_text(json.dumps({'branchScope':'Static vista camera/bench art. No collision, interactables or reveals.',
    'sourceLab':'51a3b4bef1f2d4891172164d10893d98d450a3b9','sourceLayout':'5d019a020361c47187ec889f2bc947f82cd9f98a',
    'canonicalScene':parity,'donorBenchSha256':pin,'badgeBytes':len(raw),'badgeTriangles':tri,'roofs':review},indent=2)+'\n')
if os.getenv('WILDSHARD_VALIDATE_ONLY'):raise SystemExit(0)

# A wider Blender review camera stays separate from the tested seated ray.
def aim(o,p,t):
    o.location=p;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
for o in list(s.objects):
    if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
w=bpy.data.worlds.new('Slate mountain sky');w.use_nodes=True;s.world=w
nd=w.node_tree.nodes;sky=nd.new('ShaderNodeTexSky');sky.sky_type='NISHITA'
sky.sun_elevation=.36;sky.sun_rotation=-1.08;sky.sun_size=.082;sky.sun_intensity=.66
nd.get('Background').inputs['Strength'].default_value=.38
# Keep the sky lighting but soften its visible pitch.
w.node_tree.links.new(sky.outputs[0],nd.get('Background').inputs[0])
rng=random.Random(44)
def horizon(layer,rise):
    a=[]
    for j in range(120):
        t=j*math.tau/120
        r=450+layer*70
        z=rise+14*math.sin(6*t+layer)**2+8*math.sin(17*t)**2+rng.random()*5
        a.extend([(r*math.cos(t),r*math.sin(t),-8),(r*math.cos(t),r*math.sin(t),z)])
    fs=[(2*j,2*((j+1)%120),2*((j+1)%120)+1,2*j+1) for j in range(120)]
    mesh=bpy.data.meshes.new('Review distant ridge');mesh.from_pydata(a,[],fs);mesh.update()
    o=bpy.data.objects.new('Render-only distant ridge',mesh);s.collection.objects.link(o)
    mesh.materials.append(mat('Distant shale '+str(layer),(.17+layer*.05,.224+layer*.045,.245+layer*.047),.85))
horizon(0,12);horizon(1,26)
cam=bpy.data.objects.new('Vista presentation',bpy.data.cameras.new('Vista presentation'));s.collection.objects.link(cam);s.camera=cam
cam.data.lens=28;cam.data.clip_end=1100
s.render.engine='CYCLES';s.cycles.samples=34;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.072
s.cycles.use_denoising=False
s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=1580,1020,100
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-1.04
s.render.image_settings.file_format='JPEG';s.render.image_settings.color_mode='RGB';s.render.image_settings.quality=94
for row in rows:
    bp,d,side,dst=(row[k] for k in ('bp','d','side','dst'))
    if row['id']=='02':
        p=bp-8.2*d+1.70*side+Vector((0,0,2.10))
        target=bp+20*d+Vector((0,0,3.77))
    else:
        p=bp-6.0*d-1.15*side+Vector((0,0,3.22))
        target=bp+22*d+Vector((0,0,-4.90))
    aim(cam,p,target)
    s.render.filepath=str(out/('nov25-roof-vista-'+row['id']+'.jpg'))
    bpy.ops.render.render(write_still=True)

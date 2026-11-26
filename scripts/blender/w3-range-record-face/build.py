"""Removable drill record card fitted over the exact old timer face."""
import hashlib
import json
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'showcase-studies'))
from common import clear_scene,export,output_directory

out=output_directory()
assets=here.parents[2]/'public/assets/wildshard-art'
donor=assets/'wsc-prop-027-range-timer-display.glb'
pin='5e443a0211c4b5806c7f7118cc4a00c7bad19c31522a75d9f2295c3a71a42bc3'
assert hashlib.sha256(donor.read_bytes()).hexdigest()==pin
clear_scene()
s=bpy.context.scene

def mat(name,c,rough=.65,metal=0,glow=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*c,1)
    m.use_nodes=True
    q=m.node_tree.nodes['Principled BSDF']
    for k,v in [('Base Color',(*c,1)),('Roughness',rough),('Metallic',metal),
                ('Emission Color',(*c,1)),('Emission Strength',glow)]:
        q.inputs[k].default_value=v
    return m

black=mat('Deep petrol enamel',(.023,.061,.069),.54,.13)
stripe=mat('Muted header and row bars',(.043,.140,.154),.69,.1)
aqua=mat('Cyan screen printing',(.25,.80,.78),.44,0,.4)
white=mat('Ivory screen printing',(.87,.90,.75),.47,0,.25)
amber=mat('Warm brass screen printing',(.93,.59,.19),.51,0,.35)
face_y=-.337
parts=[]

def box(name,at,size,m,b=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=at)
    o=bpy.context.object
    o.name,o.dimensions=name,size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if b:
        mod=o.modifiers.new('Bevel','BEVEL')
        mod.width,mod.segments=b,1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return o

def text(body,x,z,size,m,max_width,align='LEFT',bucket=None):
    f=bpy.data.curves.new(body,'FONT')
    f.body,f.align_x,f.align_y,f.size=body,align,'CENTER',size
    f.resolution_u=3
    f.materials.append(m)
    o=bpy.data.objects.new(body,f)
    s.collection.objects.link(o)
    o.location=(x,face_y-.004,z)
    o.rotation_euler.x=1.5707963267948966
    bpy.context.view_layer.update()
    if o.dimensions.x>max_width:o.scale.x=max_width/o.dimensions.x
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    if bucket is not None:bucket.append(o)
    return o

body=box('Reversible record face', (0,face_y+.007,.736), (1.608,.014,.576),black,.002)
parts.append(body)
parts.append(box('Header band',(0,face_y-.0006,.966),(1.552,.0012,.077),stripe))
for z in [.838,.719,.600,.527]:
    parts.append(box('Table row divider',(0,face_y-.0006,z),(1.495,.0012,.0035),stripe))
parts.append(box('Score column rule',(.326,face_y-.0006,.683),(.0035,.0012,.309),stripe))
text('RANGE RECORDS',-.735,.964,.091,amber,1.34,bucket=parts)
text('DRILL',-.735,.867,.058,aqua,.65,bucket=parts)
text('PERSONAL BEST',.735,.867,.058,aqua,.38,'RIGHT',parts)
for z,title in zip((.779,.659,.552),('SIX DUMMIES','LANES','RIFLE')):
    text(title,-.735,z,.076,white,.90,bucket=parts)
text('RECORDS APPEAR AFTER A FINISHED DRILL',-.735,.484,.048,aqua,1.45,bucket=parts)
# The value slots are deliberately editable, not a fabricated saved score.
unset=[]
for z in (.779,.659,.552):
    text('--',.702,z,.077,white,.28,'RIGHT',unset)

groups=[]
named=[('Range face | '+m.name,[o for o in parts if o.data.materials[0]==m]) for m in (black,stripe,aqua,white,amber)]
for name,oo in [*named,('RangeRecordUnsetValues',unset)]:
    bpy.ops.object.select_all(action='DESELECT')
    for o in oo:o.select_set(True)
    bpy.context.view_layer.objects.active=oo[0]
    if len(oo)>1:bpy.ops.object.join()
    o=bpy.context.object
    o.name=name
    s.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    groups.append(o)
file=out/'w3a-range-record-face.glb'
export(groups,file)
raw=file.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
j=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
pr=[p for m in j['meshes'] for p in m['primitives']]
tri=sum(j['accessors'][p['indices']]['count']//3 for p in pr)
assert len(raw)<130000 and tri<3200 and len(pr)==6
assert not any(k in j for k in ('animations','images','skins','cameras'))
clear_scene()

def load(p):
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    bpy.context.view_layer.update()
    return sorted(set(s.objects)-before,key=lambda o:o.name)

old=load(donor)
assert len(old)==1
new=load(file)
shell=next(o for o in new if any('Deep petrol enamel' in m.name for m in o.data.materials))

def pts(objs):
    return [o.matrix_world@v.co for o in objs if o.type=='MESH' for v in o.data.vertices]

def tree(objs):
    p,fs=[],[]
    for o in objs:
        n=len(p)
        p.extend(pts([o]))
        fs.extend(tuple(n+i for i in poly.vertices) for poly in o.data.polygons)
    return BVHTree.FromPolygons(p,fs)

p=pts(new)
lo=[min(v[i] for v in p) for i in range(3)]
hi=[max(v[i] for v in p) for i in range(3)]
assert lo[0]>-.815 and hi[0]<.815 and lo[2]>.4435 and hi[2]<1.0305
old_front_min=min(v.y for v in pts(old))
assert hi[1]<old_front_min and old_front_min-hi[1]>.0018
plate=tree([shell])
rays=0
sample_materials={'Aqua display','Ghost display','Warm lettering'}
samples=[old[0].matrix_world@old[0].data.vertices[i].co for poly in old[0].data.polygons
          if old[0].data.materials[poly.material_index].name in sample_materials for i in poly.vertices]
assert samples
for eye in ((0,-4,.94),(-2.20,-3,1.24),(2.20,-3,1.24)):
    a=Vector(eye)
    for target in samples:
        d=target-a
        q,*_=plate.ray_cast(a,d.normalized(),d.length-.0001)
        assert q is not None,(eye,list(target))
        rays+=1

proof={'slice':'W3a','catalogHost':'WSC-PROP-027',
       'donorSha256':pin,'insertSha256':hashlib.sha256(raw).hexdigest(),
       'bytes':len(raw),'triangles':tri,'primitives':len(pr),
       'localBoundsBlender':[lo,hi],'clearanceToNearestDonorFaceM':old_front_min-hi[1],
       'oldArtworkOcclusionRays':rays,'cameraPositions':3,
       'initialValues':'All unset; no example numbers in the asset',
       'unsetNode':'RangeRecordUnsetValues','valueSlotsBlender':[[.702,face_y-.004,z] for z in (.779,.659,.552)],
       'readiness':'Separate cosmetic face only; no live record bindings.'}
(out/'w3a-range-record-face-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
if os.environ.get('WSC_METADATA_ONLY')=='1':sys.exit(0)

slate=mat('Dusty basalt plinth',(.082,.095,.104),.78)
ochre=mat('Stand edge',(.29,.105,.037),.71)
demo=mat('Studio drape',(.064,.108,.121),.83)
box('Review plinth',(0,.012,-.165),(2.24,.74,.329),slate,.034)
box('Plinth edge',(0,-.367,-.192),(1.98,.021,.049),ochre,.006)
box('Stage panel',(0,1,1.50),(20,.06,6),demo)
box('Stage floor',(0,0,-.40),(27,22,.10),demo)
lamp=assets/'w11a-record-board-light.glb'
assert hashlib.sha256(lamp.read_bytes()).hexdigest()=='332b05613fd49f57a8887d61e8b5d9e64cad695125e4848366538f63ed1f0860'
ll=load(lamp)
for o in ll:
    if o.parent is None:o.location+=Vector((0,-.12,1.245))

def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()

def area(name,at,target,color,power,size):
    d=bpy.data.lights.new(name,'AREA')
    d.energy,d.color,d.size=power,color,size
    o=bpy.data.objects.new(name,d)
    s.collection.objects.link(o)
    o.location=at
    aim(o,target)

area('Warm daylight',(-2.9,-3.9,4.1),(0,-.25,.6),(1,.80,.59),270,3.2)
area('Cool side light',(3.2,-.6,2.7),(0,0,.7),(.48,.78,1),190,2.0)
area('Fitted shade glow',(0,-.52,1.275),(0,-.34,.70),(1,.67,.32),4,.54)
w=bpy.data.worlds.new('Cool outdoor fill')
s.world=w
w.use_nodes=True
bg=w.node_tree.nodes['Background']
bg.inputs[0].default_value=(.20,.31,.40,1)
bg.inputs[1].default_value=.39
cam=bpy.data.cameras.new('Record face review')
c=bpy.data.objects.new(cam.name,cam)
s.collection.objects.link(c)
s.camera=c
s.render.engine='CYCLES'
s.cycles.samples=48
s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.06
s.view_settings.view_transform='AgX'
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG'
s.render.image_settings.quality=93
for name,pos,t,lens,width,height in [
    ('detail',(0,-2.91,1.05),(0,-.34,.75),50,1280,780),
    ('housing',(2.16,-4.25,2.07),(0,-.19,.47),46,1280,900),
]:
    c.location=pos
    aim(c,t)
    cam.lens=lens
    s.render.resolution_x,s.render.resolution_y=width,height
    s.render.filepath=str(out/f'nov26-w3a-range-record-{name}.jpg')
    bpy.ops.render.render(write_still=True)

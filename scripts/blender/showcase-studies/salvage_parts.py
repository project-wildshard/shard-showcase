"""W2a/E1e salvage display art: two source-derived parts, four proposals."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,export,output_directory

root=Path(__file__).resolve().parents[3]
out=output_directory()
s=bpy.context.scene
clear_scene()
asset_dir=root/'public/assets/wildshard-art'

def sha(path,value):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==value

sha(root/'demos/mite-yard/yard.mjs',
    '7a0b266a4e94b74fe680c74d781311ac12d4d00de72b2872bf736820d0f72edd')
jack=asset_dir/'wsc-actor-002-pallet-jack-study.glb'
sha(jack,'ade8c5099ca6881655782f0f57dc4828bf64d45510bb798cfe1be8c4904a61bc')

def linear(rgb):
    def f(x):return x/12.92 if x<.04045 else ((x+.055)/1.055)**2.4
    return tuple(f((rgb>>n&255)/255) for n in (16,8,0))
def mat(n,rgb,rough=.52,metal=0,em=0,emhex=None):
    m=bpy.data.materials.new(n);m.use_nodes=True
    c=linear(rgb);m.diffuse_color=(*c,1)
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1)
    b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    b.inputs['Emission Color'].default_value=(*(c if emhex is None else linear(emhex)),1)
    b.inputs['Emission Strength'].default_value=em
    return m

iron=mat('Yard dark steel',0x2a3d40,.56,.39)
steel=mat('Yard blue steel',0xa0b2ad,.36,.65)
brown=mat('Yard insulating plug',0x39291d,.68)
copper=mat('Yard copper windings',0xc67a35,.44,.52)
lens=mat('Yard cyan lens',0x46cdd2,.29,.28,1.7,0x15bfc7)
brass=mat('Proposed warm brass',0xb98a53,.35,.65)
blued=mat('Proposed blackened blue steel',0x314e62,.38,.63)
bright=mat('Proposed brushed edge',0xb7bdba,.39,.64)
enamel=mat('Proposed ochre enamel',0xdb9140,.51,.25)
tape=mat('Proposed pale ceramic',0xd9c7a0,.55,.10)
recess=mat('Proposed chassis shadow',0x252b32,.52,.32)

def link(n,data):
    o=bpy.data.objects.new(n,data);s.collection.objects.link(o);return o

def mesh(n,vs,fs,ma):
    d=bpy.data.meshes.new(n);d.from_pydata(vs,[],fs);d.update()
    d.materials.append(ma);return link(n,d)

def bevel(o,wide,segments=1):
    if not wide:return
    bpy.context.view_layer.objects.active=o
    m=o.modifiers.new('Cast edge','BEVEL');m.width=wide;m.segments=segments
    bpy.ops.object.modifier_apply(modifier=m.name)

def box(n,ma,p,d,r=0,yaw=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.scale=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(ma);bevel(o,r)
    o.rotation_euler.z=yaw
    return o

def axial(n,ma,r,h,z,sides=10):
    # Three's CylinderGeometry uses sin(theta) for X and cos(theta) for Z.
    # The game-to-Blender rotation maps that positive Z to negative Y.
    xy=[(r*math.sin(math.tau*i/sides),-r*math.cos(math.tau*i/sides)) for i in range(sides)]
    vv=[(x,y,z+k*h/2) for k in (-1,1) for x,y in xy]
    fs=[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]
    fs.extend((i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides))
    return mesh(n,vv,fs,ma)

def ring(n,ma,spec,sides=20,cap=True):
    # Closed multiring surface: profile points (radius, height).
    pts=[(r*math.cos(i*math.tau/sides),r*math.sin(i*math.tau/sides),z)
         for r,z in spec for i in range(sides)]
    nrows=len(spec); fs=[]
    for j in range(nrows if cap else nrows-1):
        k=(j+1)%nrows
        fs.extend((j*sides+i,j*sides+(i+1)%sides,k*sides+(i+1)%sides,k*sides+i) for i in range(sides))
    return mesh(n,pts,fs,ma)

def join(n,items):
    bpy.ops.object.select_all(action='DESELECT')
    for o in items:o.select_set(True)
    bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join()
    o=items[0];o.name=n;o.data.name=n;return o

def points(o):return [o.matrix_world@v.co for v in o.data.vertices]

def bounds(vv):
    return [[min(p[i] for p in vv) for i in range(3)],[max(p[i] for p in vv) for i in range(3)]]

def center_pivot(o):
    # Keep the artist exports at their real study size, centered laterally
    # and vertically at the bottom, without mutating source GLB donors.
    bpy.context.view_layer.update()
    v=points(o)
    lo,hi=bounds(v)
    off=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]))
    o.data.transform(Matrix.Translation(-off)@o.matrix_world)
    o.matrix_world=Matrix.Identity(4)
    return lo,hi

parts={}
servo=[axial('Servo cylinder',iron,.092,.23,0)]
servo += [axial('End flange',steel,.132,.041,y) for y in (-.105,.105)]
servo += [axial('Copper winding',copper,.107,.019,y) for y in (-.067,-.034,0,.034,.067)]
servo += [axial('Cyan cap',lens,.068,.018,.135),
          box('Plug block',brown,(.12,0,-.016),(.077,.112,.085))]
parts['Servo']=join('Servo',servo)
ss=bounds(points(parts['Servo']))
assert abs(ss[1][2]-ss[0][2]-.2695)<1e-6
assert abs(ss[1][0]-.1585)<1e-6

prior=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(jack));bpy.context.view_layer.update()
tine=bpy.data.objects['Tapered steel fork']
donor_v=points(tine)
assert len({tuple(round(x,5) for x in v) for v in donor_v})==16
assert abs(bounds(donor_v)[1][1]-bounds(donor_v)[0][1]-1.19)<1e-6
tine.name='Tine';tine.data.name='Tine'
for o in set(s.objects)-prior-{tine}:bpy.data.objects.remove(o,do_unlink=True)
parts['Tine']=tine

# Proposals follow the enemy roles and silhouettes, not unseen donor details.
rotor=[ring('Rotor hollow hub',blued,[(.052,.018),(.059,.026),(.059,.061),(.050,.073),
         (.021,.073),(.018,.065),(.018,.023),(.026,.018)],18)]
for i in range(3):
    a=math.tau*i/3
    body=box('Swept rotor arm',bright,(.094*math.cos(a),.094*math.sin(a),.041),
             (.106,.037,.022),.007,a+.25)
    b=a+.29
    rotor.extend((body,box('Bronze rotor tip',brass,(.147*math.cos(b),.147*math.sin(b),.046),
                (.083,.027,.017),.006,b+.35)))
for i in range(3):
    a=i*math.tau/3
    r=axial('Hub screws',enamel,.008,.009,.074,6);r.location=(.037*math.cos(a),.037*math.sin(a),0);rotor.append(r)
parts['Rotor']=join('Rotor',rotor)

nozzle=[
    ring('Nozzle tapered heat shield',blued,[(.071,.006),(.075,.016),(.074,.042),(.048,.101),
            (.039,.165),(.061,.180),(.061,.200),(.053,.207),(.029,.207),(.026,.192),
            (.032,.135),(.033,.008)],18),
    ring('Nozzle brass lower collar',brass,[(.075,.016),(.081,.023),(.081,.035),(.075,.039)],16),
    ring('Nozzle brass upper ferrule',brass,[(.055,.182),(.064,.187),(.064,.198),(.057,.203)],16),
]
for j in range(6):
    a=j*math.tau/6
    nozzle.append(box('Heat shield rail',iron,(.047*math.cos(a),.047*math.sin(a),.091),
                      (.018,.017,.056),.003,a))
parts['Nozzle']=join('Nozzle',nozzle)
parts['Nozzle'].data.transform(Matrix.Diagonal((.83,.83,1.26,1)))

plate=[
    box('Plate center',iron,(0,0,.023),(.270,.224,.046),.021),
    box('Plate flange',bright,(0,0,.043),(.225,.179,.022),.016),
    box('Dressed plate inset',blued,(0,0,.056),(.132,.116,.014),.011),
]
for x in (-.093,.093):
    for y in (-.067,.067):
        o=axial('Rivet dome',brass,.017,.016,.061,8);o.location=(x,y,0);plate.append(o)
for k in range(3):
    plate.append(box('Key slots',recess,(0,(-1+k)*.027,.066),(.086,.010,.006),.001))
parts['Rivet plate']=join('Rivet plate',plate)
parts['Rivet plate'].data.transform(Matrix.Diagonal((1.16,.81,1,1)))

def tubes(n,ma,rows,width=.012):
    path=bpy.data.curves.new(n,'CURVE')
    path.dimensions='3D';path.resolution_u=1
    path.bevel_depth=width;path.bevel_resolution=0
    path.use_fill_caps=True
    for vv in rows:
        b=path.splines.new('POLY');b.points.add(len(vv)-1)
        for p,v in zip(b.points,vv):p.co=(*v,1)
    path.materials.append(ma)
    o=link(n,path)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    return bpy.context.object

coil=[]
coil.append(tubes('Arc collector U',blued,[[(.104*math.cos(a),.105*math.sin(a),.034)
                    for a in [math.radians(20)+i*math.radians(320)/22 for i in range(23)]]],.018))
rings=[]
for radius in (.029,.039):
    rings.append([(.101*math.cos(a)+radius*math.cos(a)*math.cos(12*a),
                   .101*math.sin(a)+radius*math.sin(a)*math.cos(12*a),
                   .038+radius*math.sin(12*a))
                  for a in [math.radians(29)+i*math.radians(302)/96 for i in range(97)]])
coil.append(tubes('Copper windings',copper,rings,.0055))
for y in (-.039,.039):
    coil.extend((box('Arc ceramic jaw',tape,(.101,y,.041),(.043,.032,.043),.006),
                 box('Arc brass terminal',enamel,(.137,y,.039),(.043,.019,.023),.003),
                 box('Arc turquoise cut',lens,(.145,y,.056),(.025,.012,.005),.001)))
parts['Arc coil']=join('Arc coil',coil)

source_bounds={name:center_pivot(o) for name,o in parts.items()}
assert abs(source_bounds['Tine'][1][1]-source_bounds['Tine'][0][1]-1.19)<1e-6
for i,o in enumerate(parts.values()):
    o.location=(1.6*(i%3-1),1.05*(1-i//3),0)
dst=out/'w2a-salvage-parts.glb'
export(list(parts.values()),dst)
raw=dst.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tri=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])
assert len(doc['nodes'])==len(doc['meshes'])==6 and len(raw)<250000 and tri<5000,(len(raw),tri)
assert not any(doc.get(k) for k in ('images','skins','animations','extensionsRequired'))
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(dst));bpy.context.view_layer.update()
parts={name:bpy.data.objects[name] for name in parts}
for name,o in parts.items():
    lo,hi=source_bounds[name]
    boxlo,boxhi=bounds(points(o))
    assert max(abs((hi[i]-lo[i])-(boxhi[i]-boxlo[i])) for i in range(3))<.00002
    assert abs(boxlo[2])<.00002

# Orient the exact same meshes the same way in the lit and silhouette sheets.
angles={'Servo':(40,9,-25),'Tine':(15,31,-42),'Rotor':(9,8,-8),
        'Nozzle':(63,-18,28),'Rivet plate':(17,-15,-24),'Arc coil':(14,0,-29)}
sizes={'Servo':.95,'Tine':1.35,'Rotor':1.08,'Nozzle':.95,'Rivet plate':1.06,'Arc coil':1.08}
def set_pose(o,name,px,py,pz):
    rotate=Matrix.Rotation(math.radians(angles[name][2]),4,'Z')@Matrix.Rotation(math.radians(angles[name][1]),4,'Y')@Matrix.Rotation(math.radians(angles[name][0]),4,'X')
    pts=[rotate@v.co for v in o.data.vertices];lo,hi=bounds(pts)
    k=sizes[name]/max(hi[0]-lo[0],hi[1]-lo[1])
    p=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]))
    o.matrix_world=Matrix.Translation((px,py,pz))@Matrix.Scale(k,4)@Matrix.Translation(-p)@rotate

def camat(cam,p,q):
    cam.location=p;cam.rotation_euler=(Vector(q)-cam.location).to_track_quat('-Z','Y').to_euler()

c=bpy.data.cameras.new('PACK review');cam=link(c.name,c);s.camera=cam
c.type='ORTHO'
s.render.engine='CYCLES';s.cycles.samples=14;s.cycles.use_denoising=False
s.render.resolution_percentage=100
s.render.film_transparent=True
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.world=bpy.data.worlds.new('Studio sky');s.world.color=(.19,.23,.29)
c.ortho_scale=1.65
s.render.resolution_x=s.render.resolution_y=48
s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGBA'
alpha_masks=[]
for name,o in parts.items():
    for other in parts.values():other.hide_render=other!=o
    set_pose(o,name,0,0,0)
    camat(cam,(0,-.25,4.8),(0,0,0))
    file=out/('mask-'+name.lower().replace(' ','-')+'.png')
    s.render.filepath=str(file);bpy.ops.render.render(write_still=True)
    image=bpy.data.images.load(str(file),check_existing=False)
    mask={i for i,val in enumerate(image.pixels[:][3::4]) if val>=.50}
    assert 140<len(mask)<1450,(name,len(mask))
    alpha_masks.append((name,mask))
    bpy.data.images.remove(image)
deltas={a+' / '+b:round(len(ma&mb)/len(ma|mb),4) for (a,ma),(b,mb) in itertools.combinations(alpha_masks,2)}
assert max(deltas.values())<.76,deltas

# Orthographic studio layout. Large captions are review context only and
# the small masks give a separate reproducible PACK-scale check.
def area(n,p,q,e,color,size):
    d=bpy.data.lights.new(n,'AREA');d.energy=e;d.color=color;d.shape='DISK';d.size=size
    o=link(n,d);camat(o,p,q);return o
def flat(n,rgb):
    m=bpy.data.materials.new(n);m.use_nodes=True
    nodes=m.node_tree.nodes;nodes.clear()
    v=nodes.new('ShaderNodeEmission');v.inputs['Color'].default_value=(*linear(rgb),1)
    o=nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(v.outputs[0],o.inputs[0]);return m
font=flat('Caption white',0xede4ce)
dim=flat('Caption subdued',0x86a0aa)
matte=flat('Silhouette',0x10171d)
panel=mat('Slate cards',0x344853,.77)
canvas=mat('Studio background',0x1b272c,.84)
pale=flat('Mask cards',0xe4d8bb)
plain=flat('Mask backdrop',0x1a242b)
def label(txt,x,y,size,ma,align='CENTER'):
    c=bpy.data.curves.new(txt,'FONT');c.body=txt;c.size=size;c.align_x=align;c.align_y='CENTER';c.materials.append(ma)
    o=link(txt,c);o.location=(x,y,.038)

base=box('Contact board',canvas,(0,0,-.07),(40,40,.1))
cards=[]
for i,(name,ob) in enumerate(parts.items()):
    xx=(i%3-1)*2.14;yy=(.51-i//3)*1.875
    ob.hide_render=False
    set_pose(ob,name,xx,yy+.12,.04)
    cards.append(box('Contact cell',panel,(xx,yy,-.032),(2.035,1.745,.08),.07))
    label(name.upper(),xx,yy-.625,.177,font)
    label(('YARD SOURCE','JACK FORK','CONCEPT','CONCEPT','CONCEPT','CONCEPT')[i],
          xx,yy-.812,.094,dim)
label('WILDSHARD / SALVAGE PARTS',-3.05,2.18,.22,font,'LEFT')
label('W2A / PACK READABILITY',-3.05,1.94,.107,dim,'LEFT')
area('Large studio key',(-3.8,-5.6,7),(0,0,.1),435,(1,.83,.62),6)
area('Cool edge',(4.3,3.2,6.7),(0,0,.15),375,(.56,.79,1),6)
s.render.film_transparent=False
s.cycles.samples=28
s.render.resolution_x,s.render.resolution_y=1540,1130
s.render.image_settings.file_format='JPEG';s.render.image_settings.color_mode='RGB';s.render.image_settings.quality=91
c.ortho_scale=6.62
camat(cam,(0,-.40,10),(0,.32,0))
s.render.filepath=str(out/'nov24-salvage-contact.jpg');bpy.ops.render.render(write_still=True)

for ob in parts.values():
    ob.data.materials.clear();ob.data.materials.append(matte)
for ob in cards:ob.data.materials[0]=pale
base.data.materials[0]=plain
for ob in s.objects:
    if ob.type=='FONT' and ob.name.isupper() and ob.data.body in {k.upper() for k in parts}:
        ob.data.materials[0]=matte
    if ob.type=='FONT' and ob.data.body in ('YARD SOURCE','JACK FORK','CONCEPT'):
        ob.data.materials[0]=matte
s.render.filepath=str(out/'nov24-salvage-masks.jpg');bpy.ops.render.render(write_still=True)

(out/'validation.json').write_text(json.dumps({
    'glb_bytes':len(raw),'triangles':tri,'geometry_parts':list(parts),
    'source_derived':['Servo','Tine'],'new_concepts':['Rotor','Nozzle','Rivet plate','Arc coil'],
    'source_bounds_blender_m':source_bounds,'thumbnail_pixels':[48,48],
    'occupied_pixels':{name:len(mask) for name,mask in alpha_masks},
    'maximum_pair_mask_iou':max(deltas.values()),'runtime_pack':False,
},indent=2)+'\n')

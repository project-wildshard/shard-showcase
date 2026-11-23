"""Reusable W0b wall/corner/trim pieces and two stacked facades."""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

assets=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art'
out=output_directory()
dst=out/'wsc-arch-003-town-facade-grid.glb'
s=bpy.context.scene
clear_scene()
buckets=defaultdict(lambda:([],[]))

def mat(n,c,rough=.79):
    m=bpy.data.materials.new(n)
    m.diffuse_color=(*c,1)
    m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1)
    b.inputs['Roughness'].default_value=rough
    return m

stucco=mat('Cream limewash',(.66,.55,.36))
sand=mat('Warm pale ashlar',(.44,.39,.29))
limestone=[mat(f'Limestone shade {i}',c) for i,c in enumerate(((.50,.45,.34),(.55,.46,.32),(.40,.37,.30),(.60,.54,.42)))]
oak=mat('Dark weathered oak',(.245,.126,.058))
ivory=mat('Chamfered pale limestone',(.58,.50,.37))
soil=mat('Warm Gray Mortar',(.218,.231,.206))

def box(group,m,x,y,z,w,d,h):
    vs,fs=buckets[(group,m)]
    a=len(vs)
    vs.extend((x+i*w/2,y+j*d/2,z+k*h/2) for k in (-1,1) for j in (-1,1) for i in (-1,1))
    fs.extend(tuple(a+i for i in face) for face in ((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)))

W,D,H=4.4,4.0,3.1
THICK=.2
box('Wall',stucco,0,.1,H/2,W,THICK,H)
box('Plinth',sand,0,-.013,.22,W,.065,.44)
for course in range(4):
    cuts=[-2.20]+[-2.2+(k+.5*(course%2))*.55 for k in range(1,8)]+[2.2]
    for n,(l,r) in enumerate(zip(cuts,cuts[1:])):
        box('Plinth',limestone[(course*3+n*5)%4],(l+r)*.5,-.065,.06+course*.104,r-l-.013,.12,.089)
box('Plinth',ivory,0,-.06,.46,W,.21,.071)
for row in range(8):
    l=.28 if row%2==0 else .46
    y=.29 if row%2==1 else .46
    z=.19+.37*row
    # Lower-face L made of two adjoining blocks, not intersecting twins.
    box('Turn',limestone[row%4],l/2,-.056,z,l,.17,.324)
    box('Turn',limestone[(row+1)%4],-.056,y/2,z,.17,y,.324)
    box('Turn',ivory,-.073,-.073,z,.136,.136,.324)
for name,pieces in {
    'Stringcourse':[(.17,.125,-.04,sand),(.225,.059,-.07,ivory),(.13,.056,-.103,ivory)],
    'Eave':[(.16,.13,-.048,oak),(.245,.088,-.074,oak),(.29,.06,-.089,ivory)]
}.items():
    for i,(depth,h,y,m) in enumerate(pieces):
        box(name,m,0,y,(i-1)*.062,W,depth,h)

def bake(bevel=.005):
    objs=[]
    for (group,m),(vs,fs) in buckets.items():
        mesh=bpy.data.meshes.new(group)
        mesh.from_pydata(vs,[],fs)
        mesh.materials.append(m)
        mesh.update()
        o=bpy.data.objects.new(group+' / '+m.name,mesh)
        s.collection.objects.link(o)
        if bevel:
            bpy.context.view_layer.objects.active=o
            b=o.modifiers.new('Small chipped edge','BEVEL');b.width=bevel;b.segments=1
            bpy.ops.object.modifier_apply(modifier=b.name)
        objs.append(o)
    buckets.clear()
    return objs

def group(assembled):
    groups=defaultdict(list)
    for o in assembled:
        groups[o.name.split(' / ')[0]].append(o)
    result=[]
    for name,parts in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in parts:o.select_set(True)
        bpy.context.view_layer.objects.active=parts[0]
        bpy.ops.object.join()
        parts[0].name=name
        result.append(parts[0])
    return result

def load(p):
    old=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    bpy.context.view_layer.update()
    return sorted((o for o in set(s.objects)-old if o.type=='MESH'),key=lambda o:o.name)

made=group(bake())
export(made,dst)
for o in made:
    bpy.data.objects.remove(o,do_unlink=True)
components={o.name:o for o in load(dst)}
assert set(components)=={'Wall','Plinth','Turn','Stringcourse','Eave'}
raw=dst.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
tri=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])
assert len(raw)<175000 and tri<3800 and not any(doc.get(k) for k in ('images','skins','animations'))
def limits(items):
    vs=[o.matrix_world@v.co for o in items for v in o.data.vertices]
    return [[fn(p[i] for p in vs) for i in range(3)] for fn in (min,max)]
lo,hi=limits([components['Wall']])
assert max(abs(a-b) for a,b in zip(lo+hi,[-W/2,0,0,W/2,THICK,H]))<1e-6
# For side spans, depth minus two wall thicknesses. Side wall ends meet
# front/back's inner faces, with no unintended volume overlap at the seams.
SIDE=(D-2*THICK)/W
assert abs(D/2-THICK-W*SIDE/2)<1e-6

def place(parts,p,yaw=0,scale=(1,1,1),tag=''):
    t=Matrix.Translation(p)@Matrix.Rotation(math.radians(yaw),4,'Z')@Matrix.Diagonal((*scale,1))
    result=[]
    for src in parts:
        o=bpy.data.objects.new(tag+' '+src.name,src.data)
        s.collection.objects.link(o)
        o.matrix_world=t@src.matrix_world
        result.append(o)
    return result

SHAS={
    'door':('wsc-module-028-town-arched-timber-doorway','a28bfb7e9e71dcb334403e3a248ec5dc6627a6013703d7915a3c63f6325b1505'),
    'window':('window-shutter-module','72823a28c501c92d3494959191ca7b62ae10446118d847d6136243b7d240b862'),
    'flower':('window-flower-box','6703afee9586cd1850a254727ea7ba0fcab764ccb28189b0b93f7334c93b890a'),
    'planter':('wsc-prop-006-west-flower-tub','b3e4edc0ee2522f017593106f6b1a751213fc3e771b269b7ca9f93e9ac507eb5'),
    'roof':('wsc-module-030-terracotta-gable-roof','7738c17a7b7c2e7b3d9b06552bcdadd1736e1915fec7780ab2a93da4f5b69981'),
}
donors={}
for key,(name,sha) in SHAS.items():
    p=assets/(name+'.glb')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
    donors[key]=load(p)
for o in [*components.values(),*(o for os in donors.values() for o in os)]:
    o.hide_render=True

def unit(name,x,y,levels,yaw=0):
    turn=Matrix.Rotation(math.radians(yaw),3,'Z')
    tag=name
    def local(parts,p,a=0,scale=(1,1,1)):
        return place(parts,Vector((x,y,0))+turn@Vector(p),a+yaw,scale,tag)
    def own(k,p,a=0,scale=(1,1,1)):
        return local([components[k]],p,a,scale)
    for story in range(levels):
        z=story*H
        for xx,yy,a,k in ((0,-D/2,0,1),(0,D/2,180,1),(-W/2,0,-90,SIDE),(W/2,0,90,SIDE)):
            own('Wall',(xx,yy,z),a,(k,1,1))
            if story==0 and a==0:
                # Interrupt the plinth at the unchanged 1.682 m door surround.
                for sign in (-1,1):
                    own('Plinth',(sign*(W+1.71)/4,yy,0),0,((W-1.71)/(2*W),1,1))
            elif story==0:own('Plinth',(xx,yy,0),a,(k,1,1))
            else:own('Stringcourse',(xx,yy,z),a,(k,1,1))
            if story==levels-1:own('Eave',(xx,yy,z+H),a,(k,1,1))
        for xx,yy,a in ((-W/2,-D/2,0),(W/2,-D/2,90),(W/2,D/2,180),(-W/2,D/2,270)):
            own('Turn',(xx,yy,z),a)
        if story:
            local(donors['window'],(-.04,-D/2-.018,z+.71))
            local(donors['flower'],(-.04,-D/2-.19,z+.67),0,(.83,.83,.83))
        if story or levels==2:
            local(donors['window'],(W/2+.018,-.45,z+.72),90,(.74,.74,.74))
    local(donors['door'],(0,-D/2-.09,.015))
    local(donors['planter'],(-1.57,-D/2-.49,.008),12,(.70,.70,.70))
    # The donor underside is at z=0. Place it on the stack, not inside it.
    local(donors['roof'],(0,0,H*levels-.002))

unit('Two-storey street house',-3.20,.35,2,1)
unit('Three-storey return',2.61,1.25,3,-4)
rng=random.Random(321)
for row in range(-11,10):
    for col in range(-16,17):
        box('Paving',rng.choice(limestone),col*.63+(row%2)*.31,row*.40,-.071,.61,.387,.14)
bake(.009)
bpy.ops.mesh.primitive_plane_add(size=180,location=(0,0,-.14))
bpy.context.object.data.materials.append(soil)

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(n,p,q,e,c,sz):
    l=bpy.data.lights.new(n,'AREA')
    l.energy=e;l.color=c;l.shape='DISK';l.size=sz
    o=bpy.data.objects.new(n,l);s.collection.objects.link(o);o.location=p;aim(o,q)
s.world=bpy.data.worlds.new('West soft turquoise bounce')
s.world.color=(.21,.24,.27)
area('Warm direction',(-8,-7,15),(0,0,3),5200,(1,.80,.59),8)
area('Blue sky bounce',(2,2,15),(0,0,4),3900,(.64,.82,1),12)
area('Route fill',(8,-6,9),(0,0,2),2100,(.73,.85,1),11)
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=91
s.render.resolution_percentage=100
cam=bpy.data.cameras.new('W0b facade art')
s.camera=bpy.data.objects.new(cam.name,cam);s.collection.objects.link(s.camera)
cam.type='ORTHO'
def render(key,p,q,scale,wh):
    s.camera.location=p;aim(s.camera,q);cam.ortho_scale=scale
    (s.render.resolution_x,s.render.resolution_y)=wh
    s.render.filepath=str(out/(key+'.jpg'))
    bpy.ops.render.render(write_still=True)
(out/'validation.json').write_text(json.dumps({'asset_id':'WSC-ARCH-003','bytes':len(raw),'triangles':tri,
    'parts':sorted(components),'floor_pitch_m':H,'footprint_m':[W,D],'examples':[2,3],'native':False},indent=2)+'\n')
render('nov23-town-facade-grid',(12,-19,15),(0,.0,4.72),15.3,(1540,1175))
render('nov23-town-facade-corner',(11,-10,9),(3.16,-.04,4.71),7.3,(1160,1020))

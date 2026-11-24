"""Round 5 Gauntlet forecourt, 08F; join new static art to pinned C1."""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,export,output_directory

root=Path(__file__).resolve().parents[3]
out=output_directory()
L=json.loads((root/'project/layouts/wsc-scene-007-forecourt.json').read_text())
X,Y,Z=L['origin_world_xyz']
s=bpy.context.scene
clear_scene()
rng=random.Random(412)
groups=defaultdict(lambda:([],[]))

def p(x,z,y):return Vector((x-X,Z-z,y-Y))

def mat(n,b,rough=.7,metal=0,em=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*b,1);m.use_nodes=True
    q=m.node_tree.nodes['Principled BSDF']
    for k,v in (('Base Color',(*b,1)),('Roughness',rough),('Metallic',metal),
                ('Emission Color',(*b,1)),('Emission Strength',em)):
        q.inputs[k].default_value=v
    return m

concrete=mat('Warm forecourt concrete',(.26,.216,.163))
dust=[mat('Aggregate shade '+str(i),c) for i,c in enumerate((
    (.225,.179,.131),(.268,.219,.174),(.291,.233,.172),(.250,.205,.157)))]
steel=mat('Slate blue steel',(.081,.128,.143),.53,.59)
metal=mat('Narrow rolled rib',(.159,.211,.224),.58,.52)
dark=mat('Deep joint',(.023,.032,.033),.66,.29)
ochre=mat('Burnt orange guidance',(.62,.205,.043),.50,.29)
cream=mat('Pale route paint',(.72,.58,.331))
teal=mat('Petrol enamel',(.033,.112,.149),.55,.33)
mint=mat('Cool ceramic sign readout',(.29,.721,.765),.43,.09,.16)
amber=mat('Warm service lens',(.99,.551,.179),.43,.11,1.5)
charcoal=mat('Road and podium top',(.078,.084,.082))
letters=mat('Warm pale lettering',(.75,.72,.55),.64,.02,.04)

def poly(g,m,vs,fs):
    a,b=groups[(g,m)];off=len(a)
    a.extend(p(*v) for v in vs);b.extend(tuple(off+i for i in f) for f in fs)

def box(g,m,x,z,y,w,d,h,a=0):
    co,si=math.cos(a),math.sin(a)
    v=[(x+co*i*w/2-si*j*d/2,z+si*i*w/2+co*j*d/2,y+k*h/2)
       for k in (-1,1) for j in (-1,1) for i in (-1,1)]
    poly(g,m,v,((1,3,2,0),(6,7,5,4),(4,5,1,0),(3,7,6,2),(2,6,4,0),(5,7,3,1)))

def slab(g,m,a,b,c,d,lo,hi):
    box(g,m,(a+b)/2,(c+d)/2,(lo+hi)/2,b-a,d-c,hi-lo)

slab('Forecourt datum',concrete,*L['forecourt_x0_x1_z0_z1'],-.42,0)
# Forecourt's road turns east within the authored 12 m band. This study
# includes just the first 32 m of the shortcut, not the full 102 m route.
slab('Titan shortcut start',charcoal,98,152,124,136,-.32,.005)
for ix in range(16):
    x1=40+5*ix;x2=x1+5
    for z1,z2 in ((123,127.75),(127.75,132.5),(132.5,137.25),(137.25,142)):
        # Never put cover in the 8 m ramp footprint.
        if x1<66 and x2>58 and z2>132:continue
        if x1>=95 and z1>=123 and z2<=137.25:continue
        slab('Forecourt apron panels',rng.choice(dust),x1+.023,x2-.023,z1+.019,z2-.019,-.022,.008)
for a,b in L['se_openings_x']:
    slab('Portal approach paver',charcoal,a,b,115,123,-.36,0)
for x in range(101,153,3):
    box('Titan road dashes',cream,x,130,.011,1.77,.092,.012)
for q in (124.18,135.82):
    for x in range(105,153,4):
        box('Titan outer edge marking',ochre,x,q,.013,2.9,.11,.016)
for x in (58.5,65.5):
    for z in (118,121,124,127,130):
        box('C1 center approach paint',cream,x,z,.012,.15,1.62,.016)

def wedge(g,cx,z0,z1,w,r):
    a,b=cx-w/2,cx+w/2
    v=[(a,z0,-.31),(b,z0,-.31),(a,z1,-.31),(b,z1,-.31),
       (a,z0,0),(b,z0,0),(a,z1,r),(b,z1,r)]
    poly(g,concrete,v,((1,3,2,0),(6,7,5,4),(4,5,1,0),(3,7,6,2),(2,6,4,0),(5,7,3,1)))
    for x in (a+.15,b-.15):
        poly(g,ochre,[(x-.08,z0,.017),(x+.08,z0,.017),(x+.08,z1-.035,r+.0065),(x-.08,z1-.035,r+.0065)],
             [(3,2,1,0)])
    for i in range(6):
        z=z0+.7+i*1.49;y=(z-z0)/(z1-z0)*r
        bx=cx+(1 if i%2 else -1)*2.54
        box(g,cream,bx,z,y+.017,1.44,.057,.012)
wedge('C1 grade and edge strips',L['ramp_center_x'],*L['ramp_z0_z1'],L['ramp_width_m'],L['ramp_rise_m'])

# Field bays end at exact cuts; jamb fittings occupy the wall outside the
# opening, not the 16 m clearance. Markings use the art's industrial palette.
def wall(g,a,b,z,k=4.55):
    slab(g,steel,a,b,z-.40,z+.40,0,k)
    slab(g,metal,a,b,z-.45,z+.45,k-.13,k+.012)
    slab(g,ochre,a,b,z-.415,z+.415,k-.36,k-.225)
    n=max(1,round((b-a)/2.55))
    for j in range(n):
        x=a+(j+.5)*(b-a)/n
        box(g,metal,x,z,2.36,.14,1.09,4.09)
        box(g,dark,x,z,.31,.63,1.13,.62)
for a,b in ((35,54),(70,100),(116,129)):
    wall('SE dividing wall',a,b,L['se_wall_z'])
for idx,(a,b) in enumerate(L['se_openings_x']):
    g='C1 north portal' if not idx else 'Titan north portal'
    z=L['se_wall_z']
    for x,t in ((a-.54,-1),(b+.54,1)):
        box(g,steel,x,z,2.53,1.068,1.46,5.06)
        box(g,ochre,x,z-.754,2.47,.71,.071,4.74)
        box(g,metal,x,z,4.97,1.068,1.62,.32)
        for zz in (z-.793,z+.793):
            box(g,amber if not idx else mint,x,zz,3.4,.39,.052,.56)
        for i in range(5):
            box(g,dark,x+.21*t,z-.80,.75+.31*i,.095,.039,.12)
    box(g,steel,(a+b)/2,z,5.11,b-a+2.16,1.48,.52)
    box(g,ochre if not idx else teal,(a+b)/2,z-.763,5.11,9.35,.071,.43)
    for x in (a+1.2,b-1.2):
        box(g,amber if not idx else mint,x,z-.765,5.11,1.07,.090,.11)
    for x in (a+.19,b-.19):
        box(g,cream,x,z,.021,.11,2.80,.018)

# Static checkpoint at the pinned datum, outside main route centerlines.
cx,cz=L['checkpoint_xz']
for side in (-1,1):
    box('Checkpoint frame',steel,cx+side*1.46,cz,.42,.34,3.2,.84)
    box('Checkpoint frame',mint,cx+side*1.46,cz,.861,.107,2.90,.048)
    box('Checkpoint frame',ochre,cx,cz+side*1.47,.14,2.58,.28,.28)
box('Checkpoint bed',charcoal,cx,cz,.093,2.57,2.69,.186)
for x in (-.65,0,.65):box('Checkpoint bed',teal,cx+x,cz,.20,.48,2.42,.054)
# Published board width and height follow the R5 9 x 4 plane. Legs and slate
# are illustrative. A blank best time makes the absence of runtime clear.
bx,bz=L['run_board_xz']
by=2.39
box('Run board case',steel,bx,bz,by,9,.61,4)
box('Run board case',dark,bx,bz-.334,by,8.67,.072,3.61)
box('Run board case',teal,bx,bz-.381,by,8.49,.049,3.43)
for x in (-3.44,3.44):
    box('Run board posts',steel,bx+x,bz,.26,.48,.59,.52)
    box('Run board posts',ochre,bx+x,bz,4.37,.14,.39,.12)
for x in (-2,-1,0,1,2):
    box('Run board tile',dark,bx+x,bz-.412,2.18,.67,.025,.64)
    box('Run board tile',mint,bx+x,bz-.431,1.94,.42,.018,.058)
box('Board header rule',mint,bx,bz-.425,2.87,7.78,.025,.041)

def obj(n,d):
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);return o

parts=[]
for (g,ma),(verts,faces) in sorted(groups.items(),key=lambda r:(r[0][0],r[0][1].name)):
    me=bpy.data.meshes.new(g);me.from_pydata(verts,[],faces);me.update();me.materials.append(ma)
    parts.append(obj(g,me))

def lettering(txt,x,z,y,size,m):
    d=bpy.data.curves.new(txt,'FONT');d.body=txt;d.size=size
    d.align_x='CENTER';d.align_y='CENTER';d.resolution_u=4;d.materials.append(m)
    o=obj(txt,d);o.location=p(x,z,y);o.rotation_euler=(math.pi/2,0,math.pi)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    return bpy.context.object

for txt,x,z,y,size,ma in (
    ('C1  /  LOADING YARD',62,121.185,5.1,.36,letters),
    ('TITAN ROAD',108,121.185,5.1,.37,mint),
    ('GAUNTLET',bx,bz-.453,3.34,.52,letters),
    ('05 WAVES',bx,bz-.453,2.61,.255,mint),
    ('BEST TIME   --',bx,bz-.453,1.23,.34,letters),
):
    parts.append(lettering(txt,x,z,y,size,ma))
for j in range(5):
    parts.append(lettering(str(j+1),bx+j-2,bz-.453,2.24,.26,letters))

dst=out/'wsc-scene-007-forecourt.glb'
export(parts,dst)
raw=dst.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n])
tri=sum(doc['accessors'][q['indices']]['count']//3 for m in doc['meshes'] for q in m['primitives'])
assert len(raw)<650000 and tri<13000,(len(raw),tri)
assert not any(doc.get(k) for k in ('images','skins','animations'))

clear_scene();bpy.ops.import_scene.gltf(filepath=str(dst));bpy.context.view_layer.update()
ours=[o for o in s.objects if o.type=='MESH']
def bvh(objs):
    vs,fs=[],[]
    for o in objs:
        start=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
        fs.extend(tuple(start+i for i in f.vertices) for f in o.data.polygons)
    return BVHTree.FromPolygons(vs,fs)

dest=root/'public/assets/wildshard-art/wsc-scene-007-c1-loading-yard.glb'
assert hashlib.sha256(dest.read_bytes()).hexdigest()==L['c1_donor_sha256']
old=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(dest))
c1=set(s.objects)-old
ox,oy,oz=L['c1_origin_world_xyz']
for o in c1:
    if o.parent is None:o.location+=p(ox,oz,oy)
bpy.context.view_layer.update()
F=bvh(ours);C=bvh([o for o in c1 if o.type=='MESH'])
def height(tree,x,z):
    h,_,_,_=tree.ray_cast(p(x,z,12),(0,0,-1),20)
    assert h is not None,(x,z)
    return h.z
heights={}
for x in (58.43,59.2,61,62,63,64.8,65.57):
    run=height(F,x,141.995)
    deck=height(C,x,142.026)
    assert abs(run-2.9985)<.00025 and 0 <= deck-run < .015,(x,run,deck)
    heights[x]=[run,deck]
assert abs(height(F,62,137)-1.5)<.0001
rays=0
for a,b in L['se_openings_x']:
    for k in range(31):
        x=a+.06+(b-a-.12)*k/30
        for h in (.25,1.2,1.8,2.5,3.7):
            assert F.ray_cast(p(x,119,h),(0,-1,0),5)[0] is None,(x,h)
            rays+=1
for x in (58.25,59.78,62,64.22,65.75):
    for t in (.22,.80,1.65,2.25):
        d=p(x,142.7,3+t)-p(x,141.6,2.88+t)
        for tree in (F,C):assert tree.ray_cast(p(x,141.6,2.88+t),d.normalized(),d.length)[0] is None,(x,t)

(out/'validation.json').write_text(json.dumps({
    'bytes':len(raw),'triangles':tri,'gap_rays':rays,'c1_clearance_rays':20,
    'cross_junction_height_samples_m':heights,
    'maximum_visible_height_step_m':max(b-a for a,b in heights.values()),
    'nominal_ramp_angle_degrees':math.degrees(math.atan2(3,10)),
    'c1_unchanged':True,'native_play':False,
},indent=2)+'\n')

def aim(o,where):o.rotation_euler=(where-o.location).to_track_quat('-Z','Y').to_euler()
def stagebox(name,loc,size,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.scale=size;o.data.materials.append(m)
    return o

stagebox('Ground, studio only',p(82,134,-.55),(540,540,1.02),dust[0])
for x,z,w,h in [(129,141,7,4.2),(138,146,8,5.0),(145,120,8,7.4),(153,137,13,4.9),(111,145,9,4.8)]:
    stagebox('Distant shortcut context',p(x,z,h/2),(w,3.7,h),steel)
    stagebox('Distant coping',p(x,z,h-.10),(w+.17,4.0,.24),ochre)
# A north approach, a distinct eastward exit, and a joined diagonal provide
# presentation context. The Titan arena assets are not part of this shot.
world=bpy.data.worlds.new('Southeast sun')
world.use_nodes=True
n=world.node_tree.nodes
sky=n.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_elevation=.37;sky.sun_rotation=1.73
sky.sun_size=.031;sky.sun_intensity=.72
world.node_tree.links.new(sky.outputs['Color'],n['Background'].inputs[0]);n['Background'].inputs[1].default_value=.21
s.world=world
d=bpy.data.cameras.new('Route review');cam=obj('Route review',d);s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=34;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=91
def shot(file,eye,to,wh,lens,ortho=0):
    cam.location=p(*eye);aim(cam,p(*to));d.lens=lens;d.type='ORTHO' if ortho else 'PERSP'
    if ortho:d.ortho_scale=ortho
    s.render.resolution_x,s.render.resolution_y=wh
    s.render.filepath=str(out/(file+'.jpg'));bpy.ops.render.render(write_still=True)
shot('nov24-forecourt-c1',(62,109,1.70),(62,141,2.65),(1390,900),24)
shot('nov24-forecourt-titan',(101.5,107.5,1.70),(122,133,2.38),(1390,900),23)
shot('nov24-forecourt-overview',(158,91,97),(87,144,1.8),(1510,1020),38,148)
shot('nov24-forecourt-board',(85,123.6,1.70),(86,129.68,2.5),(1180,850),21)

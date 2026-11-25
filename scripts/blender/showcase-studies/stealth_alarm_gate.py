"""E5b visual alarm gates in the exact Round 5 north and west map openings."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import output_directory, clear_scene

out=output_directory()
clear_scene()
s=bpy.context.scene
repo=Path(__file__).resolve().parents[3]
names=['e5b-alarm-gate-leaf','e5b-alarm-signal']
origin={'north':[148,0,14], 'west':[126,0,66]}
pocket=8.12
seat=.015

def make_mat(n,c,metal=.5,rough=.55,e=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    q=m.node_tree.nodes.get('Principled BSDF')
    for k,v in {'Base Color':(*c,1),'Metallic':metal,'Roughness':rough,
                'Emission Color':(*c,1),'Emission Strength':e}.items():q.inputs[k].default_value=v
    return m

iron=make_mat('Worn volcanic black',(.039,.066,.069),.62)
steel=make_mat('Blued corrugated steel',(.135,.224,.237),.56)
edge=make_mat('Rain-brushed zinc',(.27,.36,.37),.65,.37)
copper=make_mat('Closure-edge saffron enamel',(.68,.22,.04),.37)
cyan=make_mat('Unlocked cyan',(.019,.40,.48),.22,.29,1.5)
alarm=make_mat('Red alarm',(.84,.037,.014),.23,.31,2.1)
dim=make_mat('Inactive smoke lens',(.047,.068,.067),.08,.48)
slab=make_mat('Wet asphalt',(.075,.085,.089),.16,.38)
night=make_mat('Blue wall sheet',(.073,.111,.114),.46,.67)
fog=make_mat('Concrete footing',(.134,.142,.137),.1)
cream=make_mat('Traffic stencil',(.52,.50,.37),.1)
road=make_mat('Worn tar patch',(.095,.108,.105),.13,.55)

def assign(o,n,m):
    o.name=n;o.data.materials.append(m);return o

def box(n,p,d,m,b=.030):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    assign(o,n,m)
    if b:
        v=o.modifiers.new('Rain catch bevel','BEVEL')
        v.width=min(b,min(d)*.34);v.segments=1
    return o

def cylinder(n,x,y,z,depth,r,m,verts=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=(x,y,z),rotation=(math.pi/2,0,0))
    return assign(bpy.context.object,n,m)

def beam(n,a,b,width,depth,m):
    a,b=Vector(a),Vector(b);d=b-a
    o=box(n,(a+b)*.5,(width,depth,d.length),m)
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return o

def group(n,parts):
    g=bpy.data.objects.new(n,None);s.collection.objects.link(g)
    bpy.context.view_layer.update()
    for o in parts:
        q=o.matrix_world.copy();o.parent=g;o.matrix_world=q
    return g

def mark(body,loc,size,mat):
    f=bpy.data.curves.new(body,'FONT');f.body=body;f.align_x=f.align_y='CENTER'
    f.size=size;f.materials.append(mat)
    o=bpy.data.objects.new(body,f);s.collection.objects.link(o);o.location=loc
    o.rotation_euler.x=math.pi/2
    return o

def publish(n,groups):
    bpy.ops.object.select_all(action='DESELECT')
    for g in groups:
        g.select_set(True)
        for o in g.children_recursive:o.select_set(True)
    path=out/(n+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',
                              use_selection=True,export_apply=True,export_animations=False,export_texcoords=False)
    b=path.read_bytes()
    assert struct.unpack_from('<4sII',b)==(b'glTF',2,len(b)) and len(b)<120000
    d=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
    t=sum(d['accessors'][p['indices']]['count']//3 for m in d['meshes'] for p in m['primitives'])
    return dict(bytes=len(b),triangles=t,sha256=hashlib.sha256(b).hexdigest())

# The stand-alone leaf is opaque. Positive local X has the safety meeting edge.
leaf=[box('Continuous opaque back',(0,0,1.93),(7.98,.20,3.86),steel,.021)]
for z in [.20,1.97,3.67]:
    leaf.append(box('Folded transverse rail',(0,-.17,z),(7.94,.22,.19),iron))
for x in [-3.81,-2.56,-1.28,0,1.28,2.56]:
    leaf.append(box('Pressed vertical hat',(x,-.12,1.935),(.105,.21,3.38),edge,.018))
for x in [-3.883,3.883]:
    leaf.append(box('Meeting post' if x>0 else 'Guide post',(x,-.098,1.925),(.20,.385,3.85),copper if x>0 else iron))
for x in [-3.25,.26]:
    leaf.append(beam('Reverse face rake',(x,.118,.53),(x+2.6,.118,3.43),.159,.13,iron))
for x in [-3.72,-.13,3.76]:
    for z in [.26,3.58]:
        leaf.append(cylinder('Pressed hex fastener',x,-.286,z,.033,.052,edge,6))
leaf_group=group('Alarm_leaf_floor_origin',leaf)
report={names[0]:publish(names[0],[leaf_group])}
clear_scene()

base=[box('Brow light shroud',(0,0,.47),(.47,.44,.96),iron),
      box('Slotted roof',(0,-.045,.94),(.54,.50,.083),copper),
      box('Post bracket',(0,.225,.40),(.30,.15,.54),edge)]
for z in [.23,.64]:
    base.append(box('Lens flange',(0,-.231,z),(.356,.091,.31),edge))
    for x in [-.154,.154]:
        base.append(cylinder('Lamp backing bolt',x,-.284,z,.022,.018,iron,6))
signal_housing=group('Alarm_signal_mount',base)
upper=group('Closed_red_lens',[box('Red square lens',(0,-.301,.64),(.229,.079,.197),alarm)])
lower=group('Clear_cyan_lens',[cylinder('Cyan round lens',0,-.301,.23,.074,.105,cyan)])
report[names[1]]=publish(names[1],[signal_housing,upper,lower])
clear_scene()

def read(n):
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(out/(n+'.glb')))
    return set(s.objects)-before

first=read(names[0])
src=next(o for o in first if o.type=='EMPTY' and not o.parent)
second=read(names[0])
other=next(o for o in second if o.type=='EMPTY' and not o.parent)
lights=read(names[1])
for o in lights:
    if o.parent is None:o.location+=Vector((8.35,-1.08,3.32))
reds=[o for o in lights if o.type=='MESH' and any('Red alarm' in m.name for m in o.data.materials)]
blues=[o for o in lights if o.type=='MESH' and any('Unlocked cyan' in m.name for m in o.data.materials)]
assert reds and blues
def pose(closed):
    # Right leaf is mirrored by a true 180-degree rotation, not negative scale.
    step=0 if closed else pocket
    src.location=(-3.99-step,0,seat);other.location=(3.99+step,0,seat)
    other.rotation_mode='XYZ'
    other.rotation_euler=(0,0,math.pi)
    bpy.context.view_layer.update()
    assert (other.matrix_world.to_3x3()@Vector((1,0,0))).x<-.99999

def inspect(closed):
    pose(closed)
    pts, faces=[],[]
    for o in sorted(first|second,key=lambda obj:obj.name):
        if o.type!='MESH':continue
        k=len(pts)
        pts.extend(o.matrix_world@v.co for v in o.data.vertices)
        o.data.calc_loop_triangles()
        faces.extend(tuple(k+v for v in tri.vertices) for tri in o.data.loop_triangles)
    tree=BVHTree.FromPolygons(pts,faces,all_triangles=True)
    xz=[(x,z) for x in [i*.3 for i in range(-26,27)] for z in [.22,.82,1.40,1.95,2.88,3.76]]
    hit=sum(tree.ray_cast(Vector((x,-3,z)),Vector((0,1,0)),6)[0] is not None for x,z in xz)
    left=max((o.matrix_world@v.co).x for o in first if o.type=='MESH' for v in o.data.vertices)
    right=min((o.matrix_world@v.co).x for o in second if o.type=='MESH' for v in o.data.vertices)
    assert hit==(len(xz) if closed else 0),(hit,closed,left,right)
    assert (right-left<.002) if closed else (right-left>16)
    return {'rays':len(xz),'hits':hit,'between_leaves_m':round(right-left,5)+0.0}

receipt={'slice':'E5b','catalogue_id':'WSC-KIT-006','assets':report,
         'origins_world_xyz':origin,'north_yaw_degrees':180,'west_yaw_degrees':-90,
         'original':'ce1cf050b3 round-5-blockout/layout.js, YARD_GATES; z=14 and x=126 perimeter',
         'test':'One local reusable leaf pair; x-width invariant under 90 degree rotation. Both sampled endpoints only.',
         'travel_per_leaf_m':pocket,'open':inspect(False),'closed':inspect(True),
         'not_shipped':['alarm state', 'lock timer', 'actor detection', 'player collision', 'keycard or quests']}
(out/'fit.json').write_text(json.dumps(receipt,indent=2)+'\n')

# North cutaway scene: not a replacement for the full yard and its corner beacons.
box('Wet approach',(0,0,-.26),(60,58,.52),slab,.035)
for sign in [-1,1]:
    for i in range(13):
        x=sign*(8.14+i*1.10)
        box('Perimeter corrugated bay',(x,.59,2.07),(1.09,.37,4.14),night if i%4 else steel,.04)
        for r in [-.35,0,.35]:
            box('Seam ridge',(x+r,.36,2.10),(.039,.105,3.93),iron,.013)
    box('Perimeter coping',(sign*15.10,.59,4.17),(14.45,.43,.15),iron)
    x=sign*8.26
    box('Stamped guide tower',(x,-.73,2.15),(.49,.72,4.30),edge)
    box('Footing',(x,-.79,.15),(.51,.84,.30),fog)
    box('Stub cap',(x,-.73,4.32),(.52,.73,.13),copper)
    for y in [-7.7,-3.4,2.6,6.2]:
        box('Broken road boundary',(sign*5.9,y,.006),(.13,2.12,.012),cream,.002)
for x in range(-7,8,2):
    box('Closure approach bars',(x,-2,.006),(1.26,.19,.012),copper,.002)
    box('Drain',(x,.77,.005),(1.55,.20,.010),iron,.002)
for i,(x,y) in enumerate([(-4,-8),(-1,-5),(4,-9),(-1,6),(2,12),(7,1)]):
    box('Worn wet patch',(x,y,.001),(1.8+i*.18,1.2+i*.19,.002),road,.0005)
box('North wall placard',(9.32,-.31,2.44),(1.55,.11,.79),iron)
mark('BAND 5',(9.32,-.374,2.58),.31,cream)
mark('NORTH',(9.32,-.374,2.26),.232,cream)
container=repo/'public/assets/wildshard-art/wsc-prop-058-shipping-container.glb'
assert hashlib.sha256(container.read_bytes()).hexdigest()=='8bd1c2bca075256315a8bf5a76b5da489b3e42fca0def63d06088031695232af'
for x,y,yaw in [(-3.4,9,0),(-6.6,14,15),(5.65,9,-7)]:
    before=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(container))
    for o in set(s.objects)-before:
        if o.parent is None:
            o.matrix_world=Matrix.Translation((x,y,0))@Matrix.Rotation(math.radians(yaw),4,'Z')@o.matrix_world
for x in [-7.1,7.1]:
    box('Wheel channel',(x,0,.028),(1.8,.1,.056),edge)
# Render context only: the two GLBs do not contain procedural materials.
for m in [slab,road,night]:
    nt=m.node_tree; bs=nt.nodes.get('Principled BSDF')
    tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3 if m==night else 38
    tex.inputs['Detail'].default_value=2.3
    texcoord=nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(texcoord.outputs['Object'],tex.inputs['Vector'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.24
    bump.inputs['Distance'].default_value=.022
    nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
camd=bpy.data.cameras.new('Paired wet gate views');s.camera=bpy.data.objects.new(camd.name,camd)
s.collection.objects.link(s.camera);camd.lens=44
def aim(o,q):o.rotation_euler=(Vector(q)-o.location).to_track_quat('-Z','Y').to_euler()
s.camera.location=(3.15,-25.0,6.65); aim(s.camera,(.50,0,2.40))
def area(n,p,q,e,c,size):
    m=bpy.data.lights.new(n,'AREA');m.energy=e;m.color=c;m.size=size
    o=bpy.data.objects.new(n,m);s.collection.objects.link(o);o.location=p;aim(o,q)
s.world=bpy.data.worlds.new('Crushed dusk sky');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.29,.45,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.32
area('Cool sky key',(0,-11,13),(0,1,1),5500,(.57,.77,1),14)
area('Industrial yard bounce',(1,11,8),(0,0,1),3600,(1,.62,.32),8)
area('Cold edge',(-16,-5,7),(0,0,2),4100,(.53,.81,1),7)
s.render.engine='CYCLES';s.cycles.samples=52;s.cycles.adaptive_threshold=.050;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_x=1380;s.render.resolution_y=880;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=92
for state,closed in [('clear',False),('alarm',True)]:
    pose(closed)
    for o in reds+blues:
        bright=o in reds if closed else o in blues
        for slot in o.material_slots:
            slot.material=(alarm if o in reds else cyan) if bright else dim
    s.render.filepath=str(out/('e5b-north-'+state+'.jpg'))
    bpy.ops.render.render(write_still=True)

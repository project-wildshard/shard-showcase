"""Westbound W10b study; exact R02 gantry, timer and opening ring."""
import hashlib
import json
import math
import random
import struct
import sys
from pathlib import Path

import bmesh
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

root=Path(__file__).resolve().parents[3]
out=output_directory()
clear_scene()
s=bpy.context.scene
donors=json.loads((root/'project/layouts/w10b-riding-course-study.json').read_text())
history='Raynos/project-wildshard-singleplayer@ce1cf050b36fa236155ac26d43e721b9012c49df'
board_pos=(-80,137,0)
cue_pos=(-75.6,141.1,0)
cue_yaw=90
ring=donors['rings']['placements'][1]
assert ring['number']==2 and ring['origin_blender_m'][:2]==[-105,148]
assert donors['timer']['gantry_blender_xy_m']==[-80,148]

def mat(name,c,rough=.65,metal=0.):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    q=m.node_tree.nodes.get('Principled BSDF')
    for k,v in {'Base Color':(*c,1),'Roughness':rough,'Metallic':metal}.items():q.inputs[k].default_value=v
    return m

def grain(m,c,scale):
    q=m.node_tree.nodes; link=m.node_tree.links
    n=q.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale
    uv=q.new('ShaderNodeTexCoord')
    link.new(uv.outputs['Object'],n.inputs['Vector'])
    ramp=q.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.19
    ramp.color_ramp.elements[0].color=(*(v*.65 for v in c),1)
    ramp.color_ramp.elements[1].position=.81
    ramp.color_ramp.elements[1].color=(*(v*1.23 for v in c),1)
    link.new(n.outputs['Fac'],ramp.inputs[0]); link.new(ramp.outputs[0],q.get('Principled BSDF').inputs['Base Color'])
    bump=q.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.23;bump.inputs['Distance'].default_value=.032
    link.new(n.outputs['Fac'],bump.inputs['Height']);link.new(bump.outputs[0],q.get('Principled BSDF').inputs['Normal'])

wood=mat('Tobacco stain',(.22,.097,.038))
back=mat('Sawcut oak',(.35,.174,.062))
bronze=mat('Antique ironwork',(.095,.13,.117),.48,.64)
cream=mat('Hand-letter ivory enamel',(.79,.713,.464),.48,.07)
green=mat('Forest green enamel',(.036,.156,.103),.60,.21)
black=mat('Blank graphite readout',(.025,.052,.039),.78,.12)
stone=mat('Fieldstone ballast',(.22,.22,.165))
sand=mat('Trodden amber clay',(.30,.167,.079),.85)
meadow=mat('Late summer meadow',(.16,.23,.071),.85)
apron=mat('Crushed quartz apron',(.224,.206,.143),.86)
wear=mat('Burnished track line',(.355,.215,.104),.77)

def box(n,p,d,m,b=.018):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d;o.data.materials.append(m)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if b:
        v=o.modifiers.new('Tool soft edge','BEVEL');v.width=min(b,min(d)*.30);v.segments=1
    return o

def bolt(x,y,z):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.037,depth=.033,location=(x,y,z),rotation=(math.pi/2,0,0))
    o=bpy.context.object;o.name='Cut iron peg';o.data.materials.append(bronze);return o

def glyph(body,p,sz,m):
    d=bpy.data.curves.new(body,'FONT');d.body=body;d.size=sz
    d.align_x=d.align_y='CENTER';d.materials.append(m)
    o=bpy.data.objects.new(body,d);s.collection.objects.link(o);o.location=p;o.rotation_euler.x=math.pi/2
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=1e-6)
    bmesh.ops.triangulate(bm,faces=bm.faces[:])
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-9],context='FACES_ONLY')
    bm.to_mesh(o.data);bm.free();return o

def mesh(n,vs,faces,m):
    d=bpy.data.meshes.new(n);d.from_pydata(vs,[],faces);d.update()
    d.materials.append(m);o=bpy.data.objects.new(n,d);s.collection.objects.link(o);return o

def model(n,group_name,parts):
    group=bpy.data.objects.new(group_name,None);s.collection.objects.link(group)
    bpy.context.view_layer.update()
    for o in parts:
        q=o.matrix_world.copy();o.parent=group;o.matrix_world=q
    bpy.ops.object.select_all(action='DESELECT')
    group.select_set(True)
    for o in parts:o.select_set(True)
    p=out/(n+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,
                              export_apply=True,export_animations=False,export_texcoords=False)
    b=p.read_bytes();j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
    assert len(b)<125000 and not j.get('images')
    return {'bytes':len(b),'triangles':sum(j['accessors'][a['indices']]['count']//3 for m in j['meshes'] for a in m['primitives']),
            'sha256':hashlib.sha256(b).hexdigest()}

parts=[]
for x in [-.78,.78]:
    parts.extend([box('Seated foot',(x,0,.105),(.35,.39,.21),stone),
        box('Tenoned leg',(x,0,.90),(.174,.144,1.69),wood),
        box('Iron foot wrap',(x,0,.287),(.184,.164,.17),bronze)])
parts += [box('Enamel mounted plinth',(0,0,1.53),(2.16,.223,1.265),wood,.048),
          box('Score frame',(0,-.127,1.55),(1.99,.12,1.108),green,.032),
          box('Rain-shedding top cap',(0,0,2.192),(2.27,.349,.113),bronze,.026),
          box('Vacant record plane',(0,-.198,1.48),(1.67,.054,.38),black),
          glyph('RIDING LAP',(0,-.199,1.929),.245,cream),
          glyph('PERSONAL BEST',(0,-.199,1.112),.156,cream)]
for x in [-.92,.92]:
    for z in [1.073,1.991]:parts.append(bolt(x,-.194,z))
assets={'w10b-riding-lap-board':model('w10b-riding-lap-board','Riding_lap_floor_origin',parts)}
clear_scene()

parts=[box('Cairn socket',(0,0,.091),(.47,.49,.182),stone),
       box('Timber finial post',(0,0,.87),(.19,.19,1.57),back),
       box('Carved tablet',(0,-.036,1.61),(.88,.153,.94),wood,.032),
       box('Inset green tablet',(0,-.128,1.61),(.75,.064,.796),green,.021)]
# Explicit non-self-crossing arrow triangles, no font dependency.
poly=[(-.25,1.66),(-.071,1.66),(-.071,1.37),(.071,1.37),(.071,1.66),(.25,1.66),(0,1.977)]
parts.append(mesh('Ahead arrow',[(x,-.165,z) for x,z in poly],[(0,5,6),(1,2,3),(1,3,4)],cream))
parts += [bolt(x,-.165,1.265) for x in [-.305,.305]]
assets['w10b-first-ring-ahead']=model('w10b-first-ring-ahead','First_ring_arrow_floor_origin',parts)
clear_scene()

def proto(file):
    prev=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(file));bpy.context.view_layer.update()
    new=set(s.objects)-prev
    p=[(o.name,o.data,o.matrix_world.copy()) for o in sorted(new,key=lambda x:x.name) if o.type=='MESH']
    for o in new:bpy.data.objects.remove(o,do_unlink=True)
    return p

def place(pr,xyz,yaw=0,scale=1.):
    tf=Matrix.Translation(xyz)@Matrix.Rotation(math.radians(yaw),4,'Z')@Matrix.Scale(scale,4)
    placed=[]
    for n,d,m in pr:
        o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.matrix_world=tf@m;placed.append(o)
    return placed

def source(k):
    p=donors['donor_meshes'][k]
    f=root/p['path']
    assert hashlib.sha256(f.read_bytes()).hexdigest()==p['sha256']
    return proto(f)

board=place(proto(out/'w10b-riding-lap-board.glb'),board_pos,180)
cue=place(proto(out/'w10b-first-ring-ahead.glb'),cue_pos,cue_yaw)
gantry=place(source('gantry'),(-80,148,.025),90)
# Face the timer toward the archived westbound camera without moving the gantry.
place(source('timer'),(-79.29,148,5.25),90)
first=place(source('ring'),ring['origin_blender_m'],ring['yaw_deg'],donors['rings']['uniform_scale'])
place(source('ring'),donors['rings']['placements'][0]['origin_blender_m'],90,donors['rings']['uniform_scale'])
place(source('jump'),(-125,148,.025),90)
fence=source('fence')
for y in [154.55,141.45]:
    for i in range(36):
        x=-167+i*3.16
        if abs(x+80)<4.5 or (y<148 and abs(x-cue_pos[0])<2.):continue
        place(fence,(x,y,.02),0)
grain(meadow,(.16,.235,.071),.50);grain(sand,(.33,.193,.093),.46);grain(apron,(.25,.224,.159),.56)
box('Paddock meadow',(-140,151,-.16),(310,248,.32),meadow)
box('Straight 12 m oval excerpt',(-118,148,.009),(137,12,.018),sand,0)
box('Rider-worn shelf',(-118,148,.020),(136,3.7,.004),wear,0)
box('Roadside pullout, no route collision',(-80,137,.009),(7.8,7.2,.018),apron)
rng=random.Random(58)
trees=(source('conifer'),source('oak'))
for i in range(81):
    x=-212+rng.uniform(0,153);y=rng.choice([rng.uniform(98,126),rng.uniform(164,196)])
    place(trees[i%2],(x,y,0),rng.uniform(0,360),rng.uniform(.78,1.85))
for j in range(8):
    x=-178-3*j
    place(trees[j%2],(x,148+rng.uniform(-12,19),0),rng.uniform(0,360),rng.uniform(.78,1.85))
for i in range(18):
    x=-88+rng.uniform(0,18);y=132+rng.uniform(0,32)
    if 133<y<155:continue
    o=box('Native grass tufts',(x,y,.11),(.04,.16,rng.uniform(.11,.32)),meadow,.006)
    o.rotation_euler.y=rng.uniform(-.4,.5)

# Staging backdrop kept well behind the entire oval; not shipped in either asset.
ridge1=mat('Distant spruce ridgeline',(.07,.14,.13),.91)
ridge2=mat('Highland haze',(.17,.255,.259),.91)
for idx,(front,peak,backx,center) in enumerate([(-239,-270,-285,17),(-292,-343,-380,28)]):
    pts=[]
    for j in range(125):
        y=-30+j*3.8
        z=center+6.4*math.sin(.058*y+idx)+9.9*math.sin(.026*y+idx)+2.3*math.sin(.119*y)
        pts.extend([(front,y,0),(peak,y,max(3,z)),(backx,y,0)])
    mesh('Far ridgeline '+str(idx),pts,[(3*j+k,3*(j+1)+k,3*(j+1)+k+1,3*j+k+1)
         for j in range(124) for k in (0,1)],ridge1 if idx==0 else ridge2)
s.world=bpy.data.worlds.new('Warm highland morning');s.world.use_nodes=True
w=s.world.node_tree.nodes.get('Background');w.inputs[0].default_value=(.32,.48,.61,1);w.inputs[1].default_value=.49
sun=bpy.data.lights.new('Filtered golden sun','SUN');sun.energy=2.8;sun.color=(1,.85,.67);sun.angle=.16
o=bpy.data.objects.new(sun.name,sun);s.collection.objects.link(o);o.rotation_euler=(.49,-.73,-.27)
cam=bpy.data.cameras.new('Photo proofs');s.camera=bpy.data.objects.new(cam.name,cam);s.collection.objects.link(s.camera)
s.render.engine='CYCLES';s.cycles.samples=44;s.cycles.adaptive_threshold=.067;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94

def frame(name,eye,target,lens,wh):
    s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler()
    cam.lens=lens;cam.sensor_fit='HORIZONTAL'
    s.render.resolution_x,s.render.resolution_y=wh
    bpy.context.view_layer.update()
    s.render.filepath=str(out/(name+'.jpg'))

def bounds(os):
    ps=[o.matrix_world@Vector(c) for o in os for c in o.bound_box]
    return [Vector([fn(p[i] for p in ps) for i in range(3)]) for fn in [min,max]]

arch_cam=(-52,149,2.6)
frame('w10b-westbound-portrait',arch_cam,(-107,142.6,2.75),37,(900,1540))
q=lambda p:world_to_camera_view(s,s.camera,Vector(p))
inside=lambda p:all(.025<v<.975 for v in (p.x,p.y)) and p.z>0
# Preserve the historical camera position but not an assertion about gameplay direction.
cue_screen=q(cue_pos[:2]+(1.62,))
ring_screen=q((-105,148,3.4))
assert inside(cue_screen) and inside(ring_screen)
deps=bpy.context.evaluated_depsgraph_get()
def line(u,v):
    u,v=Vector(u),Vector(v)
    return s.ray_cast(deps,u,(v-u).normalized(),distance=(v-u).length)
watch=[(-82,139.4,1.65),(-80,140.30,1.65),(-78,139.4,1.65)]
board_hits=[line(u,(-80,137.212,1.48)) for u in watch]
assert all(h[0] and h[4] in board and 'vacant' in h[4].name.lower() for h in board_hits)
rider_line=line(arch_cam,(-105,148,3.40))
assert not rider_line[0], 'The view through the opening is obstructed'
bb=bounds(board); cb=bounds(cue)
assert bb[1].y<142 and cb[1].y<142,"Props must stay off the original 12 m riding ribbon"
receipt={'slice':'W10b','catalogue_id':'WSC-KIT-005','historical_layout':history,
         'board_blender_xyz':board_pos,'board_world_xyz':[-80,0,-137], 'board_track_clearance_m':round(142-bb[1].y,4),
         'cue_blender_xyz':cue_pos,'cue_track_clearance_m':round(142-cb[1].y,4),
         'archived_eye_blender_xyz':arch_cam,'first_ring_blender_xyz':[-105,148,3.4],
         'r02_westbound_ring_order_provisional':[2,1,8,7,6,5,4,3],
         'gantry_to_first_ring_m':25,'cue_ndc':list(cue_screen),'first_ring_ndc':list(ring_screen),
         'unobstructed_eye_to_ring_center':True,'board_readout_rays':len(board_hits),
         'assets':assets,'scope':'Art fit, no route, mount, penalty, record or live scoring changes.'}
(out/'fit.json').write_text(json.dumps(receipt,indent=2)+'\n')
bpy.ops.render.render(write_still=True)
frame('w10b-best-board',(-74.8,140.9,2.5),(-80,137.1,1.35),48,(1400,900))
bpy.ops.render.render(write_still=True)

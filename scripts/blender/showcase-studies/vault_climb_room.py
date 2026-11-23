"""Static E10c Room 3 in the D41 envelope. No native route or winch host is changed."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

OUT=output_directory()
ROOT=Path(__file__).resolve().parents[3]
ASSETS=ROOT/'public/assets/wildshard-art'
clear_scene()
S=bpy.context.scene
FILES={
    'bay':'wsc-arch-002-industrial-wall-bay.glb',
    'plates':'wsc-prop-064-metal-floor-plates.glb',
    'ladder':'wsc-prop-040-mover-access-ladder.glb',
    'bridge':'wsc-prop-048-rope-walkway.glb',
    'lift_frame':'wsc-kit-009-reveal-lift-frame.glb',
    'lift_deck':'wsc-kit-009-reveal-lift-deck.glb',
    'door':'wsc-prop-063-round-vault-bulkhead.glb',
}
templates={}; metadata={}
def bounds(points):
    return [[round(fn(v[i] for v in points),6) for i in range(3)] for fn in (min,max)]

for key,name in FILES.items():
    p=ASSETS/name
    pre=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    bpy.context.view_layer.update()
    obs=sorted(set(S.objects)-pre,key=lambda o:o.name)
    pieces=[(o.name,o.data,o.matrix_world.copy()) for o in obs if o.type=='MESH']
    templates[key]=pieces
    pts=[m@p.co for _,mesh,m in pieces for p in mesh.vertices]
    metadata[key]=dict(file=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),local_bounds_blender_m=bounds(pts))
    for ob in obs:bpy.data.objects.remove(ob,do_unlink=True)

assert metadata['lift_deck']['local_bounds_blender_m']==[[-3.0,-3.0,-4.959],[3.0,3.0,0.0]]
assert metadata['lift_frame']['local_bounds_blender_m']==[[-3.49,-3.49,-1.57],[3.49,3.49,0.0]]
assert metadata['ladder']['local_bounds_blender_m'][1][2]==3.755
# Check the exact timber surface at the two landing sample points, not the ropes' overall AABB.
timber=[]
for n,mesh,m in templates['bridge']:
    if any(q in n.lower() for q in ('timber','cedar','endgrain')):
        b=BVHTree.FromPolygons([m@v.co for v in mesh.vertices],[tuple(f.vertices) for f in mesh.polygons])
        timber.append(b)
def deck_ray(x):
    hits=[b.ray_cast(Vector((x,0,1.8)),Vector((0,0,-1)),2.0)[0] for b in timber]
    return max(h.z for h in hits if h is not None)
low=5.5;high=9.5
near_lip,far_lip=[deck_ray(x) for x in (-4,4)]
assert abs(near_lip-far_lip)<.00003 and abs(near_lip-.682)<.002
bridge_z=round(low-(near_lip+far_lip)*.5,6)
assert max(abs(bridge_z+t-low) for t in (near_lip,far_lip))<.00002
records=[]
def place(key,name,xyz,yaw=0):
    transform=Matrix.Translation(xyz) @ Matrix.Rotation(math.radians(yaw),4,'Z')
    result=[]
    for n,mesh,m in templates[key]:
        o=bpy.data.objects.new(name+' | '+n,mesh)
        S.collection.objects.link(o)
        o.matrix_world=transform@m
        result.append(o)
    records.append(dict(asset=key,label=name,origin_blender_m=xyz,yaw_deg=yaw))
    return result

def mat(n,c,rough=.58,metal=.2,emit=0):
    m=bpy.data.materials.new(n)
    m.use_nodes=True
    q=m.node_tree.nodes.get('Principled BSDF')
    q.inputs['Base Color'].default_value=(*c,1)
    q.inputs['Metallic'].default_value=metal
    q.inputs['Roughness'].default_value=rough
    q.inputs['Emission Color'].default_value=(*c,1)
    q.inputs['Emission Strength'].default_value=emit
    return m

structure=mat('Vault blackened plate',(.038,.063,.075))
wall=mat('Vault cold masonry',(.082,.123,.129),.84,.0)
edge=mat('Steel guard channel',(.23,.31,.32),.45,.37)
dark=mat('Deep vault graphite',(.020,.039,.048),.8)
yellow=mat('Vault warm hazard trim',(.77,.243,.040))
cyan=mat('Vault pale teal status lights',(.058,.56,.62),.43,.08,1.6)
white=mat('Vault route printing',(.72,.85,.79),.71,.05,.48)
name_mat=mat('Vault bright room numbers',(.97,.60,.19),.52,.05,.62)

struct=[]
def box(n,p,d,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    ob=bpy.context.object; ob.name=n;ob.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(m)
    if bevel:
        b=ob.modifiers.new('Small steel bevel','BEVEL')
        b.width=bevel;b.segments=2
    struct.append(ob)
    return ob

schematic=[]
def label(n,value,p,size,m,angle=0):
    c=bpy.data.curves.new(n,'FONT')
    c.body=value;c.align_x='CENTER';c.size=size;c.materials.append(m)
    o=bpy.data.objects.new(n,c);S.collection.objects.link(o)
    o.location=p;o.rotation_euler=(math.pi/2,0,angle)
    return o
def platform(name,x0,x1,z,width,depth):
    box(name,((x0+x1)/2,0,z-depth/2),(x1-x0,width,depth),structure,.055)
    box(name+' safety header',((x0+x1)/2,-width/2-.010,z-.16),(x1-x0,.04,.095),yellow,.014)

# A coherent sequence from west to east. Deck access aligns to the crossed bridge.
platform('Threshold from Room 2',-16.0,-10.68,.90,4.8,.23)
place('plates','Entry tread',(-13.6,0,.903))
ladder=place('ladder','01 wall ladder',(-10.94,0,.875),-90)
platform('Ladder landing',-10.68,-8.0,4.45,3.2,.40)
platform('Scramble step A',-8.0,-6.7,4.87,3.2,.64)
platform('Scramble step B',-6.7,-5.26,5.23,3.0,.67)
platform('Scramble step C / bridge apron',-5.26,-4.0,low,3.0,.56)
for i,(x,z) in enumerate([(-9.9,4.45),(-7.40,4.87),(-6.0,5.23),(-4.77,low)]):
    box('Scramble support', (x,1.14,z*.50),(.61,.62,z),dark,.066)
    box('Step light', (x,-1.65,z-.19),(.52,.036,.082),cyan,.014)
place('bridge','03 original bridge',(0,0,bridge_z))
platform('Winch approach',4.0,6.51,low,3.3,.45)
lift_fixed=place('lift_frame','04 fixed shaft mouth',(10,0,low))
lift_low=place('lift_deck','Deck at lower mark',(10,0,low))
lift_up=place('lift_deck','Deck at upper mark',(10,0,high))
platform('Last-door landing',13.0,19.05,high,4.8,.53)
place('plates','Last-door tread',(16.15,0,high+.003))
place('door','05 last door / static bulkhead',(18.0,0,high),-90)
box('Static final door jamb',(18.32,1.65,high+1.64),(.46,.37,3.28),structure,.06)
box('Static final lintel',(18.32,0,high+3.13),(.40,3.58,.38),structure,.05)
label('Final room id','LAST DOOR',(17.96,0,high+3.2),.22,name_mat,-math.pi/2)
for y in (-3.69,3.69):
    for x in (6.35,13.64):
        box('Outer guide upright',(x,y,5.48),(.18,.18,10.85),edge,.025)
        box('Anchor socket',(x,y,.24),(.34,.34,.34),dark,.035)
    box('Overhead side tie',(10,y,11.05),(7.66,.24,.25),edge,.03)
box('Winch header (art cue)',(10,0,11.95),(1.55,7.66,.31),structure,.075)
for x in (9.55,10.45):
    for y in (-3.17,3.17):
        box('Stand-in guarded suspension',(x,y,7.05),(.065,.065,9.54),edge,.011)
box('Winch cable casing',(10,0,12.42),(1.6,1.25,.69),dark,.067)
box('Winch casing status',(10,-.645,12.45),(.91,.025,.085),cyan,.013)
for y in (-4.26,4.26):
    box('Vault perimeter beam',(1.6,y,.29),(36.8,.39,.43),structure,.06)
for i in range(10):
    x=-15.4+i*3.6
    for z in (.16,2.30,4.44):
        place('bay','Back wall repeated industrial bay',(x,4.54,z))
for x in (-15.9,-11.9,-7.9,-3.9,.1,4.1,8.1,12.1,16.1,19.1):
    box('Shaft rib',(x,4.74,7.33),(.27,.25,14.55),structure,.028)
box('Rear chamber wall',(1.72,4.94,7.3),(36.8,.32,14.6),wall,.03)
box('Ceiling fascia cutaway line',(1.72,4.58,14.68),(36.8,.48,.17),edge,.02)
box('Vault invert',(1.72,0,.065),(36.8,9.7,.13),dark,.041)
for x in (-14,-8,-2,4,10,16):
    for z in (5.75,11.35):
        box('Wall lighting strip',(x,4.28,z),(1.37,.04,.14),cyan,.026)
for p,value in [((-13.3,-4.43,3.03),'01   LADDER'),((-7.21,-4.43,6.91),'02   SCRAMBLE'),
                ((.0,-4.43,7.52),'03   ROPE BRIDGE'),((9.6,-4.43,13.72),'04   WINCH LIFT'),
                ((16.28,-4.43,10.62),'05   LAST DOOR')]:
    x,y,z=p
    schematic.append(box('Section label plaque', (x,y+.046,z+.14),(5.20,.06,.50),dark,.045))
    schematic.append(label(value,value,p,.46,white))
for z,c in [(5.5,'LOW  −44.5 m'),(9.5,'HIGH  −40.5 m')]:
    x=11.0
    schematic.append(box('Landing label plaque',(x,-4.126,z-.54),(3.02,.06,.35),dark,.032))
    schematic.append(label(c,c,(x,-4.168,z-.64),.33,name_mat))
    for x in (7.33,8.22,9.11,10.0,10.89,11.78,12.67):
        schematic.append(box('Landing plane dash',(x,-4.19,z),(.52,.036,.043),cyan,.006))

bounds_world=dict(x=[151,221],y=[-50,-30],z=[-99,-29])
def world(p):
    return (186+p[0],-50+p[2],-64-p[1])
pts=[world(o.matrix_world@v.co) for o in S.objects if o.type=='MESH' for v in o.data.vertices]
b=bounds(pts)
for i,k in enumerate('xyz'):
    assert bounds_world[k][0]-.0001<=b[0][i] and b[1][i]<=bounds_world[k][1]+.0001,(k,b)
shaft_floor=round(low+metadata['lift_deck']['local_bounds_blender_m'][0][2],6)
assert shaft_floor==.541
assert round(world((10,0,high))[1]-world((10,0,low))[1],3)==4.0
assert high==9.5 and 10+3.0==13.0
report=dict(catalogue_id='WSC-KIT-008',support_id='WSC-SCENE-006',
            scope='E10c Room 3 art layout. No working ladder, scramble, bridge, winch, door, clearance or native runtime.',
            plan_refs=['E10c-vault-rooms', 'DECISIONS.md D41'],
            bounds_world_gltf_m=bounds_world,
            proposal_art_bounds_world_gltf_m=b,
            scene_transform='world [186+x, -50+z, -64-y] for Blender x,y,z. Placement is proposed, not a native map anchor.',
            bridge=dict(length_overall_m=round(metadata['bridge']['local_bounds_blender_m'][1][0]*2,4),
                        end_board_plane_world_y=-44.5,
                        end_test_local_x=[-4,4],donor_end_board_z=[round(near_lip,6),round(far_lip,6)],
                        end_board_centerline_height_error_m=round(max(abs(bridge_z+t-low) for t in (near_lip,far_lip)),7)),
            lift=dict(donor='Measured Gauntlet art donor only',fixed_frame_world_y=-44.5,
                      platform_low_world_y=-44.5,platform_high_world_y=-40.5,
                      shaft_bottom_low_world_y=-49.459,margin_above_box_bottom_m=shaft_floor,
                      upper_deck_joins_apron_x_blender_m=13.0,proposed_rise_m=4),
            route=['ladder','three scramble ledges','rope bridge','winch lift','last door'],
            donors=metadata,placements=records)
(OUT/'e10c-vault-room-03-study.json').write_text(json.dumps(report,indent=2)+'\n')
print('VAULT_03_PROOF',b,bridge_z,shaft_floor)
if os.getenv('WSC_METADATA_ONLY')=='1':sys.exit(0)

S.world=bpy.data.worlds.new('Vault cold ambient')
S.world.use_nodes=True
q=S.world.node_tree.nodes.get('Background')
q.inputs[0].default_value=(.17,.28,.40,1)
q.inputs[1].default_value=.28
def aim(o,target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,p,target,power,size,col):
    bpy.ops.object.light_add(type='AREA',location=p)
    o=bpy.context.object;o.name=name;o.data.energy=power;o.data.size=size;o.data.color=col
    aim(o,target)
for x,z in [(-14,3.0),(-7,7.2),(0,8.3),(10,10),(16,12.6)]:
    light('Warm route key',(x,-3.3,z+3.0),(x,.15,z-2.0),1650,4,(1,.65,.34))
    light('Cool shell bounce',(x+1.2,2.85,z+4.2),(x,0,z-1),1150,4.4,(.46,.77,1))
light('Section front fill',(0,-13.2,10),(1,0,5),2650,12,(.62,.78,1))
S.render.engine='CYCLES'
S.cycles.samples=42
S.cycles.use_adaptive_sampling=True;S.cycles.adaptive_threshold=.078
S.cycles.use_denoising=False
S.render.image_settings.file_format='JPEG'
S.render.image_settings.quality=90
S.render.resolution_percentage=100
def render(name,xyz,target,wh,ortho=None,lens=35):
    bpy.ops.object.camera_add(location=xyz)
    o=bpy.context.object;S.camera=o
    aim(o,target)
    if ortho is not None:
        o.data.type='ORTHO';o.data.ortho_scale=ortho
    else:o.data.lens=lens
    S.render.resolution_x,S.render.resolution_y=wh
    S.render.filepath=str(OUT/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)
def set_hide(batch,val):
    for o in batch:o.hide_render=val
set_hide(lift_up,True)
render('nov23-vault-03-section',(-11.25,-45.0,16.7),(1.6,0,6.7),(1680,970),ortho=41.0)
set_hide(schematic,True)
render('nov23-vault-03-entry',(-15.55,-2.13,2.62),(-7.90,.16,5.65),(1000,1400),lens=26)
set_hide(lift_low,True);set_hide(lift_up,False)
render('nov23-vault-03-high',(-2.37,-12.8,14.7),(9.60,.10,7.1),(1510,920),lens=34)

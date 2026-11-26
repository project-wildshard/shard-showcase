"""Optional E9 wall control; four fits on the unchanged Round 5 corner proxies."""
from pathlib import Path
import hashlib
import json
import math
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[3]
assets = root / 'public/assets/wildshard-art'
out = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
out.mkdir(parents=True, exist_ok=True)
name = 'wsc-kit-007-storm-beacon-control.glb'
proof_only = '--proof-only' in sys.argv
pins = {
    'wsc-kit-007-storm-beacon.glb': '3a525f2637d5150a1e5a85c04640d6a57772c842731f063aa429142810239833',
    'wsc-kit-007-storm-beacon-seat.glb': '4a63489abed860eabd4a736b6c9732d0e75233953b523b7705ea5b9f1b8af2b3',
    'wsc-kit-007-storm-beacon-charged-lamp.glb': 'ab7445a6977c9af5cea7a31618a9c660f539e1026e23e61b1bbc2b3426b77a5d',
}
for f, pin in pins.items():
    assert hashlib.sha256((assets/f).read_bytes()).hexdigest() == pin
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.render.fps = 25

def mat(label, color, metal=0, rough=.48, em=0):
    m = bpy.data.materials.new(label)
    m.use_nodes = True
    n = m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value = (*color,1)
    n.inputs['Metallic'].default_value = metal
    n.inputs['Roughness'].default_value = rough
    n.inputs['Emission Color'].default_value = (*color,1)
    n.inputs['Emission Strength'].default_value = em
    return m

def select(obs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]

def box(label, loc, dims, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=label
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        z=o.modifiers.new('Rounded edges','BEVEL');z.width=bevel;z.segments=1
        bpy.ops.object.modifier_apply(modifier=z.name)
    return o

def cyl(label, loc, radius, length, material, axis='z', sides=10):
    r={'x':(0,math.pi/2,0),'y':(math.pi/2,0,0),'z':(0,0,0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides,radius=radius,depth=length,location=loc,rotation=r)
    o=bpy.context.object;o.name=label;o.data.materials.append(material)
    return o

def text(body, loc, size, material):
    c=bpy.data.curves.new(body,'FONT');c.body=body;c.align_x='CENTER';c.align_y='CENTER'
    c.size=size;c.resolution_u=2;c.materials.append(material)
    o=bpy.data.objects.new(body,c);s.collection.objects.link(o)
    o.location=loc;o.rotation_euler.x=math.pi/2
    select([o]);bpy.ops.object.convert(target='MESH')
    return bpy.context.object

def join(label, obs):
    select(obs)
    bpy.ops.object.join()
    ob=bpy.context.object;ob.name=label
    return ob

iron=mat('Warm cast iron',(.042,.062,.068),.46)
slate=mat('Oxidised dark petrol enamel',(.058,.109,.12),.28)
zinc=mat('Bright edge and fasteners',(.205,.26,.267),.63)
ochre=mat('Beacon ochre',(.65,.237,.041),.35,.39)
rubber=mat('Gripped dark rubber',(.019,.028,.028),.08,.72)
ivory=mat('Stamped bone enamel',(.77,.79,.64),.22,.45)
amber=mat('Amber lens, no emitted beam',(.87,.35,.048),.32,.30)
body = [
    box('Gasket plate',(0,-.017,0),(.57,.030,.68),rubber,.016),
    box('Cast chassis',(0,-.080,0),(.52,.126,.62),iron,.032),
    box('Inset face',(0,-.145,.006),(.446,.028,.526),slate,.022),
    box('Hood, formed drip lip',(0,-.155,.305),(.555,.172,.050),zinc,.012),
    box('Raised hazard bar',(0,-.165,-.234),(.307,.013,.035),ochre,.004),
    text('BEACON',(0,-.163,.182),.083,ivory),
    cyl('Bottom cable gland',(0,-.081,-.340),.047,.070,zinc,'z',8),
]
for sign in (-1,1):
    x=.224*sign
    body.append(box('Recess guard',(x,-.245,-.021),(.050,.171,.33),iron,.015))
    for z in (-.185,.244):
        body.append(cyl('Recessed hex bolt',(x,-.160,z),.018,.018,zinc,'y',6))
axle=cyl('BeaconControlAxle',(0,-.223,-.025),.047,.282,zinc,'x',12)
fixed=join('BeaconControlHousing',body)
# Fixed lens is intentionally non-emissive. The game can replace this material if it
# needs an actual Ready/On indication independent of the moving switch.
lens=cyl('BeaconControlStatusLens',(.169,-.165,.104),.027,.014,amber,'y',12)
hinge=bpy.data.objects.new('BeaconControlPivot',None);s.collection.objects.link(hinge)
hinge.location=(0,-.223,-.025)
handle=join('BeaconControlHandle',[
    box('Forged toggle stem',(0,-.223,.066),(.055,.046,.171),ochre,.010),
    cyl('Grip core',(0,-.223,.145),.035,.226,zinc,'x',12),
    cyl('Grip overmold',(0,-.223,.145),.039,.168,rubber,'x',12)])
bpy.context.view_layer.update()
m=handle.matrix_world.copy();handle.parent=hinge;handle.matrix_world=m
for frame, deg in [(0,145),(2,131),(6,63),(8,35)]:
    hinge.rotation_euler.x=math.radians(deg)
    hinge.keyframe_insert(data_path='rotation_euler',frame=frame,group='Switch')
act=hinge.animation_data.action;act.name='BeaconControlEngage'
for fc in act.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_start,s.frame_end=0,8
s.frame_set(0)
select([fixed,axle,lens,hinge,handle])
bpy.ops.export_scene.gltf(filepath=str(out/name),export_format='GLB',use_selection=True,export_animations=True,
    export_animation_mode='ACTIONS',export_frame_range=True,export_force_sampling=True)
blob=(out/name).read_bytes()
h=struct.unpack_from('<I',blob,12)[0]
g=json.loads(blob[20:20+h])
assert not g.get('textures')
assert [a['name'] for a in g['animations']]==['BeaconControlEngage']
tri_count=sum((g['accessors'][q['indices']]['count'] if 'indices' in q else g['accessors'][q['attributes']['POSITION']]['count'])//3
              for m in g['meshes'] for q in m['primitives'])
assert tri_count<2600 and len(blob)<180_000

def clear():
    for o in tuple(s.objects):
        bpy.data.objects.remove(o,do_unlink=True)
    for a in tuple(bpy.data.actions):
        bpy.data.actions.remove(a)

def load(path):
    old=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return sorted(set(s.objects)-old,key=lambda o:o.name)

def mesh(obs):
    deps=bpy.context.evaluated_depsgraph_get()
    vv,tt=[],[]
    for obj in obs:
        if obj.type!='MESH': continue
        o=obj.evaluated_get(deps);d=o.to_mesh();d.calc_loop_triangles()
        i=len(vv);vv.extend(o.matrix_world@v.co for v in d.vertices)
        tt.extend(tuple(i+k for k in t.vertices) for t in d.loop_triangles);o.to_mesh_clear()
    return vv,BVHTree.FromPolygons(vv,tt,all_triangles=True)

clear()
obs=load(out/name)
hinge=next(o for o in obs if o.name=='BeaconControlPivot')
hand=next(o for o in obs if o.name=='BeaconControlHandle')
action=bpy.data.actions[0];a,b=action.frame_range
assert abs((b-a)/25-.32)<1e-5
def frame(f):
    s.frame_set(math.floor(f),subframe=f%1)
    bpy.context.view_layer.update()
frame(a);p0=hinge.matrix_world.to_quaternion()
frame(b);p1=hinge.matrix_world.to_quaternion()
difference=p0.rotation_difference(p1).angle
assert abs(math.degrees(difference)-110)<.01
static=mesh([o for o in obs if o.name in {'BeaconControlHousing','BeaconControlStatusLens'}])[1]
all_points=[];handles=[]
for k in range(65):
    frame(a+(b-a)*k/64)
    v,_=mesh(obs);vv,grip=mesh([hand]);all_points.extend(v);handles.extend(vv)
    assert not grip.overlap(static), ('Guard or lens collision',k)
assert max(v.y for v in all_points)<-.001
assert max(abs(v.x) for v in handles)<.16
assert max(v.y for v in handles)<-.181
assert min(v.y for v in handles)>-.445

corners=[(126,14),(232,14),(232,118),(126,118)]
walls=[(126,14,140,14),(156,14,232,14),(232,14,232,118),
       (126,118,232,118),(126,14,126,58),(126,74,126,118)]
ped_mat=mat('Weathered gray concrete',(.13,.19,.21),.08,.59)
floor_mat=mat('Wet slate',(.055,.085,.107),.16,.28)
paint=mat('Faded ochre wayfinding',(.47,.197,.041),.13,.55)
# All four exact anchors; local z is up; Three translation is [X,Y,Z].
poses=[]
footprints=[(x-2,x+2,z-2,z+2) for x,z in corners]
footprints.extend((min(x,u)-.3,max(x,u)+.3,min(z,v)-.3,max(z,v)+.3) for x,z,u,v in walls)
def intersects(a,b):
    return a[0]<b[1] and b[0]<a[1] and a[2]<b[3] and b[2]<a[3]
for i,(x,z) in enumerate(corners):
    sx=1 if x==126 else -1
    sz=1 if z==14 else -1
    center=(x+sx*1,1.32,z+sz*2)
    yaw=0 if sz==1 else math.pi
    transform=Matrix.Translation((center[0],-center[2],center[1]))@Matrix.Rotation(yaw,4,'Z')
    pts=[transform@v for v in all_points]
    # Full sweep stays outside the pedestal and in the interior of the yard.
    min_out=min(((-v.y)-center[2])*sz for v in pts)
    assert min_out>.001
    assert all(126.3 < p.x < 231.7 and 14.3 < -p.y < 117.7 for p in pts)
    # Continuous worst-case 1.0 m-wide walkway prism starts 0.50 m
    # outside wall; no reach claimed beyond a simple geometry reservation.
    approach_z=[center[2]+sz*d for d in (.50,3.65)]
    assert max(abs(p.y+center[2]) for p in pts)<.50
    assert 126.3 < center[0]-.5 < center[0]+.5 < 231.7
    assert all(14.3<q<117.7 for q in approach_z)
    approach=(center[0]-.5,center[0]+.5,*sorted(approach_z))
    assert not any(intersects(approach,f) for f in footprints)
    poses.append(dict(corner=i+1,three_xyz=center,yaw_deg=math.degrees(yaw),
        min_air_gap_from_pedestal_m=round(min_out,6),outward_approach_three_z=approach_z))
receipt=dict(scope='Optional art at four Round 5 corner pedestal proxies. No trigger, quest, hold, payout or live behavior.',
    archive_layout_blob='5d019a020361c47187ec889f2bc947f82cd9f98a',
    archive_lab_blob='51a3b4bef1f2d4891172164d10893d98d450a3b9',
    pins=pins,sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),triangles=tri_count,
    texture_count=0,clip='BeaconControlEngage',seconds=.32,degrees=110,checked_poses_per_anchor=65,
    handle_top_offset_m=round(max(v.z for v in handles),6),
    handle_bottom_offset_m=round(min(v.z for v in handles),6),
    max_protrusion_m=round(-min(v.y for v in all_points),6),approach_width_m=1,placements=poses)
(out/'e9-beacon-ground-control-proof.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt,flush=True)
if proof_only:
    sys.exit(0)

# North-west fitted face in a local review stage; retain exact original
# height and footprints and load the existing lamp/cage for the context shot.
box('4 m original pedestal proxy',(-1,2,6),(4,4,12),ped_mat,.04)
box('Original northern wall', (6,2,1.3),(14,.6,2.6),ped_mat,.025)
box('Original western wall',(-1,-20,1.3),(.6,44,2.6),ped_mat,.025)
box('Review yard ground',(15,-10,-.1),(94,76,.2),floor_mat)
for n in [-1,1]:
    for i in range(2):
        stripe=box('Review floor paint',(n*.7,-.6-i*.48,.003),(.085,.28,.006),paint)
        stripe.rotation_euler.z=n*.18
def translate(parts, offset):
    for o in parts:
        if o.parent is None:o.location+=Vector(offset)
translate(obs,(0,0,1.32))
for file,hgt in [('wsc-kit-007-storm-beacon-seat.glb',12),('wsc-kit-007-storm-beacon.glb',14.533658),
                 ('wsc-kit-007-storm-beacon-charged-lamp.glb',14.533658)]:
    translate(load(assets/file),(-1,2,hgt))
world=bpy.data.worlds.new('Storm blue');s.world=world;world.use_nodes=True
bg=world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.30,.49,.68,1)
bg.inputs['Strength'].default_value=.47
data=bpy.data.lights.new('Break in cloud','AREA');data.energy=620;data.shape='DISK';data.size=5
data.color=(1,.83,.64)
key=bpy.data.objects.new(data.name,data);s.collection.objects.link(key)
key.location=(2,-3,6)
key.rotation_euler=(Vector((0,0,1.35))-key.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=38;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.062
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
def render(label,location,target,focal,dims,t):
    frame(t)
    bpy.ops.object.camera_add(location=location);cam=bpy.context.object
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=focal;s.camera=cam
    s.render.resolution_x,s.render.resolution_y=dims
    s.render.resolution_percentage=100
    s.render.filepath=str(out/(label+'.png'))
    bpy.ops.render.render(write_still=True)
render('ground-control',(.80,-1.45,1.80),(0,-.17,1.33),53,(1080,1050),a)
render('corner-context',(8,-14,1.70),(-.9,1.2,8.9),22,(940,1350),b)

"""Tinker Rook: actual packed actor reimport plus a street-side W04 art composition.

Generate tinker-rook-decoded-for-blender.glb with the shared town bot packer first.
The decode is out-of-tree; no kit geometry is changed and there is no room or shop logic.
"""
import hashlib
import json
import math
from pathlib import Path
import sys
import os

import bpy
from mathutils import Matrix, Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

out = output_directory()
repo = Path(__file__).resolve().parents[3]
assets = repo / 'public/assets/wildshard-art'
actor = out / 'tinker-rook-decoded-for-blender.glb'
packed = out / 'wsc-actor-018-tinker-rook-packed.glb'

def imported(file):
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(file))
    bpy.context.view_layer.update()
    return sorted(set(bpy.context.scene.objects) - before, key=lambda o: o.name)

def actor_instance(xyz, yaw):
    obs = imported(actor)
    rig, = [o for o in obs if o.type == 'ARMATURE']
    body, = [o for o in obs if o.type == 'MESH' and o.vertex_groups]
    assert len(rig.data.bones) == 21
    assert body.parent == rig and len(body.data.materials) == 1
    assert rig.animation_data and len(rig.animation_data.nla_tracks) == 1
    clip = rig.animation_data.nla_tracks[0]
    frame_start, frame_end = clip.strips[0].frame_start, clip.strips[0].frame_end
    assert abs((frame_end-frame_start)/bpy.context.scene.render.fps-3) < .039
    transform = Matrix.Translation(xyz) @ Matrix.Rotation(math.radians(yaw),4,'Z')
    for o in obs:
        if o.parent not in obs:
            o.matrix_world = transform @ o.matrix_world
    return rig, body

def setup():
    clear_scene()
    s = bpy.context.scene
    s.render.fps = 24
    s.render.engine = 'CYCLES'
    s.cycles.samples = 46
    s.cycles.use_denoising = False
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = .056
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = 'JPEG'
    s.render.image_settings.quality = 89
    s.world = bpy.data.worlds.new('W04 controlled ambient')
    s.world.use_nodes=True
    q = s.world.node_tree.nodes.get('Background')
    q.inputs[0].default_value=(.31,.44,.63,1)
    q.inputs[1].default_value=.47
    return s

def aim(o, target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def area(n, xyz, power, diameter, color, target):
    bpy.ops.object.light_add(type='AREA',location=xyz)
    o=bpy.context.object
    o.name=n
    o.data.energy=power
    o.data.shape='DISK'
    o.data.size=diameter
    o.data.color=color
    aim(o,target)

def point(n, xyz, power, color):
    bpy.ops.object.light_add(type='POINT',location=xyz)
    o=bpy.context.object
    o.name=n
    o.data.energy=power
    o.data.shadow_soft_size=.16
    o.data.color=color

def plain(name, color, rough=.72):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    q=m.node_tree.nodes.get('Principled BSDF')
    q.inputs['Base Color'].default_value=(*color,1)
    q.inputs['Roughness'].default_value=rough
    return m

def slab(name, loc, dims, mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.name=name
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    b=o.modifiers.new('Small edge','BEVEL')
    b.width=.033
    b.segments=2
    return o

def camera(s, name, xyz, target, res, ortho=None, lens=50):
    bpy.ops.object.camera_add(location=xyz)
    o=bpy.context.object
    s.camera=o
    aim(o,target)
    if ortho:
        o.data.type='ORTHO'
        o.data.ortho_scale=ortho
    else:
        o.data.lens=lens
    s.render.resolution_x,s.render.resolution_y=res
    s.render.filepath=str(out/(name+'.jpg'))
    if os.environ.get('WSC_METADATA_ONLY') != '1':
        bpy.ops.render.render(write_still=True)

def rgba_points(body, rig, frames):
    s=bpy.context.scene
    points=[]
    for n in frames:
        s.frame_set(n)
        dep=bpy.context.evaluated_depsgraph_get()
        ev=body.evaluated_get(dep)
        pts=[tuple(ev.matrix_world@v.co) for v in ev.data.vertices]
        points.append(pts)
    shift=max(math.dist(a,b) for a,b in zip(points[0],points[1]))
    assert shift>.005
    assert abs(min(v[2] for v in points[0]))<.002
    assert max(math.dist(a,b) for a,b in zip(points[0],points[-1]))<.0002
    return round(shift,4)

s=setup()
rig,body=actor_instance((-.60,0,0),-14)
shift=rgba_points(body,rig,(1,19,73))
rig2,body2=actor_instance((.61,.05,0),153)
s.frame_set(25)
slab('Studio deck',(0,0,-.106),(200,200,.21),plain('Petrol oxidized studio floor',(.036,.065,.072)))
area('Warm window key',(-2.6,-3.4,4.6),430,3.1,(1,.83,.63),(0,0,1.1))
area('Cool porch fill',(3.4,-1.9,2.5),230,2.5,(.63,.84,1),(0,0,.94))
area('Back edge',(1.4,3.0,3.9),560,2.2,(1,.65,.38),(0,0,1.02))
camera(s,'nov23-rook-studio',(0,-6.0,2.26),(0,0,.95),(1400,1030),ortho=2.77)

s=setup()
rig,body=actor_instance((-.86,-1.73,0),12)
s.frame_set(19)
sources={}
placements=[]
def source(key, name, only=None):
    p=assets/name
    obs=imported(p)
    arr=[(o.data,o.matrix_world.copy()) for o in obs if o.type=='MESH' and (not only or o.name.startswith(only))]
    pts=[m@v.co for mesh,m in arr for v in mesh.vertices]
    mid=[(min(c[i] for c in pts)+max(c[i] for c in pts))*.5 for i in range(2)]
    low=min(c.z for c in pts)
    sources[key]=(arr,(mid[0],mid[1],low),name,hashlib.sha256(p.read_bytes()).hexdigest(),only)
    for o in obs:bpy.data.objects.remove(o,do_unlink=True)

def place(key, xyz, yaw=0, scale=1, recenter=False):
    arr,center,name,_,_=sources[key]
    T=Matrix.Translation(xyz) @ Matrix.Rotation(math.radians(yaw),4,'Z') @ Matrix.Scale(scale,4)
    if recenter: T=T @ Matrix.Translation(-Vector(center))
    for i,(mesh,m) in enumerate(arr):
        o=bpy.data.objects.new(key+f' part {i+1}',mesh)
        s.collection.objects.link(o)
        o.matrix_world=T @ m
    placements.append(dict(name=key,xyz_blender_m=xyz,yaw_degrees=yaw,uniform_scale=scale,recenter_on_base=recenter))

source('storefront','wsc-prop-022-tinker-rook.glb')
source('awning','wsc-prop-023-shop-doorway-awning.glb')
source('wrench sign','wsc-prop-024-shop-wrench-sign.glb')
source('counter','wsc-arch-006-shop-interior-kit.glb','Oak display counter')
source('lantern','wall-lantern.glb')
source('cargo crate','haul-crate.glb')
source('paving','wsc-arch-005-plaza-paving-kit.glb')
source('street bay','wsc-arch-003-town-facade-kit.glb')
place('storefront',(0,0,0))
place('awning',(.57,-.48,1.99),scale=1.16)
place('wrench sign',(3.15,-.457,3.02),scale=.43)
place('counter',(1.45,-1.56,0),-7,recenter=True)
place('cargo crate',(3.57,-1.21,0),-12,scale=.81)
place('lantern',(-2.99,-.38,2.42),scale=.52)
place('lantern',(2.97,-.38,2.39),scale=.52)
for y in (-7.2,-2.4):
    for x in (-4.8,0,4.8):
        place('paving',(x,y,-.015),0)
for x in (-5.41,5.44):
    for z in (0,3.13):
        place('street bay',(x,.44,z))
# Off-crop side walls and cool bounce put rhythm into the street vignette.
slab('West bounce block',(-5.4,1.99,2.97),(3.40,3.29,5.91),plain('Limestone bounce block',(.26,.22,.15)))
slab('East bounce block',(5.48,1.99,2.97),(3.70,3.29,5.91),plain('Ochre bounce block',(.27,.177,.094)))
slab('Paving underfill',(0,0,-.33),(200,200,.56),plain('Smooth lane base',(.14,.117,.084)))
area('Late storefront sunlight',(-6.2,-4.3,7.0),1530,4.6,(1,.82,.62),(0,-.6,2))
area('Cool street soft fill',(4.9,-4,4.0),600,4.9,(.63,.81,1),(0,-1,2))
point('Left lamp pool',(-2.99,-.83,2.71),32,(1,.49,.20))
point('Right lamp pool',(2.97,-.83,2.68),32,(1,.49,.20))
area('Awning reflected glow',(.65,-1.25,2.43),49,1.7,(1,.58,.24),(0,-1.65,1.08))
camera(s,'nov23-rook-street',(-3.08,-9.4,2.15),(-.16,-.70,2.62),(1420,1000),lens=35)
camera(s,'nov23-rook-counter',(-2.12,-5.12,1.57),(.31,-1.40,1.3),(1420,1000),lens=34)

manifest={
    'scope':'W04 visual staging, open-air frontage only. Not a walk-in interior, route, collision or trade implementation.',
    'catalogue_id':'WSC-SCENE-002',
    'reference':'originals/round-11-remaster/west/w04.jpg; W0b Main Street 72m; W2b Shops.',
    'actor':{'id':'WSC-ACTOR-018','placement_blender_m':[-.86,-1.73,0],'yaw_deg':12,'frame':19,
             'rig_joints':len(rig.data.bones),'authored_clip':'Idle_Studio','clip_length_s':3,
             'pose_motion_max_distance_m_at_frame_19':shift,
             'sha256':hashlib.sha256(packed.read_bytes()).hexdigest(), 'bytes':packed.stat().st_size},
    'donors':{k:dict(file=v[2],sha256=v[3],filter=v[4]) for k,v in sources.items()},
    'placement_axes':'Blender x,y,z metres (x,z,-y for glTF)',
    'placements':placements,
}
(out/'w2b-rook-counter-study.json').write_text(json.dumps(manifest,indent=2)+'\n')

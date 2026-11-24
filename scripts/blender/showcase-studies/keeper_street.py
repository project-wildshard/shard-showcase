"""W1a: exact two Main Street actor anchors; visual only, no town mesh export."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene,output_directory

out=output_directory()
repo=Path(__file__).resolve().parents[3]
assets=repo/'public/assets/wildshard-art'
pins={
 'wsc-plan-002-weapons-keeper.glb':'e1687e5d6db4f9555ad8c094f5cc1479e3931ba86c2977ba5c8c2b9978254aa1',
 'wsc-actor-018-tinker-rook.glb':'41a9d103fba6aea871d9f499da8c57678181a1783635477fe3927e1796626cba',
 'wsc-arch-006-shop-interior-kit.glb':'e2266b8e5bdc43a5399b70baac0f8a53c702618b7c7606062c1483d008ea670a',
}
for f,h in pins.items():
    assert hashlib.sha256((assets/f).read_bytes()).hexdigest()==h
town=Path(os.environ['WILDSHARD_TOWN_GLB'])
rook=Path(os.environ['WILDSHARD_ROOK_DECODED'])
parity=json.loads(town.with_name('parity.json').read_text())
town_hash=hashlib.sha256(town.read_bytes()).hexdigest()
assert parity['rebuilt_sha256']==town_hash
expected=json.loads((repo/'scripts/blender/west-town/expected.json').read_text())
assert parity['matched_signature'] in (
    expected['semantic_signature'],expected['normalized_semantic_signature']
)
clear_scene()
s=bpy.context.scene
s.render.fps=24

def load(file):
    prior=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(file))
    bpy.context.view_layer.update()
    return sorted(set(s.objects)-prior,key=lambda o:o.name)

world=load(town)
fascias=[o for o in world if o.type=='MESH' and 'fascia' in o.name.lower()]
assert any('weapons' in o.name.lower() for o in fascias) and any('tinker' in o.name.lower() for o in fascias),[o.name for o in fascias]
dg=bpy.context.evaluated_depsgraph_get()
def rr(x,y,hi=2,lo=-1):
    return s.ray_cast(dg,Vector((x,y,hi)),Vector((0,0,-1)),distance=hi-lo)
def support(x,y):
    hit,p,_,_,obj,_=rr(x,y)
    assert hit and abs(p.z)<.2,(x,y,p.z,obj)
    return p.z

def bbox(objs,eval_mesh=False):
    pts=[]
    for o in objs:
        if o.type=='MESH':
            if eval_mesh:o=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
            pts.extend(o.matrix_world@v.co for v in o.data.vertices)
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]

actor_bases={}
for key,file,x,y,yaw in [('Keeper',assets/'wsc-plan-002-weapons-keeper.glb',-64,-3.5,math.pi),
                         ('Rook',rook,-64,3.5,0)]:
    actor_bases[key]=[support(x,y),x,y]
counter_points=[support(x,y) for x in (-67.28,-66.15,-65.02) for y in (-5.04,-4.70,-4.36)]
assert max(counter_points)-min(counter_points)<.012
counter_z=max(counter_points)
src=load(assets/'wsc-arch-006-shop-interior-kit.glb')
pick=[o for o in src if o.type=='MESH' and o.name.startswith('Oak display counter')]
assert pick,[o.name for o in src]
cb=bbox(pick)
c=(.5*(cb[0][0]+cb[1][0]),.5*(cb[0][1]+cb[1][1]),cb[0][2])
tr=Matrix.Translation(Vector((-66.15,-4.70,counter_z))-Vector(c))
arr=[(o.data,o.matrix_world.copy()) for o in pick]
for obj in src:bpy.data.objects.remove(obj,do_unlink=True)
counter=[]
for i,(mesh,m) in enumerate(arr):
    o=bpy.data.objects.new('Oak counter exact part '+str(i+1),mesh)
    s.collection.objects.link(o);o.matrix_world=tr@m;counter.append(o)
bpy.context.view_layer.update()
cb=bbox(counter)
dims=[hi-lo for lo,hi in zip(*cb)]
assert all(abs(a-b)<.003 for a,b in zip(dims,(2.380,.849,1.052))),dims

def stage_actor(key,file,x,y,yaw,frame):
    obs=load(file)
    (rig,)=tuple(o for o in obs if o.type=='ARMATURE')
    assert len(rig.data.bones)==21
    assert rig.animation_data and len(rig.animation_data.nla_tracks)==1
    mesh=[o for o in obs if o.type=='MESH' and o.vertex_groups]
    assert len(mesh)==1
    # Some studio packages also carry an unskinned sample pedestal. It is not the NPC.
    extras=[o for o in obs if o.type=='MESH' and not o.vertex_groups]
    obs=[o for o in obs if o not in extras]
    for o in extras:bpy.data.objects.remove(o,do_unlink=True)
    s.frame_set(frame)
    lo,_=bbox(mesh,True)
    T=Matrix.Translation((x,y,actor_bases[key][0]-lo[2]))@Matrix.Rotation(yaw,4,'Z')
    for q in obs:
        if q.parent not in obs:q.matrix_world=T@q.matrix_world
    bpy.context.view_layer.update()
    posed=bbox(mesh,True)
    assert abs(posed[0][2]-actor_bases[key][0])<.003,(key,posed,actor_bases[key])
    assert 1.74<posed[1][2]-posed[0][2]<1.88,(key,posed)
    return posed
pose_frame=19
keeper=stage_actor('Keeper',assets/'wsc-plan-002-weapons-keeper.glb',-64,-3.5,math.pi,pose_frame)
rook_b=stage_actor('Rook',rook,-64,3.5,0,pose_frame)

# Measure the current facade front from the frontage at several heights.
dgraph=bpy.context.evaluated_depsgraph_get()
seps=[]
for x in (-67.29,-66.15,-65.01):
    for z in (counter_z+.2,counter_z+.6,counter_z+1.0):
        v=Vector((x,-5.70,z))
        hit,p,_,_,ob,_=s.ray_cast(dgraph,v,Vector((0,-1,0)),distance=2)
        assert hit and ('lot' in ob.name.lower()),(x,z,p,ob)
        seps.append(cb[0][1]-p.y)
actor_gap=keeper[0][0]-cb[1][0]
assert min(seps)>.4 and actor_gap>.39,(seps,actor_gap)
proof=dict(town_glb_sha256=town_hash,
           keeper_world_xz=[-64,3.5],rook_world_xz=[-64,-3.5],
           keeper_yaw=math.pi,rook_yaw=0,keeper_bounds=keeper,rook_bounds=rook_b,
           counter_dimensions=dims,counter_blender_xyz=[-66.15,-4.70,counter_z],
           sampled_paving_delta_m=max(counter_points)-min(counter_points),
           sampled_facade_min_m=min(seps),keeper_posed_x_gap_m=actor_gap,
           stage_frame=pose_frame,native_shop_or_spawn=False)
(out/'w1a-keeper-frontage-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print(proof)
if os.getenv('WILDSHARD_VALIDATE_ONLY')=='1':
    sys.exit(0)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
w=s.world or bpy.data.worlds.new('West warm daylight')
s.world=w;w.use_nodes=True
bg=w.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.31,.48,.60,1);bg.inputs[1].default_value=.55
bpy.ops.object.light_add(type='SUN',location=(-79,1,20))
o=bpy.context.object;o.data.energy=1.7;o.data.angle=.15;o.data.color=(1,.84,.65);aim(o,(-62,-4,0))
for p,t,watt,col,size in [
    ((-66,-.3,4.85),(-63,-4,1),260,(1,.72,.44),4.2),
    ((-67,.75,3.5),(-62,3.5,1),520,(.69,.82,1),5),
]:
    bpy.ops.object.light_add(type='AREA',location=p)
    o=bpy.context.object;o.data.energy=watt;o.data.size=size;o.data.color=col;aim(o,t)
bpy.ops.object.camera_add()
s.camera=bpy.context.object
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.06
s.render.resolution_x=1440;s.render.resolution_y=920;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=90
s.view_settings.view_transform='AgX'
for name,p,t,lens in [
    ('keeper-frontage',(-67.5,2.3,1.67),(-64.7,-4.7,2.18),32),
    ('keeper-main-street',(-79.5,.45,2.35),(-62,0,2.1),34),
]:
    s.camera.location=p;aim(s.camera,t);s.camera.data.lens=lens
    s.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)

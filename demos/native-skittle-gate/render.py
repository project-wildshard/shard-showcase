"""Photograph the original ramp with reimported GLBs at recorded gate/ball transforms."""
from pathlib import Path
import hashlib
import json
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

trace,out=map(Path,sys.argv[sys.argv.index('--')+1:])
out.mkdir(parents=True,exist_ok=True)
model=trace.parent
r=json.loads(trace.read_text())
scene=bpy.context.scene
assets=Path(__file__).resolve().parents[2]/'public/assets/wildshard-art'
ballfile=assets/'wsc-plan-004-rolling-ball.glb'
assert hashlib.sha256(ballfile.read_bytes()).hexdigest()=='c04881c87359049db80b6f17772628543628688dd6fee3c58e1bf6f7f3ebe171'

def pos(p):
    return p['x'],-p['z'],p['y']

def transform(roots,p,q=None):
    new=Matrix.Translation(pos(p))
    if q:
        new=new@Quaternion((q['w'],q['x'],-q['z'],q['y'])).to_matrix().to_4x4()
    for ob,base in roots:ob.matrix_world=new@base

def load(path):
    old=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [(ob,ob.matrix_world.copy()) for ob in set(scene.objects)-old if ob.parent is None]

# Hide scene-only balls; the original ramp and rails remain visible.
for ob in tuple(scene.objects):
    if 'shared scene-only study' in ob.name and 'ball ' in ob.name:ob.hide_render=True
lever='stand' in r
folder=assets if lever else model
if lever:
    for name,sha in r['donors'].items():
        assert hashlib.sha256((assets/name).read_bytes()).hexdigest()==sha
    for ob in tuple(scene.objects):
        if ('shared scene-only study' in ob.name and 'pin' in ob.name.lower()) or ob.name=='release lever and pin approach static arts':
            ob.hide_render=True
yy=load(folder/'w4b-ball-gate-yoke.glb')
transform(yy,r['blocked']['frames'][0]['bar'])
bar=load(folder/'w4b-ball-gate-bar.glb')
balls=[load(ballfile) for _ in range(4)]
if lever:
    stand=load(assets/'w4b-release-stand.glb')
    arm,=[o for o,_ in stand if o.name.startswith('Release_arm_localX_pivot')]
    transform(stand,r['stand'])
    arm_ready=arm.matrix_world.copy()
    pins=[load(assets/'wsc-plan-005-skittle-pin.glb') for _ in range(10)]

def pose(frame):
    transform(bar,frame['bar'])
    for body,roots in zip(frame['bodies'],balls):
        transform(roots,body['p'],body['q'])
    if lever:
        # Grip is visual staging; gate and pin poses are from the simulation.
        arm.matrix_world=arm_ready@Matrix.Rotation(.56*min(frame['tick']/36,1),4,'X')
        for body,roots in zip(frame['bodies'][4:],pins):
            p,q=body['p'],body['q']
            shift=Quaternion((q['w'],q['x'],-q['z'],q['y']))@Vector((0,0,-.645))
            transform(roots,{'x':p['x']+shift.x,'y':p['y']+shift.z,'z':p['z']-shift.y},q)
    bpy.context.view_layer.update()

scene.render.engine='CYCLES'
scene.cycles.samples=29
scene.cycles.adaptive_threshold=.045
scene.cycles.use_denoising=False
scene.render.image_settings.file_format='WEBP'
scene.render.image_settings.quality=89
scene.view_settings.view_transform='AgX'
scene.render.resolution_percentage=100
world=bpy.data.worlds.new('Physics Yard clear day')
scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.48,.62,.74,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.62
bpy.ops.object.light_add(type='SUN')
sun=bpy.context.object
sun.rotation_euler=Vector((-.58,-.32,-1)).to_track_quat('-Z','Y').to_euler()
sun.data.color=(1,.86,.69)
sun.data.energy=2.8
sun.data.angle=.14
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam

def render(n,eye,target,lens,res):
    cam.location=eye
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=res
    scene.render.filepath=str(out/(n+'.webp'))
    bpy.ops.render.render(write_still=True)

if 'replay' in r:
    roll=r['replay']
    eye=(-45.1,-190.8,4.05)
    aim=(-52.08,-196.05,.62)
    for key,frame in (
        ('result',roll['first']['frames'][-1]),
        ('reset',roll['resetFrame']),
        ('replay',roll['second']['frames'][-1])):
        pose(frame)
        render('nov26-w4b-score-'+key,eye,aim,42,(1240,840))
elif lever:
    feet=r['released']['activation']['arrived']
    pose(r['blocked']['frames'][0])
    render('nov26-w4b-player-lever', (feet[0],-feet[2],feet[1]+1.68),(-29.65,-200.0,1.62),25,(960,1280))
    pose(next(f for f in r['released']['frames'] if f['tick']==144))
    render('nov26-w4b-player-release',(-32,-204.1,7.85),(-27.4,-196.3,4.64),32,(1240,880))
    pose(r['released']['frames'][-1])
    render('nov26-w4b-player-settled',(-42.9,-193.5,3.2),(-52.0,-196.1,.75),34,(1240,880))
else:
    pose(r['blocked']['frames'][0])
    render('nov26-w4b-gate-held',(-17.6,-189.2,10.8),(-25.0,-196,5.15),38,(1360,900))
    pose(next(f for f in r['released']['frames'] if f['tick']==144))
    render('nov26-w4b-gate-raised',(-32.0,-192.1,6.7),(-25.9,-196,5.55),33,(804,1748))

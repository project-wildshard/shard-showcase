"""Editable rigid-part Crate Mite rig and local clips; no world movement baked into the actor."""
from pathlib import Path
import math,sys
import bpy
from mathutils import Quaternion,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import output_directory
from crate_mite import build

out=output_directory()
parts=build(True)
bpy.ops.object.select_all(action="DESELECT")
for ob in parts:
    label=ob.name
    if label.startswith(('Four short','Angled pressure','Short single-piece')):
        bone=('front' if ob.location.y<0 else 'rear')+('_l' if ob.location.x<0 else '_r')
    elif label.startswith('Sealed octagonal'):
        bone='eye'
    elif label.startswith(('Orange clamp','Flat restraint','Recessed nose','Lid edge')):
        bone='head'
    else:
        bone='body'
    ob.vertex_groups.new(name=bone).add(range(len(ob.data.vertices)),1.0,'REPLACE')
    ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
mesh=bpy.context.object;mesh.name='Crate Mite skinned mesh'
# Bake the active mesh's prior object offset into the geometry before binding.
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
a=bpy.data.armatures.new('crateMite')
rig=bpy.data.objects.new('Crate Mite rig',a);bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig
mesh.select_set(False);rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
def edit_bone(n,H,T,parent=None):
    q=a.edit_bones.new(n);q.head=H;q.tail=T
    if parent:q.parent=a.edit_bones[parent]
edit_bone('body',(0,0,.227),(0,0,.44))
edit_bone('head',(0,0,.44),(0,0,.60),'body')
edit_bone('eye',(0,-.269,.365),(0,-.269,.46),'body')
for region,y in [('front',-.172),('rear',.172)]:
    for side,x in [('l',-.238),('r',.238)]:
        edit_bone(f'{region}_{side}',(x,y,.23),(x,y,.065),'body')
bpy.ops.object.mode_set(mode='OBJECT')
mesh.parent=rig
m=mesh.modifiers.new('Mite rigid skeletal binding','ARMATURE');m.object=rig
s=bpy.context.scene;s.render.fps=30
rig.animation_data_create()
legs=['front_l','front_r','rear_l','rear_r']
def F(dz=0,dy=0,rx=0,rz=0,leg=None,fl=0,head=0):
    dest={'body':((0,dy,dz),rx,rz,1),'head':((0,0,0),head,0,1),'eye':((0,0,0),0,0,max(.018,1+fl))}
    for n,x in zip(legs,leg or [0,0,0,0]):dest[n]=((0,0,0),x,0,1)
    return dest
def clip(name,frames):
    act=bpy.data.actions.new(name);rig.animation_data.action=act
    for fr,state in frames:
        for n,(move,rx,rz,size) in state.items():
            pb=rig.pose.bones[n];pb.rotation_mode='QUATERNION'
            axes=pb.bone.matrix_local.to_3x3().inverted()
            pb.location=axes@Vector(move)
            pb.rotation_quaternion=Quaternion(axes@Vector((0,0,1)),rz)@Quaternion(axes@Vector((1,0,0)),rx)
            pb.scale=(size,size,size)
            for path in ('location','rotation_quaternion','scale'):pb.keyframe_insert(path,frame=fr,group=n)
    rig.animation_data.action=None
    track=rig.animation_data.nla_tracks.new();track.name=name
    strip=track.strips.new(name,0,act);strip.name=name;strip.blend_type='REPLACE'
    track.mute=True
neutral=F()
clip('idle',[(0,neutral),(15,F(dz=.018,head=.026)),(30,neutral)])
walk=[(0,F(leg=[.40,-.40,-.40,.40])),(6,F(dz=.024)),(12,F(leg=[-.40,.40,.40,-.40])),(18,F(dz=.024)),(24,F(leg=[.40,-.40,-.40,.40]))]
clip('walk',walk)
clip('run',[(round(t*2/3),f) for t,f in walk])
clip('turn',[(0,neutral),(6,F(rz=.18,leg=[.24,-.12,.14,-.21])),(12,F(rz=-.13,leg=[-.24,.12,-.14,.21])),(18,neutral)])
clip('telegraph',[(0,neutral),(12,F(dz=-.071,rx=.085,fl=.05)),(18,F(dz=-.10,rx=.12,fl=.27))])
clip('attack.bite',[(0,neutral),(12,F(dz=-.071,rx=.085)),(18,F(dz=-.10,rx=.12,fl=.27)),(22,F(dz=.14,dy=-.13,rx=-.27,leg=[.21,.21,-.30,-.30])),(27,F(dz=-.035,rx=.13)),(36,neutral)])
clip('attack.overclock',[(0,neutral),(8,F(dz=-.034,fl=.38,head=.18)),(16,F(dz=-.071,fl=-.17,head=-.17)),(23,F(dz=-.10,fl=.45,rx=.12)),(28,F(dz=.18,dy=-.18,rx=-.33,leg=[.27,.27,-.33,-.33])),(36,F(dz=-.07,rx=.15)),(44,neutral)])
clip('hit',[(0,neutral),(4,F(dz=-.021,dy=.09,rx=.21,rz=.08,fl=-.38)),(12,neutral)])
clip('die',[(0,neutral),(7,F(dz=.056,dy=.06,rx=.30,head=.27)),(16,F(dz=-.174,rx=-.43,rz=.16,leg=[.4,-.4,-.5,.5],fl=-1,head=.39)),(29,F(dz=-.186,rx=-.51,rz=.20,leg=[.50,-.50,-.52,.52],fl=-1,head=.48))])
sleep=F(dz=-.166,leg=[-.66,-.66,.66,.66],fl=-1)
clip('sleep',[(0,sleep),(30,sleep)])
clip('wake',[(0,sleep),(6,F(dz=-.14,leg=[-.43,-.43,.43,.43],fl=-.50)),(16,neutral)])
# The runtime, not the source Blender scene, chooses which clip to play.
for track in rig.animation_data.nla_tracks:track.mute=False
s.frame_set(0)
bpy.ops.object.select_all(action='DESELECT')
for ob in (mesh,rig):ob.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(out/'wsc-actor-001-crate-mite-rig.glb'),
    export_format='GLB',use_selection=True,export_animations=True,
    export_animation_mode='NLA_TRACKS',export_frame_range=False,
    export_force_sampling=True,export_optimize_animation_size=True)
for track in rig.animation_data.nla_tracks:track.mute=track.name!='idle'
s.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'crate-mite-rig-edit.blend'),compress=True)
print('Skin export and editable source complete',flush=True)

"""Build the pose-test armature over the editable fitted-plate model, not over the sculpt underlay."""
import bpy, sys, json, re, math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:]
out=Path(args[0]);out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
is_hybrid=scene.get('executioner_fit') in {'hybrid','mantle'}
if is_hybrid:
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from hybrid_fit import fit
model=bpy.data.collections['Executioner | Editable Form']
ad=bpy.data.armatures.new('Executioner | pose skeleton')
rig=bpy.data.objects.new(ad.name,ad);model.objects.link(rig)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
bpy.context.view_layer.objects.active=rig;rig.show_in_front=True;bpy.ops.object.mode_set(mode='EDIT')
spec={}
def bone(n,a,b,parent=None):
    if is_hybrid:a,b=fit(a),fit(b)
    x=ad.edit_bones.new(n);x.head=a;x.tail=b
    if parent:
        x.parent=ad.edit_bones[parent]
        x.use_connect=(x.head-x.parent.tail).length<.0001
    spec[n]=(Vector(a),Vector(b));return x
bone('root',(0,0,.018),(0,0,.15)).use_deform=False
bone('pelvis',(0,.019,.97),(0,.013,1.15),'root')
bone('spine',(0,.013,1.15),(.012,.012,1.37),'pelvis')
bone('chest',(.012,.012,1.37),(.01,.009,1.59),'spine')
bone('neck',(.01,.009,1.59),(.013,-.022,1.71),'chest')
bone('head',(.013,-.022,1.71),(.013,.006,1.94),'neck')
for side, shoulder, elbow, wrist, hip, knee, ankle in [
 ('R',(.205,.015,1.544),(.331,-.029,1.265),(.401,-.107,1.043),
  (.095,.014,1.006),(.130,-.072,.555),(.192,-.104,.090)),
 ('L',(-.186,.027,1.537),(-.322,.041,1.263),(-.394,-.016,1.027),
  (-.097,.023,1.009),(-.137,.040,.550),(-.230,.102,.091))]:
    sign=1 if side=='R' else -1
    def short(n):return n+'.'+side
    bone(short('clavicle'),(.04*sign,.014,1.51),shoulder,'chest')
    bone(short('upper_arm'),shoulder,elbow,short('clavicle'))
    bone(short('forearm'),elbow,wrist,short('upper_arm'))
    x,y,z=wrist
    bone(short('hand'),wrist,(x,y-.018,z-.092),short('forearm'))
    for digit in range(4):
        xx=x+(digit-1.45)*.016
        bone(short('finger_%s'%digit),(xx,y-.023,z-.074),(xx-sign*.007,y-.040,z-.074-(.066-.006*abs(digit-1))),short('hand'))
    bone(short('thumb'),(x-sign*.025,y-.002,z-.022),(x-sign*.048,y-.024,z-.065),short('hand'))
    bone(short('thigh'),hip,knee,'pelvis')
    bone(short('shin'),knee,ankle,short('thigh'))
    x,y,z=ankle;bone(short('foot'),ankle,(x,y-.127,.048),short('shin'))
    bone(short('apron'),(.097*sign,-.119,1.13),(.127*sign,-.17,.52),'pelvis')
    bone(short('mantle'),(.097*sign,.106,1.12),(.139*sign,.125,.58),'pelvis')
bpy.ops.object.mode_set(mode='OBJECT')

def rigid(name):
    if name.startswith(('Ceramic','Helmet','Visor','Kiln enamel','Hood')):return 'head'
    if name.startswith(('Gorget','Neck cowl')):return 'neck'
    if name.startswith(('Cuirass','Dorsal','Forged diagonal','Shoulder mantle')):return 'chest'
    if name.startswith(('Waist belt','Overlapping','Apron suspension')):return 'pelvis'
    if name.startswith(('Right pauldron','Right rerebrace','Right lower','Pauldron raised')):return 'upper_arm.R'
    if name.startswith('Left fireproof'):return 'upper_arm.L'
    if name.startswith('Hand-shaped'):return 'forearm.'+name[-1]
    if name.startswith(('Shin','Rounded knee')):return 'shin.'+name.partition(' | raised hem')[0][-1]
    if name.startswith('Hanging curved'):return 'thigh.'+name[-1]
    if name.startswith('Boot'):return 'foot.'+name.split()[1]
    if name.startswith(('Glove cuff','Glove palm')):return 'hand.'+name[-1]
    if name.startswith('Glove digit'):return 'finger_'+name[-1]+'.'+name[-2]
    if name.startswith('Opposing thumb'):return 'thumb.'+name[-1]
    if name.startswith(('Front leather','Rear split')):
        tail='apron' if name.startswith('Front') else 'mantle'
        return tail+'.'+('L' if 'left' in name else 'R')
    raise KeyError(name)

def smooth(x):
    t=max(0,min(1,x));return t*t*(3-2*t)
def blend_weights(v,one,two,reach):
    a,hinge=spec[one];_,b=spec[two];axis=((hinge-a).normalized()+(b-hinge).normalized()).normalized()
    mix=smooth(.5+(v-hinge).dot(axis)/(2*reach))
    return {one:1-mix,two:mix}
report={'fit':scene.get('executioner_fit','authored'),'bones':len(ad.bones),'armatureMeshes':[],'rigidParts':[]}
for ob in list(model.objects):
    if ob==rig:continue
    name=ob.name
    if name.startswith(('Continuous sleeve','Continuous trousers','Quilted suit','Shoulder mantle | asymmetric')):
        assert ob.type=='MESH'
        mod=ob.modifiers.new('Weighted pose deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True
        ob.modifiers.move(len(ob.modifiers)-1,0)
        if name.startswith('Quilted'):func=lambda v: {'pelvis':1-smooth((v.z-1.07)/.43),'chest':smooth((v.z-1.07)/.43)}
        elif name.startswith('Shoulder mantle'):
            # The neck hangs from chest; the wrapping hem rides the outer upper arm instead of cutting through it.
            def func(v):
                w=.93*smooth((-v.x-.112)/.192)
                return {'chest':1-w,'upper_arm.L':w}
        else:
            short=name[-1]
            a,b,r=('upper_arm','forearm',.10) if 'sleeve' in name else ('thigh','shin',.125)
            func=lambda v:blend_weights(v,a+'.'+short,b+'.'+short,r)
        groups={}
        for v in ob.data.vertices:
            weights=func(v.co)
            assert abs(sum(weights.values())-1)<1e-6
            for n,w in weights.items():
                if w<=0:continue
                if n not in groups:groups[n]=ob.vertex_groups.new(name=n)
                groups[n].add([v.index],w,'REPLACE')
        report['armatureMeshes'].append(name)
    else:
        dn=rigid(name);mat=ob.matrix_world.copy()
        ob.parent=rig;ob.parent_type='BONE';ob.parent_bone=dn
        bpy.context.view_layer.update()
        ob.matrix_world=mat
        report['rigidParts'].append({'object':name,'bone':dn})

def angle(n,x=0,y=0,z=0):
    pb=rig.pose.bones[n];pb.rotation_mode='XYZ';pb.rotation_euler=[math.radians(t) for t in (x,y,z)]
# Weight-driven crouch and high forearm; designed to expose mannequin gaps, not simulate an attack.
def boot_min(side):
    ob=model.objects['Boot '+side+' | toe and instep'].evaluated_get(bpy.context.evaluated_depsgraph_get())
    me=ob.to_mesh()
    low=min((ob.matrix_world @ v.co).z for v in me.vertices)
    ob.to_mesh_clear()
    return low

def pose(frame,key):
    ad.pose_position='POSE'
    for pb in rig.pose.bones:pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.location=(0,0,0)
    if key=='guard':
        angle('chest',x=9,z=6);angle('neck',x=-6,y=-9);angle('head',x=-5,y=11)
        angle('upper_arm.R',x=-19,y=-8,z=15);angle('forearm.R',x=-35,z=6)
        angle('upper_arm.L',x=9,z=-14);angle('forearm.L',x=-22,z=-4)
        angle('thigh.R',x=-9,z=-3);angle('shin.R',x=12)
        angle('thigh.L',x=10,z=7);angle('shin.L',x=15);angle('foot.L',x=-13)
        angle('apron.R',x=-7,y=4);angle('mantle.R',x=7,y=3)
        angle('apron.L',x=7,y=-6);angle('mantle.L',x=9,y=5)
        for side in 'LR':
            for i in range(4):angle('finger_'+str(i)+'.'+side,x=-28+i*4)
    bpy.context.view_layer.update()
    root=rig.pose.bones['root']
    # Align the lowest sole with the studio floor. This is a fixed-pose
    # diagnostic and does not replace foot locking during locomotion.
    delta=.009-min(boot_min('R'),boot_min('L'))
    root.location=root.bone.matrix_local.to_3x3().inverted() @ Vector((0,0,delta))
    bpy.context.view_layer.update()
    soles={side:round(boot_min(side),6) for side in 'LR'}
    assert abs(min(soles.values())-.009)<.0002,soles
    report[key]={'frame':frame,'soleZ':soles}
    for pb in rig.pose.bones:
        pb.keyframe_insert(data_path='rotation_euler',frame=frame,group=pb.name)
        if pb.name=='root':pb.keyframe_insert(data_path='location',frame=frame,group=pb.name)
    scene.frame_set(frame)
pose(1,'rest');pose(25,'guard')
action=rig.animation_data.action;action.name='Study | guard pose test, not a production clip'
scene.frame_start=1;scene.frame_end=25
root=rig.pose.bones['root']
if rig.animation_data:
    scene.frame_set(1);bpy.context.view_layer.update()
    assert abs(min(boot_min('R'),boot_min('L'))-.009)<.0002
    scene.frame_set(25);bpy.context.view_layer.update()
    assert abs(min(boot_min('R'),boot_min('L'))-.009)<.0002
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'executioner-pose-study.blend'),compress=True)
(out/'rig-proof.json').write_text(json.dumps(report,indent=2)+'\n')
scene.cycles.samples=24;scene.cycles.use_denoising=False
scene.render.filepath=str(out/'executioner-pose-guard.png')
bpy.ops.render.render(write_still=True)
scene.frame_set(1)
scene.render.filepath=str(out/'executioner-pose-rest.png')
bpy.ops.render.render(write_still=True)

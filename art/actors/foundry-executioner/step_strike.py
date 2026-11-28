"""Pose the single Executioner's planted step and air-strike study, at 30 fps.

The step is translatable root motion, not a locomotion cycle. The contact frame
is an animation marker; there is no target, hitbox, damage or combat AI.
"""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Matrix, Vector, Euler

out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
col=bpy.data.collections['Executioner | Editable Form']
rig=col.objects['Executioner | pose skeleton']
assert scene.get('executioner_fit')=='mantle'
rig.animation_data_clear()
scene.render.fps=30;scene.render.fps_base=1
scene.frame_start=1;scene.frame_end=61
steps=({'frame':1,'label':'Rest'},{'frame':17,'label':'Lift'},{'frame':25,'label':'Plant'},
       {'frame':35,'label':'Windup'},{'frame':41,'label':'Strike'},{'frame':61,'label':'Recover'})
scene.timeline_markers.clear()
for step in steps:scene.timeline_markers.new(step['label'],frame=step['frame'])
pb=rig.pose.bones
rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
joints={name:m.translation.copy() for name,m in rest.items()}

def track(points,frame):
    # Cubic ease at authored beats; bake every frame after the IK solves.
    for (a,x),(b,y) in zip(points,points[1:]):
        if frame<=b:
            t=max(0,min(1,(frame-a)/(b-a)));e=t*t*(3-2*t)
            if isinstance(x,tuple):return tuple(i+(j-i)*e for i,j in zip(x,y))
            return x+(y-x)*e
    return points[-1][1]

def rotate(name,angles):
    pb[name].rotation_mode='QUATERNION'
    pb[name].rotation_quaternion=Euler(tuple(math.radians(v) for v in angles),'XYZ').to_quaternion()

def orient(name,head,tail):
    r=rest[name].to_quaternion()
    direction=r @ Vector((0,1,0))
    desired=tail-head
    if desired.length<1e-5:raise ValueError(name+' collapsed')
    r=direction.rotation_difference(desired.normalized())@r
    pb[name].matrix=Matrix.Translation(head) @ r.to_matrix().to_4x4()

def angle_chain(start,middle,end,target,bend):
    a=pb[start].head.copy()
    l1=(joints[middle]-joints[start]).length;l2=(joints[end]-joints[middle]).length
    v=target-a
    d=min(v.length,l1+l2-.00015)
    if d<abs(l1-l2)+.001:raise ValueError('Bad reach: '+start)
    n=v.normalized()
    pole=bend-n*n.dot(bend)
    if pole.length<.00001:raise ValueError('Collinear pole: '+start)
    mid=(l1*l1-l2*l2+d*d)/(2*d)
    c=a+n*mid+pole.normalized()*math.sqrt(max(0,l1*l1-mid*mid))
    b=a+n*d
    orient(start,a,c);bpy.context.view_layer.update()
    orient(middle,c,b);bpy.context.view_layer.update()
    return b

def mesh_floor(name):
    ob=col.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    me=ob.to_mesh()
    z=min((ob.matrix_world@v.co).z for v in me.vertices)
    ob.to_mesh_clear()
    return z

boot={s:['Boot '+s+' | toe and instep','Boot '+s+' | leather welt'] for s in 'LR'}
def sole(s):return min(mesh_floor(n) for n in boot[s])
def leg(s,f,end):
    n='foot.'+s
    base=joints[n]
    tgt=base+Vector((-.022 if s=='R' else 0,-.36 if s=='R' else 0,0))*end
    lift=track([(1,0),(10,0),(17,.136),(25,0),(61,0)],f) if s=='R' else 0
    tgt.z+=lift
    thigh,shin='thigh.'+s,'shin.'+s
    natural=joints[shin]-joints[thigh]
    if f>1:
        natural=natural.lerp(Vector((-.035 if s=='L' else .025,-.22,-.02)),track([(1,0),(17,.45),(25,.8),(61,.8)],f))
    q=angle_chain(thigh,shin,n,tgt,natural)
    # Keep sole orientation static during and after the plant. Only the
    # right swing foot pitches to clear the toe in the air.
    pitch=track([(1,0),(10,0),(17,12),(25,0),(61,0)],f) if s=='R' else 0
    foot_rotation=Euler((math.radians(pitch),0,0),'XYZ').to_matrix().to_4x4()
    rot=rest[n].to_quaternion().to_matrix().to_4x4()
    pb[n].matrix=Matrix.Translation(q)@foot_rotation@rot
    bpy.context.view_layer.update()
    return (q-tgt).length

# World-space wrist offsets from its rest joint, not calibrated to a game hit test.
right=[(1,(0,0,0)),(10,(-.015,-.055,.115)),(25,(-.058,-.010,.182)),
       (35,(-.096,.062,.246)),(41,(-.106,-.689,.279)),(46,(-.068,-.548,.195)),(61,(-.082,-.341,.123))]
left=[(1,(0,0,0)),(10,(.056,-.127,.149)),(25,(.119,-.285,.223)),
      (35,(.124,-.341,.219)),(41,(.068,-.387,.180)),(46,(.078,-.309,.174)),(61,(.092,-.322,.141))]
metrics=[]
for f in range(1,62):
    scene.frame_set(f)
    for b in pb:
        b.location=(0,0,0);b.rotation_mode='QUATERNION';b.rotation_quaternion=(1,0,0,0);b.scale=(1,1,1)
    bpy.context.view_layer.update()
    root_shift=Vector(track([(1,(0,0,0)),(10,(-.022,.018,-.026)),(17,(-.008,-.050,-.053)),
       (25,(.020,-.165,-.094)),(35,(.021,-.180,-.108)),(41,(.043,-.279,-.113)),
       (46,(.028,-.257,-.100)),(61,(.018,-.190,-.090))],f))
    # A 0.9 cm stage reference from the source guard establishes the ground plane.
    pb['root'].location=rest['root'].to_3x3().inverted()@root_shift
    rotate('pelvis',track([(1,(0,0,0)),(17,(5,0,4)),(35,(7,0,-6)),(41,(13,0,8)),(61,(5,0,2))],f))
    rotate('spine',track([(1,(0,0,0)),(17,(-4,5,0)),(35,(-7,13,-2)),(41,(-11,-12,3)),(61,(-1,0,0))],f))
    rotate('chest',track([(1,(0,0,0)),(17,(-8,6,-3)),(35,(-9,18,-4)),(41,(-16,-16,6)),(61,(-5,-1,0))],f))
    rotate('head',track([(1,(0,0,0)),(25,(8,-5,0)),(35,(6,-14,0)),(41,(6,12,-5)),(61,(2,0,0))],f))
    bpy.context.view_layer.update()
    foot_blend=track([(1,0),(10,0),(25,1),(61,1)],f)
    reach={s:leg(s,f,foot_blend) for s in 'LR'}
    for s,table in [('R',right),('L',left)]:
        sign=1 if s=='R' else -1
        n='hand.'+s
        pose=joints[n]+Vector(track(table,f))
        a='upper_arm.'+s;k='forearm.'+s
        restbend=joints[k]-joints[a]
        wave=track([(1,0),(10,.65),(25,1),(61,1)],f)
        elbow=restbend.lerp(Vector((sign*.29,.015,-.18)),wave)
        q=angle_chain(a,k,n,pose,elbow)
        # Turn the hand with the forearm; the baked glove follows its bone.
        if f>1:
            fwd=(q-pb[k].head).normalized()
            orient(n,q,q+fwd*.09)
        for i in range(4):
            rotate('finger_'+str(i)+'.'+s,(track([(1,0),(10,-14),(25,-32),(41,-42),(61,-20)],f),0,0))
    for s,sign in [('R',1),('L',-1)]:
        rotate('apron.'+s,(track([(1,0),(17,-8*sign),(25,8*sign),(38,-5*sign),(44,15*sign),(61,3*sign)],f),0,0))
        rotate('mantle.'+s,(track([(1,0),(17,7*sign),(27,-6*sign),(41,5*sign),(61,1*sign)],f),0,0))
    bpy.context.view_layer.update()
    feet={s:[round(v,6) for v in pb['foot.'+s].head] for s in 'LR'}
    metrics.append({'frame':f,'feet':feet,'soleZ':{s:round(sole(s),6) for s in 'LR'},
                    'reachError':{s:round(reach[s],6) for s in 'LR'},
                    'rightWrist':[round(v,6) for v in pb['hand.R'].head]})
    for b in pb:
        for path in ('location','rotation_quaternion'):
            b.keyframe_insert(data_path=path,frame=f,group=b.name)
rig.animation_data.action.name='Executioner Planted Strike'
for curve in rig.animation_data.action.fcurves:
    for k in curve.keyframe_points:k.interpolation='LINEAR'
scene.frame_set(1)
(out/'step-baked.json').write_text(json.dumps({'fps':30,'diagnosticOnly':True,'beats':steps,'samples':metrics},indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'executioner-step-study.blend'),compress=True)

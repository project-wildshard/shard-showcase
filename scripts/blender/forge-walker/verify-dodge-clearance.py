"""Sample the authored Dodge without other action strips or scene dressing."""
import bpy
import json
from mathutils import Vector

scene=bpy.context.scene
rig=next(o for o in scene.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:track.mute=track.name!='Dodge'
soles=[o for o in rig.children if o.type=='MESH' and o.parent_bone.startswith('boot_')]
assert len(soles)==4
rows=[]
for i in range(61):
 frame=1+i/4
 scene.frame_set(int(frame),subframe=frame%1)
 lowest=min((o.matrix_world@Vector(v)).z for o in soles for v in o.bound_box)
 offset=rig.pose.bones['root'].location.length
 assert offset<1e-7
 rows.append((frame,lowest))
integer=min(y for f,y in rows if f%1==0);full=min(y for f,y in rows)
assert integer>=.0129 and full>=0, (integer,full)
print('DODGE_CLEARANCE '+json.dumps({'samples':len(rows),'minSoleBoxAtExportFramesMeters':round(integer,6),
 'minSoleBoxAtQuarterFramesMeters':round(full,6),'rootMoved':False}))

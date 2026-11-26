"""Render the recorded parked-crate transforms in the existing authored room."""
from pathlib import Path
import json
import sys
import bpy
from mathutils import Matrix, Quaternion, Vector

root=Path(__file__).resolve().parents[2]
script=root/'scripts/blender/showcase-studies/vault_puzzle_room.py'
# Reuse the room's source up to its original camera renders, without altering the original release.
ctx={'__file__':str(script),'__name__':'__main__'}
exec(compile(script.read_text().split('report={',1)[0],str(script),'exec'),ctx)
out=ctx['out']
replays=json.loads((out/'replay.json').read_text())
assert len(replays)==2
locked,flush=replays
comparison=locked['add'] and flush.get('lockYaw',False)
assert locked['settled']['held']==[True,False] and flush['settled']['held']==[True,True]
s=ctx['s']
s.cycles.samples=48
for o in ctx['ceiling']+ctx['walls']:
    o.hide_render=True
ctx['box']('Review cyclorama',(0,0,-.42),(100,100,.17),ctx['cladding'])
ctx['light']('Wide key',(-6,-6,11),(0,0,0),1550,10,(.88,.93,1),.4)
ctx['light']('Wide fill',(5,7,10),(0,0,0),1170,9,(.7,.87,1),.4)
crate=next(o for o in bpy.context.scene.objects if o.name.startswith('Spare crate at start ·'))
origin=crate.matrix_world.copy()
initial_center=Vector((1.25,-2.32,.112))
center_y=.8635/2
def move(r):
    p=r['settled']['crate']; rot=r['settled']['rotation']
    new_center=Vector((p[0],-p[2],p[1]))
    q=Quaternion((rot[3],rot[0],-rot[2],rot[1]))
    crate.matrix_world=Matrix.Translation(new_center) @ q.to_matrix().to_4x4() @ Matrix.Translation(
        -initial_center-Vector((0,0,center_y))) @ origin

def review(file):
    ctx['render'](file,(6.3,-9.5,8.7),(.05,.5,.72),(1120,880),46,13.3)

if not comparison:
    move(locked)
    review('e10c-raised-plate.jpg')
move(flush)
a=next(o for o in bpy.context.scene.objects if o.name.startswith('Crate on plate A ·'))
a.location.z-=.14625
for o in tuple(bpy.context.scene.objects):
    if o.name.startswith(('Plate A ·','Plate B ·')):
        o.hide_render=True
for cx in (-2.2,2.2):
    pre=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(out/'e10c-vault-flush-plate.glb'))
    for o in set(bpy.context.scene.objects)-pre:
        if not o.parent:
            o.location+=Vector((cx,2.35,.112))
    # Keep identical scenery in the full-input comparison.
    if not comparison:
        for y in (1.46,3.24):
            ctx['box']('Flush plate status rail',(cx,y,.117),(.94,.021,.014),ctx['green'],.005)
for o in bpy.context.scene.objects:
    if not comparison and o.name.startswith(('Plate side inlay','Plate front inlay','Paced inset route marker')) and o.location.x>0:
        o.data.materials[0]=ctx['green']
if comparison:
    for key,run in [('free',locked),('fixed',flush)]:
        move(run)
        review(f'e10c-full-push-{key}.jpg')
else:
    review('e10c-flush-plate.jpg')

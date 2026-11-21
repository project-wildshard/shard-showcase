import bpy,math
from pathlib import Path
from mathutils import Vector
P=OUT;S=bpy.context.scene
# Editable .blend is equivalent exported geometry; import final deliverable for proof.
for o in list(S.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(P/'west-linked-r02.glb'));S.cycles.samples=32
for name,pos,target,lens,sz in [('03-full-zone-overview',(20,-55,140),(-100,120,0),24,(1600,1000)),('04-mounted-arrival',(-52,149,2.6),(-130,148,3),None,(804,1748))]:
 bpy.ops.object.camera_add(location=pos);cam=bpy.context.object;cam.name=name;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.clip_end=1200
 if lens:cam.data.lens=lens
 else:cam.data.angle=math.radians(66)
 S.camera=cam;S.render.resolution_x,S.render.resolution_y=sz;S.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True) if RENDER else None
print('OVERVIEW MOUNTED COMPLETE')

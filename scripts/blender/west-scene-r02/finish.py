import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=OUT;P.mkdir(parents=True,exist_ok=True);S=bpy.context.scene;removed=[]
for o in list(S.objects):
 n=o.name;erase=n.startswith(('Stable WIP','Stable arcade','Stable pitched roof','Stable ridge','Stable Gate beam','Gate teal banner','Gold band'))
 if n.startswith(('Gate pier','Pier crown')) and -45<o.matrix_world.translation.x< -27:erase=True
 if erase:removed.append(n);bpy.data.objects.remove(o,do_unlink=True)
f=STABLE_FILE;bpy.ops.import_scene.gltf(filepath=str(f))
def box(n,loc,dim,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(bpy.data.materials[ma]);return o
# Plan's exact north back alley x[-127,-42], mapz[-36,-32], and crosslane x[-99,-91].
box('R02 source north back alley west',(-113,34,.035),(28,4,.07),'path')
box('R02 source north back alley east',(-66.5,34,.035),(49,4,.07),'path')
box('R02 source cross lane north fragment',(-95,39.5,.035),(8,39,.07),'path')
# Quiet walking apron links stable west entrance to12m Stable Lane; no lane obstructions.
box('R02 stable west approach apron',(-29,47,.04),(2,18,.08),'sand')
box('R02 stable north arcade apron',(-19,57.8,.04),(18,3.6,.08),'sand')
for x in (-42.3,-29.7):box('R02 low lane curb',(x,39.5,.09),(.2,39,.18),'capstone')
# Small paved stoops link existing houses to back alley. House fronts face north after yawpi in this scene.
for x,y in [(-53,47),(-72,47),(-114,47),(-53,25),(-76,25),(-114,25)]:
 target=34;start=y-3.5 if y>34 else y+3.5;box('R02 house-to-alley walkway',(x,(start+target)/2,.03),(2.2,abs(start-target),.06),'sand')
# Reuse the same planted tree meshes in street verges without changing original model dimensions.
pr=[o for o in S.objects if o.type=='MESH' and o.name.startswith('Existing oak planted verge')]
# Find first prototype occurrence via exact shared name before suffix. Easier import once and instance from matrices.
a=REPO/'public/assets/wildshard-art/wsc-prop-012-deciduous-tree.glb';before=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(a));objs=sorted(set(S.objects)-before,key=lambda obj:obj.name)
for i,(x,y) in enumerate([(-46,30),(-46,53),(-85,40),(-105,40),(-84,24),(-120,57),(-22,63)]):
 for o in objs:
  if o.type=='MESH':
   c=bpy.data.objects.new('R02 street grove '+str(i)+' | '+o.name,o.data);S.collection.objects.link(c);c.matrix_world=Matrix.Translation((x,y,0))@o.matrix_world
for o in objs:bpy.data.objects.remove(o,do_unlink=True)
# Grounded meadow margins at boundaries, not forests inserted into the allocated Movers zone.
for x in (-63.3,-12.7):box('R02 paddock worn verge',(x,102,.015),(1.6,61,.03),'sand')
# Deliberate entry apron highlights the existing12m route; soil edge replaces hard grass-to-road join.
box('R02 gate approach shoulder',(-36,66,.015),(13.6,12,.03),'sand')
# Private display mounting correction: clear the gantry beam rather than hiding digits.
for o in S.objects:
 if o.name.startswith('Lap timer display on gantry'):o.location.z-=.35
# Separate roundtrip export, baseline untouched.
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'west-linked-r02.glb'),export_format='GLB',use_selection=True,export_apply=True)
(P/'revision.json').write_text(json.dumps({'baseline':'generated from tracked assemble.py and dependencies.json','frontage_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'removed_proxy_objects':removed,'new_groundwork':'exact source north back alley/crosslane; inferred stable apron, house footpaths, low curb, verges and grove','unchanged':'paddock48x60, oval208x88, eight rings, four jumps, source trough/mount anchors','status':'private WIP; no gameplay or qualification'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'west-linked-r02-editable.blend'))
# Final views show only mesh data that survived export/import, with original light controls.
for o in list(S.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(P/'west-linked-r02.glb'))
S.cycles.samples=40
for name,pos,target,lens in [('01-stable-lane-linked-context',(-59,21,18),(-22,74,2),31),('02-stable-lane-player-eye',(-36,38,1.75),(-27,62,4.2),23)]:
 bpy.ops.object.camera_add(location=pos);cam=bpy.context.object;cam.name=name;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_end=1200;S.camera=cam;S.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True) if RENDER else None
bpy.ops.wm.save_as_mainfile(filepath=str(P/'west-linked-r02-export-review.blend'));print('R02 COMPLETE')

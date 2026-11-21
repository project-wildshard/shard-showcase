import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[sys.argv.index('--')+1]).resolve() if '--' in sys.argv else Path.cwd()/'tmp/w10-mounting-block'
P.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,rough=.6):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*c,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=rough;return m
cedar=[mat('Cedar honey',(.39,.23,.11)),mat('Cedar warm',(.28,.14,.065)),mat('Cedar light',(.44,.28,.14))]
teal=mat('Paddock teal',(.055,.27,.26));iron=mat('Dark iron',(.045,.065,.07),.65);zinc=mat('Fastener zinc',(.38,.43,.42),.75,.35);cream=mat('Cream tread edge',(.78,.77,.65))
def finish(o,m,b=.006):
 o.data.materials.append(m)
 if b:
  a=o.modifiers.new('Small softened edges','BEVEL');a.width=b;a.segments=2
  o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def box(n,loc,dim,m,b=.006):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,m,b)
# Three 180mm rises: first two treads 320mm, upper mounting platform 480mm.
# Front is -Y; open right/left horse approach. No interaction/collision authored.
for x in [-.35,.35]:box('Ground skid',(x,0,.025),(.105,1.16,.05),iron)
profile=[(-.55,.05),(.55,.05),(.55,.49),(.08,.49),(.08,.31),(-.24,.31),(-.24,.13),(-.55,.13)]
for x in [-.365,.365]:
 verts=[(xx,y,z) for xx in [x-.0275,x+.0275] for y,z in profile];N=len(profile);faces=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 me=bpy.data.meshes.new('Stepped side mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Continuous stepped side cheek',me);bpy.context.collection.objects.link(o);finish(o,teal)
for si,(start,end,h) in enumerate([(-.56,-.24,.18),(-.24,.08,.36),(.08,.56,.54)]):
 depth=end-start;num=3 if si<2 else 4
 for j in range(num):
  d=depth/num;box('Tread %s plank %s'%(si+1,j+1),(0,start+(j+.5)*d,h-.025),(.86,d-.006,.05),cedar[(si+j)%3],.004)
 box('Cream leading nosing',(0,start+.015,h-.008),(.86,.025,.018),cream,.003)
 box('Under-tread cross bearer',(0,start+.06,h-.078),(.74,.07,.056),cedar[1])
 # Flush-looking side fasteners on the continuous cheek, not raised on foot surface.
 for x in [-.399,.399]:
  for yy in [start+.07,end-.065]:
   bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.012,depth=.009,location=(x,yy,h-.085),rotation=(0,math.pi/2,0));o=bpy.context.object;o.name='Side fixing';finish(o,zinc,.001)
# Front riser panels and top rear closure give the block a solid supported read.
for start,end,h in [(-.56,-.24,.18),(-.24,.08,.36),(.08,.56,.54)]:
 box('Tread riser',(0,start+.025,h-.104),(.68,.035,.098),teal)
box('Rear closure',(0,.53,.275),(.68,.035,.43),teal)
asset=[o for o in bpy.context.scene.objects if o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in asset:o.select_set(True)
bpy.context.view_layer.objects.active=asset[0]
bpy.ops.export_scene.gltf(filepath=str(P/'wsc-plan-008-horse-mounting-block-wip.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'mounting-block-editable.blend'))
# Reimport delivered GLB into clean scene. All render pixels use exported mesh.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(P/'wsc-plan-008-horse-mounting-block-wip.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];pts=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
tri=0
for o in meshes:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
f=P/'wsc-plan-008-horse-mounting-block-wip.glb'
d={'id':'WSC-PLAN-008','status':'art-only-WIP','reimport_meshes':len(meshes),'triangles':tri,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'blender_z_up_bounds':{'min':lo,'max':hi,'size':[hi[i]-lo[i] for i in range(3)]},'tread_rises_m':[.18,.36,.54],'top_platform_depth_m':.48,'no_runtime_or_collision_validation':True}
(P/'validation.json').write_text(json.dumps(d,indent=2)+'\n')
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.world.color=(.24,.24,.24);s.view_settings.view_transform='AgX'
box('Studio ground',(0,0,-.045),(200,200,.08),mat('Studio grey',(.13,.17,.19)),0)
for name,loc,power,size in [('Key',(2,-3,4),500,3),('Fill',(-3,-1,2),250,3),('Rim',(0,3,3),400,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.25))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.8,-2.4,1.7));cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=1.85
for name,loc in [('hero',(1.8,-2.4,1.7)),('reverse',(-1.8,2.4,1.5))]:
 cam.location=loc;cam.rotation_euler=(Vector((0,0,.24))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'reimport-review.blend'))
print(json.dumps(d))

import bpy, sys, math
from mathutils import Vector
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
p=Path(args[0]); out=Path(args[1]);out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(p))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
coords=[o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
print('mesh count',len(meshes),'bounds',lo,hi,'dim',hi-lo)
h=max(hi-lo)
assert h>0
up=max(range(3),key=lambda i:(hi-lo)[i])
assert up==1, 'The extraction convention changed; inspect orientation before normalization'
if up!=2:
    print('Non-Z axis: aligning this exact TripoSR source')
center=(lo+hi)/2
f=1.97/h
for obj in meshes:
    matrix=obj.matrix_world.copy()
    for v in obj.data.vertices:
        q=(matrix @ v.co-center)*f
        if up==1:q=Vector((q.z,-q.x,-q.y))
        if up==0:q=Vector((q.y,q.z,q.x))
        q.z+=.985
        v.co=q
    obj.name='Executioner | reconstructed sculpt underlay'
    obj.parent=None
    obj.matrix_world.identity()
    for poly in obj.data.polygons:poly.use_smooth=True
    smooth=obj.modifiers.new('Despeckle','SMOOTH');smooth.factor=.65;smooth.iterations=4
    obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=smooth.name)
    mat=bpy.data.materials.new('Vertex color evaluation only');mat.use_nodes=True
    nodes=mat.node_tree.nodes
    bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.61
    if len(obj.data.color_attributes):
        tex=nodes.new('ShaderNodeVertexColor')
        tex.layer_name=obj.data.color_attributes[0].name
        gamma=nodes.new('ShaderNodeGamma');gamma.inputs['Gamma'].default_value=2.0;mat.node_tree.links.new(tex.outputs['Color'],gamma.inputs['Color']);mat.node_tree.links.new(gamma.outputs['Color'],bs.inputs['Base Color'])
    obj.data.materials.clear();obj.data.materials.append(mat)
def aim(o,point):o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,color):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,1));return o
scene=bpy.context.scene
scene.world.color=(.25,.25,.25)
area('key',(-3,-4,4),360,4,(1,.94,.89));area('opposite',(3,4,4),360,4,(1,.94,.89))
area('fill',(4,-2,1.6),160,3,(.86,.91,1));area('opposite fill',(-4,2,1.6),160,3,(.86,.91,1))
cam=bpy.data.cameras.new('Inspection');cam.type='ORTHO';cam.ortho_scale=2.20
camera=bpy.data.objects.new('Inspection',cam);scene.collection.objects.link(camera);scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=14;scene.cycles.use_denoising=False
scene.render.resolution_x=560;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
def view(deg, height=1.45):
    a=math.radians(deg)
    camera.location=(6*math.sin(a),-6*math.cos(a),height);aim(camera,(0,0,.985))
view(22)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'sculpt-underlay.blend'),compress=True)
for i,deg in enumerate((22,90,165)):
    view(deg)
    scene.render.filepath=str(out/('reconstructed-view-%s.png'%i));bpy.ops.render.render(write_still=True)

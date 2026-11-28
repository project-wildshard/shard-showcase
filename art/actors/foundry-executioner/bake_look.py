"""Evaluate one static pose with a baked PBR atlas, not a shipping character export."""
import bpy, sys, json, math
from pathlib import Path

args=sys.argv[sys.argv.index('--')+1:]
out=Path(args[0]);out.mkdir(parents=True,exist_ok=True)
frame=int(args[1]) if len(args)>1 else 1
size=int(args[2]) if len(args)>2 else 1024
assert size in {512,1024,2048}
scene=bpy.context.scene;scene.frame_set(frame)
collection=bpy.data.collections['Executioner | Editable Form']
source=[x for x in collection.objects if x.type in {'MESH','CURVE'}]
deps=bpy.context.evaluated_depsgraph_get()
for x in source:
    for m in x.modifiers:
        if m.type=='SUBSURF':m.levels=min(m.levels,1)
        if m.type=='BEVEL':m.segments=1
deps.update()
objects=[]
for src in source:
    ev=src.evaluated_get(deps)
    mesh=bpy.data.meshes.new_from_object(ev)
    if not mesh.polygons:continue
    # Make baked coordinates world-stable and avoid object transforms after join.
    mesh.transform(ev.matrix_world)
    review=bpy.data.objects.new(src.name+' | bake copy',mesh)
    scene.collection.objects.link(review);objects.append(review)
    mesh.calc_loop_triangles()
    if len(mesh.loop_triangles)>400:
        bpy.ops.object.select_all(action='DESELECT');review.select_set(True);bpy.context.view_layer.objects.active=review
        mod=review.modifiers.new('Bounded reduction for static review','DECIMATE')
        mod.ratio=.42 if any(x in src.name.lower() for x in ('hood','ceramic')) else .31
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if not review.data.materials and src.active_material:review.data.materials.append(src.active_material)
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
mesh=objects[0];mesh.name='Executioner | baked static look'
materials=[m for m in mesh.data.materials]
assert all(x and x.use_nodes for x in materials)
for o in list(collection.objects):
    o.hide_render=True
    o.hide_set(True)
bpy.context.view_layer.objects.active=mesh;mesh.select_set(True)
if not mesh.data.uv_layers:mesh.data.uv_layers.new(name='PBR atlas')
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(58),island_margin=.004)
bpy.ops.object.mode_set(mode='OBJECT')
scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.use_denoising=False
scene.render.bake.margin=4;scene.render.bake.use_clear=True;scene.render.bake.use_selected_to_active=False
def image(name,noncolor=False):
    i=bpy.data.images.new(name,width=size,height=size,alpha=False)
    if noncolor:i.colorspace_settings.name='Non-Color'
    return i
def targets(dest):
    for m in materials:
        tree=m.node_tree
        n=tree.nodes.get('WSC bake target') or tree.nodes.new('ShaderNodeTexImage')
        n.name='WSC bake target';n.image=dest;tree.nodes.active=n
def save(i):
    i.file_format='PNG';i.filepath_raw=str(out/(i.name+'.png'));i.save()
def material_surface(m):
    t=m.node_tree
    p=next(n for n in t.nodes if n.type=='BSDF_PRINCIPLED')
    output=next(n for n in t.nodes if n.type=='OUTPUT_MATERIAL')
    return t,p,output
def emission_pass(dest,kind):
    targets(dest)
    for m in materials:
        t,p,o=material_surface(m);n=t.nodes.new('ShaderNodeEmission')
        n.inputs['Strength'].default_value=1
        if kind=='base':
            c=p.inputs['Base Color']
            if c.is_linked:t.links.new(c.links[0].from_socket,n.inputs['Color'])
            else:n.inputs['Color'].default_value=c.default_value
        else:n.inputs['Color'].default_value=(1,p.inputs['Roughness'].default_value,p.inputs['Metallic'].default_value,1)
        t.links.new(n.outputs[0],o.inputs['Surface'])
    bpy.ops.object.bake(type='EMIT')
    for m in materials:
        t,p,o=material_surface(m);t.links.new(p.outputs[0],o.inputs['Surface'])
    save(dest)
base=image('executioner-base')
orm=image('executioner-orm',True)
normal=image('executioner-normal',True)
emission_pass(base,'base');emission_pass(orm,'orm')
targets(normal);bpy.ops.object.bake(type='NORMAL',normal_space='TANGENT');save(normal)
m=bpy.data.materials.new('Executioner | baked atlas');m.use_nodes=True
t=m.node_tree;p=next(n for n in t.nodes if n.type=='BSDF_PRINCIPLED')
def input_img(i):
    n=t.nodes.new('ShaderNodeTexImage');n.image=i;return n
base_n=input_img(base);orm_n=input_img(orm);norm_n=input_img(normal)
t.links.new(base_n.outputs['Color'],p.inputs['Base Color'])
sep=t.nodes.new('ShaderNodeSeparateColor');t.links.new(orm_n.outputs['Color'],sep.inputs['Color'])
t.links.new(sep.outputs['Green'],p.inputs['Roughness']);t.links.new(sep.outputs['Blue'],p.inputs['Metallic'])
nm=t.nodes.new('ShaderNodeNormalMap');t.links.new(norm_n.outputs['Color'],nm.inputs['Color']);t.links.new(nm.outputs['Normal'],p.inputs['Normal'])
mesh.data.materials.clear();mesh.data.materials.append(m)
for f in mesh.data.polygons:f.material_index=0
mesh.data.calc_loop_triangles();tri=len(mesh.data.loop_triangles)
assert 5000<tri<=46000,tri
bpy.ops.export_scene.gltf(filepath=str(out/'baked.glb'),export_format='GLB',use_selection=True,export_animations=False)
print(json.dumps({'triangles':tri,'atlas':size,'maps':['baseColor','roughnessMetallic','normal'],
                  'bytes':(out/'baked.glb').stat().st_size,'poseFrame':frame,'static':True}))

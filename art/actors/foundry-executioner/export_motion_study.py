"""Export the mantle guard diagnostic with actual skin weights, not a playable enemy."""
import bpy,json,sys
from pathlib import Path
a=sys.argv[sys.argv.index('--')+1:]
out=Path(a[0]);out.parent.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;s.frame_set(1)
c=bpy.data.collections['Executioner | Editable Form']
rig=c.objects['Executioner | pose skeleton']
assert s.get('executioner_fit')=='mantle'
assert rig.type=='ARMATURE' and rig.animation_data.action
rig.animation_data.action.name='Executioner Guard Study'
art=[o for o in c.objects if o!=rig]
weighted=[o for o in art if any(m.type=='ARMATURE' for m in o.modifiers)]
for o in weighted:
    mat=o.matrix_world.copy();o.parent=rig;o.matrix_world=mat
    assert all(abs(sum(g.weight for g in v.groups)-1)<.001 for v in o.data.vertices)
# The physical material constants survive Blender → GLB; no baked texture claims.
materials={o.active_material for o in art if o.active_material}
for m in materials:
    p=next((node for node in m.node_tree.nodes if node.type=='BSDF_PRINCIPLED'),None)
    if not p:continue
    for k in ('Base Color','Normal','Roughness','Metallic'):
        for link in list(p.inputs[k].links):m.node_tree.links.remove(link)
    p.inputs['Base Color'].default_value=m.diffuse_color
# Bake only rigid attachments' geometry. Keep weighted meshes on the original
# control cage so the glTF applies skinning in the renderer, not in Blender.
for o in art:
    if o in weighted:
        for m in list(o.modifiers):
            if m.type=='SUBSURF':o.modifiers.remove(m)
            elif m.type=='BEVEL':o.modifiers.remove(m)
        continue
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    if o.type=='CURVE':
        o.data.resolution_u=min(6,o.data.resolution_u)
        o.data.bevel_resolution=min(1,o.data.bevel_resolution)
        bpy.ops.object.convert(target='MESH')
    for m in list(o.modifiers):
        if m.type=='SUBSURF':m.levels=1
        elif m.type=='BEVEL':m.segments=1
    for m in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)
    o.data.calc_loop_triangles()
    if len(o.data.loop_triangles)>400:
        m=o.modifiers.new('Bounded review reduction','DECIMATE')
        m.ratio=.41 if any(k in o.name for k in ('Hood','Ceramic')) else .31
        bpy.ops.object.modifier_apply(modifier=m.name)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for o in art:o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,
 export_animations=True,export_animation_mode='ACTIONS',export_frame_range=True,
 export_force_sampling=True,export_def_bones=False,export_rest_position_armature=True)
print(json.dumps({'rigBones':len(rig.data.bones),'weightedMeshes':len(weighted),'bytes':out.stat().st_size,
 'sourceClip':rig.animation_data.action.name,'frames':[1,25],'playable':False}))

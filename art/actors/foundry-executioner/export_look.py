"""Export a static pose for Three.js visual review; never a gameplay character."""
import bpy, json, math, sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
out=Path(args[0]);out.parent.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
scene.frame_set(int(args[1]) if len(args)>1 else 1)
model=bpy.data.collections['Executioner | Editable Form']
deps=bpy.context.evaluated_depsgraph_get()
# Base color survives the review independently of proprietary environments and post effects.
# Low octave value noise is mirrored from the Blender material reference, not a skinning replacement.
COLORS=[
 ('wool',(.012,.015,.016),(.046,.046,.037)),
 ('steel',(.047,.053,.057),(.15,.17,.17)),
 ('ceramic',(.32,.23,.15),(.69,.60,.46)),
 ('leather apron',(.043,.017,.008),(.18,.081,.036)),
 ('cured',(.024,.011,.006),(.105,.060,.039)),
 ('copper',(.090,.033,.017),(.25,.105,.046)),
 ('hammered edges',(.130,.130,.115),(.29,.28,.24)),
]
def tone(v):
    x,y,z=v
    return .5+(.18*math.sin(x*51+y*19+z*9)+.13*math.sin(x*123-y*39+z*48)
                +.09*math.sin(x*266+y*193+z*121)+.05*math.sin(x*71+y*55-z*80))
mats={}
def flat(name):
    if name in mats:return mats[name]
    m=bpy.data.materials.new('Review PBR | '+name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(1,1,1,1)
    bs.inputs['Metallic'].default_value=.70 if any(k in name for k in ('steel','copper','hammered')) else .04
    bs.inputs['Roughness'].default_value=.46 if 'steel' in name else .65
    src=m.node_tree.nodes.new('ShaderNodeVertexColor');src.layer_name='reviewColor'
    m.node_tree.links.new(src.outputs['Color'],bs.inputs['Base Color'])
    mats[name]=m;return m
samples=[o for o in model.objects if o.type in ('MESH','CURVE')]
for o in samples:
    for m in o.modifiers:
        if m.type=='SUBSURF':m.levels=min(m.levels,1)
        if m.type=='BEVEL':m.segments=min(m.segments,1)
deps.update()
count=0;objs=[]
for src in samples:
    ob=src.evaluated_get(deps)
    me=bpy.data.meshes.new_from_object(ob)
    if not me.polygons:continue
    mat=ob.matrix_world.copy()
    review=bpy.data.objects.new(src.name+' | static sample',me);scene.collection.objects.link(review)
    review.matrix_world=mat
    me.calc_loop_triangles()
    if len(me.loop_triangles)>400:
        bpy.ops.object.select_all(action='DESELECT');review.select_set(True);bpy.context.view_layer.objects.active=review
        mod=review.modifiers.new('Static inspection triangle cap','DECIMATE')
        kind=src.name.lower()
        mod.ratio=.19 if kind.startswith('shoulder mantle') else .42 if any(t in kind for t in ('hood','ceramic')) else .31
        bpy.ops.object.modifier_apply(modifier=mod.name)
        me=review.data
    coords=[mat @ v.co for v in me.vertices]
    me.materials.clear()
    name=src.active_material.name.lower()
    me.materials.append(flat(name))
    _,low,high=next((a for a in COLORS if a[0] in name),('neutral',(.03,.032,.032),(.08,.084,.084)))
    col=me.color_attributes.new(name='reviewColor',type='BYTE_COLOR',domain='POINT')
    for i,v in enumerate(me.vertices):
        p=coords[i]; f=tone(p)
        col.data[i].color=(*(lo+f*(hi-lo) for lo,hi in zip(low,high)),1)
    for face in me.polygons:face.material_index=0
    me.calc_loop_triangles();count+=len(me.loop_triangles)
    objs.append(review)
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_animations=False,
                          export_materials='EXPORT',export_vertex_color='MATERIAL')
assert 5000<count<=46000,count
print(json.dumps({'tris':count,'meshes':len(objs),'poseFrame':scene.frame_current,'bytes':out.stat().st_size,'isRuntimeRig':False}))

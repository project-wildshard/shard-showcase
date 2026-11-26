"""Compact pair of side trestles for the existing oak apron, no duplicate apron."""
import sys
from pathlib import Path
import bpy

out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
def mat(name,rgb,metal):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value=(*rgb,1)
    n.inputs['Metallic'].default_value=metal
    n.inputs['Roughness'].default_value=.59
    return m
wood=mat('Dark stained oak',(.27,.113,.037),.08)
iron=mat('Oxidised graphite feet',(.085,.121,.119),.62)
ochre=mat('Muted brass hardware',(.46,.27,.075),.58)

def box(name,loc,dims,material,bevel):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=dims;o.data.materials.append(material)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    b=o.modifiers.new('Eased edges','BEVEL');b.width=bevel;b.segments=1
    bpy.ops.object.modifier_apply(modifier=b.name)
    return o
parts=[]
for tag,sign in [('Left',-1),('Right',1)]:
    x=1.935*sign
    obs=[
        box('Skid',(x,0,.065),(.265,.46,.13),iron,.02),
        box('Oak stand',(x,0,.511),(.143,.15,.882),wood,.014),
        box('Wrap saddle',(x,0,.91),(.19,.176,.105),iron,.012),
        box('Keeper pin',(x,-.087,.896),(.096,.012,.038),ochre,.006)]
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs:o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join()
    ob=bpy.context.object;ob.name='RidingBrushStand_'+tag;parts.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'w10b-riding-apron-stands.glb'),export_format='GLB',
    use_selection=True,export_animations=False)

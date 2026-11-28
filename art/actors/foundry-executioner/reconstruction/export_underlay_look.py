"""Export the local comparison underlay; not the fitted asset or a runtime mesh."""
from pathlib import Path
import bpy
import sys
out=Path(sys.argv[sys.argv.index('--')+1])
assert out.suffix=='.glb'
out.parent.mkdir(parents=True,exist_ok=True)
o=bpy.data.objects['Executioner | reconstructed sculpt underlay']
bpy.ops.object.select_all(action='DESELECT')
o.select_set(True)
bpy.context.view_layer.objects.active=o
m=o.active_material
nodes=m.node_tree.nodes
shader=nodes.get('Principled BSDF')
c=next(n for n in nodes if n.type=='VERTEX_COLOR')
m.node_tree.links.new(c.outputs['Color'],shader.inputs['Base Color'])
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,
                          export_animations=False,export_vertex_color='MATERIAL')

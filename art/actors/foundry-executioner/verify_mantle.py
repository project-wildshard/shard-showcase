"""Measure the sleeve contact of the two new deforming mantle panels."""
import bpy, json
from mathutils.bvhtree import BVHTree
c=bpy.data.collections['Executioner | Editable Form']
scene=bpy.context.scene
assert scene.get('executioner_fit')=='mantle'
sleeve=c.objects['Continuous sleeve L']
panels=[c.objects['Shoulder mantle | asymmetric '+n] for n in ('fireproof cloth','front lap')]
assert all({g.name for g in o.vertex_groups}=={'chest','upper_arm.L'} for o in panels)
def bvh(d,obj):
    ob=obj.evaluated_get(d);me=ob.to_mesh()
    poly=[tuple(p.vertices) for p in me.polygons]
    tree=BVHTree.FromPolygons([ob.matrix_world @ v.co for v in me.vertices],poly,all_triangles=False)
    ob.to_mesh_clear();return tree,len(poly)
results=[]
for i in range(scene.frame_start,scene.frame_end+1):
    scene.frame_set(i)
    d=bpy.context.evaluated_depsgraph_get()
    base,_=bvh(d,sleeve)
    overlaps={}
    for obj in panels:
        tree,n=bvh(d,obj)
        q=tree.overlap(base)
        overlaps[obj.name]={'overlapPairs':len(q),'contactFaces':len({f for f,_ in q}),'faces':n}
    results.append({'frame':i,'panels':overlaps})
print(json.dumps({'fit':'mantle','test':'evaluated left sleeve versus each mantle panel',
 'motionScope':'integer-frame samples of the loaded diagnostic action, not combat', 'frames':results},indent=2))

"""Verify the saved pre-rig mesh's continuous limb topology."""
import bpy, bmesh, json
c=bpy.data.collections['Executioner | Editable Form']
deps=bpy.context.evaluated_depsgraph_get()
objects=[o for o in c.objects if o.type in {'MESH','CURVE'}]
bounds=[]
for obj in objects:
    o=obj.evaluated_get(deps)
    mesh=o.to_mesh()
    bounds.extend(o.matrix_world @ v.co for v in mesh.vertices)
    o.to_mesh_clear()
height=max(x.z for x in bounds)-min(x.z for x in bounds)
assert 1.91<height<2.10,height
result={'stage':'pre-rig silhouette construction', 'heightM':round(height,4),'objects':len(objects),'continuousGarments':{}}
for limb in ('Continuous sleeve','Continuous trousers'):
    for side in 'LR':
        name=f'{limb} {side}'
        b=bmesh.new();b.from_mesh(c.objects[name].data)
        assert b.faces and all(e.is_manifold for e in b.edges),name
        b.verts.ensure_lookup_table();todo=[b.verts[0]];seen=set()
        while todo:
            v=todo.pop()
            if v in seen:continue
            seen.add(v)
            todo.extend(e.other_vert(v) for e in v.link_edges if e.other_vert(v) not in seen)
        assert len(seen)==len(b.verts),name
        result['continuousGarments'][name]={'vertices':len(b.verts),'faces':len(b.faces),'closedConnectedMesh':True}
        b.free()
assert c.objects.get('Ceramic face | upper brow') and c.objects.get('Ceramic face | lower jaw')
result['assetState']='no rig or game export'
print(json.dumps(result,indent=2))

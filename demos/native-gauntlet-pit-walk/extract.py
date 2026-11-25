"""Extract structural triangles from the exact C2 GLB, in authored world metres."""
import bpy, hashlib, json, sys
from pathlib import Path

src, out = map(Path, sys.argv[sys.argv.index("--")+1:])
assert hashlib.sha256(src.read_bytes()).hexdigest() == "90cff3a5ab2706987585417d898fe8fe0b42823f9be01c9dd34196cb9f8dfbd5"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=str(src))
deps = bpy.context.evaluated_depsgraph_get()
parts = []
for obj in sorted(bpy.context.scene.objects, key=lambda x: x.name):
    if obj.type != "MESH":
        continue
    if not obj.name.startswith(("01 ", "03 ", "04 ", "05 ", "06 ", "07 ", "08 ", "10 ", "11 ", "C2_Lift")):
        continue
    evaluated = obj.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        index, vertices, triangles = {}, [], []
        for tri in mesh.loop_triangles:
            material = mesh.materials[tri.material_index].name
            if material.startswith(("Pale stamped chevrons", "Ceramic lamp face")):
                continue
            for i in tri.vertices:
                if i not in index:
                    x, y, z = evaluated.matrix_world @ mesh.vertices[i].co
                    index[i] = len(vertices)//3
                    vertices.extend(round(v, 7) for v in (x+55, z, 212-y))
                triangles.append(index[i])
        if triangles:
            parts.append(dict(name=obj.name, vertices=vertices, triangles=triangles))
    finally:
        evaluated.to_mesh_clear()
assert all(any(p["name"].startswith(n) for p in parts)
           for n in ("01 ", "03 ", "10 ", "11 ", "C2_Lift"))
out.write_text(json.dumps(parts, separators=(",", ":"))+"\n")
print([(p["name"], len(p["triangles"])//3) for p in parts])

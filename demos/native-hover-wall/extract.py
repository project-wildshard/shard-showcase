"""Extract the east launch wall from the original D7 scene."""
import hashlib
import json
from pathlib import Path
import sys
import bpy

out = Path(sys.argv[sys.argv.index("--") + 1])
scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()
parts = []
for obj in sorted(scene.objects, key=lambda o: o.name):
    if obj.type != "MESH" or not obj.name.startswith(
        ("HOVER | launch wall east ",)
    ):
        continue
    evaluated = obj.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    try:
        vertices = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        mesh.calc_loop_triangles()
        positions = [
            round(n, 7) for v in vertices for n in (v.x, v.z, -v.y)
        ]
        triangles = [i for t in mesh.loop_triangles for i in t.vertices]
        parts.append(dict(name=obj.name, vertices=positions, triangles=triangles))
    finally:
        evaluated.to_mesh_clear()
assert len(parts) == 1, [p["name"] for p in parts]
raw = json.dumps(parts, separators=(",", ":")) + "\n"
out.write_text(raw)
print(len(parts), sum(len(p["triangles"]) // 3 for p in parts),
      hashlib.sha256(raw.encode()).hexdigest())

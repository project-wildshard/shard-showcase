"""Extract exact W08 mesh triangles in the connection from pole 2 to the roof."""
import hashlib
import json
from pathlib import Path
import sys
import bpy

assert "--" in sys.argv, "Pass an output path after --"
out = Path(sys.argv[sys.argv.index("--") + 1])
scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()
parts = []
for obj in sorted(scene.objects, key=lambda o: o.name):
    if obj.type != "MESH":
        continue
    evaluated = obj.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    try:
        vertices = [tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices]
        if not vertices:
            continue
        lo = tuple(min(v[i] for v in vertices) for i in range(3))
        hi = tuple(max(v[i] for v in vertices) for i in range(3))
        if any(hi[i] < a or lo[i] > b for i, (a, b) in enumerate([
                (-225, -175), (73, 122), (-1, 25)])):
            continue
        mesh.calc_loop_triangles()
        index, positions, triangles = {}, [], []
        for tri in mesh.loop_triangles:
            pts = [vertices[i] for i in tri.vertices]
            if any(max(v[k] for v in pts) < a or min(v[k] for v in pts) > b
                   for k, (a, b) in enumerate([(-225, -175), (73, 122), (-1, 25)])):
                continue
            for i in tri.vertices:
                if i not in index:
                    x, y, z = vertices[i]
                    index[i] = len(positions) // 3
                    positions.extend([round(x, 7), round(z, 7), round(-y, 7)])
                triangles.append(index[i])
        if triangles:
            parts.append(dict(name=obj.name, vertices=positions, triangles=triangles))
    finally:
        evaluated.to_mesh_clear()
assert any(p["name"] == "JUNCTION | continuous landable roof" for p in parts)
assert any(p["name"].startswith("JUNCTION | roof rail") for p in parts)
raw = json.dumps(parts, separators=(",", ":")) + "\n"
out.write_text(raw)
print(len(parts), sum(len(p["triangles"]) // 3 for p in parts),
      hashlib.sha256(raw.encode()).hexdigest())

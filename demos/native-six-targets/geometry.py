"""Reimport the six pinned fixtures and extract exact yard geometry."""
import hashlib
import json
from pathlib import Path
import math
import sys
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

assert "--" in sys.argv, "Pass an output path after --"
out = Path(sys.argv[sys.argv.index("--") + 1])
scene = bpy.context.scene
ROOT = Path(__file__).resolve().parents[2]
assets = ROOT/"public/assets/wildshard-art"
design=json.loads((ROOT/"project/layouts/w3a-w3d-melee-targets.json").read_text())
donors=dict(parry="w3d-padded-parry-stand.glb",spear="w3a-spear-ring.glb")
V=Vector

def tree(objects):
    verts, polys = [], []
    for obj in objects:
        if obj.type!="MESH":
            continue
        off=len(verts)
        verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        polys.extend(tuple(off+i for i in f.vertices) for f in obj.data.polygons)
    return BVHTree.FromPolygons(verts,polys)

ground=tree([o for o in scene.objects if o.name.startswith("RANGE LAND | ")])
fixtures=[]
for k,key in enumerate(donors):
    file=assets/donors[key]
    assert hashlib.sha256(file.read_bytes()).hexdigest()==design["assets"][key]["sha256"]
    coords=design[("sword" if key=="parry" else "spear")+"_row_world_xz"]
    for j,(x,z) in enumerate(coords):
        hit=ground.ray_cast(V((x,-z,.52)),V((0,0,-1)),1.52)[0]
        assert hit is not None and -.1<hit.z<.25, (x,z,hit)
        y=hit.z
        before=set(scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(file))
        new=set(scene.objects)-before
        roots=[o for o in new if o.parent not in new]
        assert len(roots)==1
        root=roots[0]
        root.name=f"Six Targets | {'blade' if k==0 else 'ring'} {j+1}"
        root.matrix_world=Matrix.Translation((x,-z,y)) @ Matrix.Rotation(math.pi,4,"Z") @ root.matrix_world
        bpy.context.view_layer.update()
        # A straight native-thrust viewport should see through the actual
        # ring center, but +0.54 m intersects the bronze rim (negative control).
        if k==1:
            solid=tree(new)
            assert solid.ray_cast(V((x,-z+2,y+2)), V((0,-1,0)),2.2)[0] is None
            assert solid.ray_cast(V((x+.54,-z+2,y+2)), V((0,-1,0)),2.2)[0] is not None
        fixtures.append({"id":f"{'sword' if k==0 else 'spear'}-{j+1}",
          "anchor":[x,round(y,6),z],"at":[x,round(y+(1.56 if k==0 else 2),6),z-(.235 if k==0 else .2)]})
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
                (-34.2, -13.8), (-109, -76), (-1, 3.3)])):
            continue
        mesh.calc_loop_triangles()
        index, positions, triangles = {}, [], []
        for tri in mesh.loop_triangles:
            pts = [vertices[i] for i in tri.vertices]
            if any(max(v[k] for v in pts) < a or min(v[k] for v in pts) > b
                   for k, (a, b) in enumerate([(-34.2, -13.8), (-109, -76), (-1, 3.3)])):
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
assert any(p["name"].startswith("RANGE LAND | green footprint") for p in parts)
assert len(fixtures)==6
raw = json.dumps(dict(fixtures=fixtures,parts=parts), separators=(",", ":")) + "\n"
out.write_text(raw)
print(len(parts), sum(len(p["triangles"]) // 3 for p in parts),
      hashlib.sha256(raw.encode()).hexdigest())

if len(sys.argv[sys.argv.index("--")+1:])==2:
    render=Path(__file__).with_name("render.py")
    exec(compile(render.read_text(),str(render),"exec"))

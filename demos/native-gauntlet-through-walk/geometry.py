"""Reimport the three exact public Gauntlet assets at their Round 5 placements."""
import bpy, hashlib, json
from pathlib import Path
from mathutils import Matrix

ASSETS = (
    ("forecourt", (80, 0, 132), "496698e86f76e0bc5c9834eb0fc648bf1edeea4fc15d5eee85264c238edfa41a"),
    ("c1-loading-yard", (55, 0, 163), "77cdcd7033f3c03a8fcf1c8e38b024adfca2470f53cd4af76b5b901a90431394"),
    ("c2-pit", (55, 0, 212), "90cff3a5ab2706987585417d898fe8fe0b42823f9be01c9dd34196cb9f8dfbd5"),
)

def load(directory):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    record={}
    for label,(x,y,z),sha in ASSETS:
        src=directory/f"wsc-scene-007-{label}.glb"
        assert hashlib.sha256(src.read_bytes()).hexdigest()==sha, src
        before=set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(src))
        new=set(bpy.context.scene.objects)-before
        for obj in new:
            if obj.parent not in new:
                obj.location.x+=x-55; obj.location.y+=184-z; obj.location.z+=y
        record[label]=sorted((o for o in new if o.type=="MESH"),key=lambda o:o.name)
    # C1 stages fifteen copies of the separately tracked crate, rather than
    # baking them into the architecture export. Repeat that source recipe.
    crate=directory/"haul-crate.glb"
    assert hashlib.sha256(crate.read_bytes()).hexdigest()=="d7a5f8fcb2b835d0c0c77c3051ebd950ed449dc2c563e10779fdc5f01cc6bb44"
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(crate))
    bpy.context.view_layer.update()
    imported=set(bpy.context.scene.objects)-before
    files=[(o.data,o.matrix_world.copy()) for o in sorted(imported,key=lambda o:o.name) if o.type=="MESH"]
    vv=[m@v.co for data,m in files for v in data.vertices]
    lo=[min(v[i] for v in vv) for i in range(3)]; hi=[max(v[i] for v in vv) for i in range(3)]
    pivot=Matrix.Translation((-(lo[0]+hi[0])/2,-(lo[1]+hi[1])/2,-lo[2]))
    scale=Matrix.Diagonal(tuple(w/(b-a) for w,a,b in zip((1.28,1.40,1.2),lo,hi))+(1,))
    for o in imported: bpy.data.objects.remove(o,do_unlink=True)
    for x,z in ((55,160),(55,177),(24,178)):
        for k,(dx,h) in enumerate(((-1.4,0),(0,0),(1.4,0),(-1.4,1.2),(1.4,1.2))):
            for i,(mesh,base) in enumerate(files):
                o=bpy.data.objects.new(f"C1 cargo {x}/{z} crate {k}/{i}",mesh)
                bpy.context.scene.collection.objects.link(o)
                o.matrix_world=Matrix.Translation((x+dx-55,184-z,h+.013))@scale@pivot@base
                record["c1-loading-yard"].append(o)
    bpy.context.view_layer.update()
    return record

F=("Forecourt datum","C1 grade and edge strips","C1 north portal","SE dividing wall","Portal approach paver","Titan north portal","Titan shortcut start","Checkpoint frame","Run board case","Run board posts")
C1=("Floor datum","Entry terrace datum","North descent ramps","North terrace wall","West retaining run","East retaining run","South wall around G1","G1 grade","G1 side parapet","G1 transit header","Marshalling half walls","Six-meter service pier","D1 recessed dock","D2 recessed dock")
C2=("01 ","03 ","04 ","05 ","06 ","07 ","08 ","10 ","11 ","C2_Lift")
RAMPS=("C1 grade and edge strips","North descent ramps","G1 grade")

def export(directory,out):
    record=load(directory)
    deps=bpy.context.evaluated_depsgraph_get()
    parts=[]; profiles={label:[] for label in ("c1-loading-yard","c2-pit")}
    for label,objects in record.items():
        for obj in objects:
            # Authored imported crate objects are recognized below by parent/name.
            prefix=dict(forecourt=F, **{"c1-loading-yard":C1, "c2-pit":C2})[label]
            is_cargo=label=="c1-loading-yard" and any("crate" in n.lower() for n in (obj.name,obj.parent.name if obj.parent else ""))
            if not obj.name.startswith(prefix) and not is_cargo:
                continue
            evaluated=obj.evaluated_get(deps); mesh=evaluated.to_mesh()
            try:
                mesh.calc_loop_triangles()
                pts=[]
                for v in mesh.vertices:
                    x,y,z=evaluated.matrix_world@v.co
                    pts.append(tuple(round(f,7) for f in (x+55,z,184-y)))
                keep=[]; vertices=[]; index={}
                for tri in mesh.loop_triangles:
                    mat=mesh.materials[tri.material_index].name
                    if obj.name.startswith(RAMPS) and not mat.startswith(("Sand-dusted concrete","Warm forecourt concrete")):
                        continue
                    if mat.startswith(("Pale stamped chevrons","Ceramic lamp face","Warm ceramic lens")):
                        continue
                    p=[pts[i] for i in tri.vertices]
                    c2g1=label=="c2-pit" and obj.name.startswith("03 ") and min(z for x,y,z in p)<189.99 and max(z for x,y,z in p)<=190.001
                    c1g1=label=="c1-loading-yard" and obj.name.startswith("G1 grade")
                    if c1g1 or c2g1:
                        if set((round(y,4),round(z,4)) for x,y,z in p)=={(0,184),(2.5,190)}:
                            profiles[label].append(sorted(p))
                    if c2g1:
                        continue
                    for i in tri.vertices:
                        if i not in index:
                            index[i]=len(vertices)//3; vertices.extend(pts[i])
                        keep.append(index[i])
                if keep: parts.append(dict(asset=label,name=obj.name,vertices=vertices,triangles=keep))
            finally:
                evaluated.to_mesh_clear()
    # Both art copies have precisely the same planar top corners and span;
    # their interior triangulation need not use the same diagonal.
    expected={(25,0,184),(35,0,184),(25,2.5,190),(35,2.5,190)}
    for v in profiles.values():
        assert len(v)==2 and set(p for tri in v for p in tri)==expected,profiles
    out.write_text(json.dumps(parts,separators=(",",":"))+"\n")
    print(json.dumps({label:[(p["name"],len(p["triangles"])//3) for p in parts if p["asset"]==label] for label in record}))

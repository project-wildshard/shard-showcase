"""Optional far mesh for WSC-MODULE-024; preserve finish boundaries and mounting origin."""
import hashlib,json,math,sys
from pathlib import Path
import bmesh,bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/"showcase-studies"))
from common import clear_scene,export,output_directory
out=output_directory()
src=D.parents[2]/"public/assets/wildshard-art/wsc-module-024-floodlight-tower.glb"
pin="316a77c8fdabebbbc2767fe035b7a24caa749773cffe98f2dcf99791d7ec16b2"
assert hashlib.sha256(src.read_bytes()).hexdigest()==pin
clear_scene()
S=bpy.context.scene
def load(p):
    before=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.view_layer.update()
    return sorted(set(S.objects)-before,key=lambda o:o.name)
old,=load(src);assert old.type=="MESH"
ob=bpy.data.objects.new("Floodlight tower | far",old.data.copy())
S.collection.objects.link(ob);ob.matrix_world=old.matrix_world.copy()
# The original stores every split hard normal separately in glTF. Weld only
# coincident positions, never neighbouring light emitters or nearby struts.
bm=bmesh.new();bm.from_mesh(ob.data)
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-6)
bm.to_mesh(ob.data);bm.free()
bpy.ops.object.select_all(action="DESELECT")
ob.select_set(True);bpy.context.view_layer.objects.active=ob
md=ob.modifiers.new("Collapse flat bevel interiors","DECIMATE")
md.decimate_type="DISSOLVE";md.angle_limit=math.radians(12);md.delimit={"MATERIAL"}
bpy.ops.object.modifier_apply(modifier=md.name)
md=ob.modifiers.new("Far screen-space detail budget","DECIMATE")
md.decimate_type="COLLAPSE";md.ratio=.31
bpy.ops.object.modifier_apply(modifier=md.name)
md=ob.modifiers.new("Stable triangles for reimport","TRIANGULATE")
bpy.ops.object.modifier_apply(modifier=md.name)
# Far silhouette is all broad planes; avoid imported per-vertex custom-normal
# remnants surviving the surface simplification. This is a visual-only mesh.
for p in ob.data.polygons:p.use_smooth=False
file=out/"wsc-module-024-floodlight-tower-far.glb"
export([ob],file)
bpy.data.objects.remove(ob,do_unlink=True)
new,=load(file)
def metrics(o):
    m=o.data
    verts=[o.matrix_world@p.co for p in m.vertices]
    polys=[p.vertices[:] for p in m.polygons]
    band=[p for t in m.polygons if m.materials[t.material_index].name.startswith(("Pearl ceramic reflector","Warm amber lens core")) for i in t.vertices for p in [verts[i]]]
    bounds=lambda a:[[min(v[i] for v in a) for i in range(3)],[max(v[i] for v in a) for i in range(3)]]
    m.calc_loop_triangles()
    return BVHTree.FromPolygons(verts,polys),bounds(verts),bounds(band),len(m.loop_triangles),[q.name.removesuffix(".001") for q in m.materials]
a,ab,al,at,am=metrics(old);b,bb,bl,bt,bm=metrics(new)
assert am==bm and len(bm)==8
assert min(v[2] for v in (ab[0],bb[0]))>=-1e-6
assert max(abs(i-j) for o,p in zip(ab,bb) for i,j in zip(o,p))<=.005
assert max(abs(i-j) for o,p in zip(al,bl) for i,j in zip(o,p))<=.001
views=[]
for angle in range(0,360,30):
    rad=math.radians(angle)
    n=Vector((math.sin(rad),-math.cos(rad),-.085)).normalized()
    right=Vector((-n.y,n.x,0)).normalized();up=n.cross(right).normalized()
    union=inside=0
    for j in range(200):
        for i in range(132):
            p=Vector((0,0,4.45))+n*42+right*((i+.5)/132-.5)*3.32+up*((j+.5)/200-.5)*9.7
            va=a.ray_cast(p,-n,60)[0] is not None
            vb=b.ray_cast(p,-n,60)[0] is not None
            union+=va or vb;inside+=va and vb
    views.append([angle,inside/union])
assert min(v for _,v in views)>=.973,views
assert bt<at*.31 and file.stat().st_size<src.stat().st_size*.58,(at,bt,file.stat().st_size)
proof={"scope":"Optional static far visual. No installation, automatic LOD, light or collision changes.",
       "original":{"sha256":pin,"bytes":src.stat().st_size,"triangles":at,"bounds_xyz":ab,"lens_bounds_xyz":al},
       "far":{"sha256":hashlib.sha256(file.read_bytes()).hexdigest(),"bytes":file.stat().st_size,"triangles":bt,"bounds_xyz":bb,"lens_bounds_xyz":bl},
       "materials":bm,"silhouette_132x200":views}
(out/"floodlight-far-proof.json").write_text(json.dumps(proof,indent=2)+"\n")
print(json.dumps(proof))

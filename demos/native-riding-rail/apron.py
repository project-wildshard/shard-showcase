"""Optional solid rail apron, retaining the existing W10b striped rail."""
import bpy
import json
from math import pi, sin, cos
from mathutils import Matrix, Vector
from pathlib import Path
import sys

out=Path(sys.argv[sys.argv.index("--")+1])
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
S=bpy.context.scene
materials=[]
for name,rgb,metal in (
    ("Weathered oak | heart",(.21,.102,.046),0),("Oak | uneven warm stain",(.31,.155,.07),0),
    ("Oak | darker plank",(.267,.123,.051),0),("Teal steel | end straps",(.05,.242,.221),.38),
    ("Oxidized cap heads",(.115,.145,.144),.68),("Cream stencil | lozenge",(.64,.56,.34),0)):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    n=m.node_tree.nodes.get("Principled BSDF")
    n.inputs["Base Color"].default_value=(*rgb,1)
    n.inputs["Metallic"].default_value=metal
    n.inputs["Roughness"].default_value=.67
    materials.append(m)
V=[]; F=[]; M=[]
def add(v,f,m):
    n=len(V);V.extend(v);F.extend(tuple(i+n for i in a) for a in f);M.extend([m]*len(f))
def box(x0,x1,y0,y1,z0,z1,m):
    add([(x,y,z) for z in (z0,z1) for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1))],
        [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)

# GlTF uses the same pivot as the old rail; the near W10b placement adds 25 mm.
# The longest spans delineate, but do not exceed, the compact test collider.
box(-2.047,2.047,-.048,.048,.331,1.013,0)
for i in range(9):
    a=-2.014+i*4.028/9
    b=a+4.028/9-.012
    for section in (-1,1):
        y0,y1=(-.060,-.048) if section<0 else (.048,.060)
        box(a,b,y0,y1,.344,1.000,1 if i%3 else 2)
for s in (-1,1):
    for j in (-1,1):
        a,b=sorted([s*1.88,s*2.036])
        y0,y1=(-.060,-.052) if j<0 else (.052,.060)
        box(a,b,y0,y1,.335,1.009,3)
        for z in (.395,.554,.784,.948):
            x=s*1.96
            r=.012
            # Half-pin disks on each side; tiny, without protruding beyond the bounds.
            vs=[(x+r*cos(i*pi/6),j*.061,z+r*sin(i*pi/6)) for i in range(12)]
            add(vs,[tuple(range(12))[::-j]],4)
for j in (-1,1):
    for x in (-.38,0,.38):
        # Contrasting sight marks are painted, not collision geometry.
        y=j*.0605
        vs=[(x-.12,y,.696),(x,y,.796),(x+.12,y,.696),(x,y,.596)]
        add(vs,[(0,1,2,3)[::j]],5)

mesh=bpy.data.meshes.new("W10b rail apron")
mesh.from_pydata(V,[],F);mesh.update()
ob=bpy.data.objects.new("W10b optional oak apron",mesh);S.collection.objects.link(ob)
for m in materials:mesh.materials.append(m)
for p,i in zip(mesh.polygons,M):p.material_index=i
ob.select_set(True)
bpy.context.view_layer.objects.active=ob
file=out/"w10b-riding-rail-apron.glb"
bpy.ops.export_scene.gltf(filepath=str(file),export_format="GLB",use_selection=True,export_animations=False)
bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(file))
bpy.context.view_layer.update()
o,=(x for x in S.objects if x.type=="MESH")
world=Matrix.Translation((-125,148,.025))@Matrix.Rotation(pi/2,4,"Z")
pts=[world@o.matrix_world@v.co for v in o.data.vertices]
vs=[(x,z,-y) for x,y,z in pts]
mins,maxs=list(map(min,zip(*vs))),list(map(max,zip(*vs)))
center=[round((a+b)/2,6) for a,b in zip(mins,maxs)]
extents=[round((b-a)/2,6) for a,b in zip(mins,maxs)]
assert center==[-125,.697,-148] and max(abs(a-b) for a,b in zip(extents,(.061,.341,2.047)))<.00001,(center,extents)
assert mins[1]>.35 and maxs[1]<1.052
o.data.calc_loop_triangles()
(out/"apron.json").write_text(json.dumps({"worldCenter":center,"worldHalfExtent":extents,
    "apronBytes":file.stat().st_size,"apronTriangles":len(o.data.loop_triangles)},separators=(",",":"))+"\n")

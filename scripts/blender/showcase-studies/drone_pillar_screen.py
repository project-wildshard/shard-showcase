"""E03 suspended industrial screen in the archived Round 5 cover envelope."""
import hashlib
import json
from math import cos, pi, sin
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene

args=sys.argv[sys.argv.index("--")+1:]
assert len(args) in (1,2)
out=Path(args[0])
out.mkdir(parents=True,exist_ok=True)
clear_scene()
scene=bpy.context.scene
parts=[]

def mat(name,color,metallic=0,rough=.55):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metallic
    p.inputs["Roughness"].default_value=rough
    return m

iron=mat("Warm graphite steel",(.066,.093,.112),.68,.43)
zinc=mat("Rain-brushed zinc joint collars",(.25,.28,.289),.71,.37)
base=mat("Weathered deep basalt",(.156,.146,.123),.04,.78)
paint=mat("Old amber powder coat",(.642,.25,.052),.37,.36)
canvas=mat("Saffron dyed duck cloth",(.43,.147,.033),0,.94)
dark=mat("Slate-blue waxed canvas",(.074,.112,.136),0,.88)
seam=mat("Worn orange seam binding",(.52,.227,.071),0,.73)
brass=mat("Oxidised hardware",(.49,.30,.108),.65,.38)

def box(name,loc,dim,m,bevel=.022):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.name=name
    o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new("Catch light", "BEVEL")
        b.width=min(bevel,min(dim)*.27)
        b.segments=1
        o.modifiers.new("Weighted planes","WEIGHTED_NORMAL")
    parts.append(o)
    return o

def cyl(name,loc,r,h,m,n=12,axis="Z"):
    rot=(pi/2,0,0) if axis=="Y" else (0,pi/2,0) if axis=="X" else (0,0,0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=h,location=loc,rotation=rot)
    o=bpy.context.object
    o.name=name
    o.data.materials.append(m)
    parts.append(o)
    return o

for x in (-4,4):
    box("Basalt plinth",(x,0,.16),(1.6,1.6,.32),base,.07)
    box("Bolted seat",(x,0,.38),(1.26,1.26,.2),zinc,.044)
    cyl("Tapered rhythm | rolled service column",(x,0,3.57),.55,6.26,iron)
    for z,r,h,m in [(1.18,.64,.20,zinc),(2.17,.66,.22,zinc),(6.06,.63,.19,zinc),
                    (6.51,.69,.23,paint),(6.79,.70,.22,zinc),(6.96,.615,.08,iron)]:
        cyl("Axial steel collar",(x,0,z),r,h,m)
    for dx,dy in [(-.49,-.49),(-.49,.49),(.49,-.49),(.49,.49)]:
        cyl("Plinth socket bolt",(x+dx,dy,.511),.056,.06,brass,8)
box("Closed dorsal box girder",(0,0,6.63),(8.06,.60,.42),paint,.052)
box("Zinc lower beam edge",(0,0,6.423),(7.7,.69,.046),zinc,.012)
for x in (-3.28,3.28):
    box("Post to beam cleat",(x,0,6.49),(.34,.74,.50),iron,.028)
    for z in (6.35,6.635):
        for y in (-.379,.379):
            cyl("Dark cleat fastener",(x,y,z),.053,.038,brass,8,"Y")

# Closed, two-sided fabric; composition comes from E03, dimensions from R5.
# The cloth is the only thing reaching the bottom hem between the posts.
verts,faces,slots=[],[],[]
cols,rows=32,18
for back in (0,1):
    for j in range(rows+1):
        v=j/rows
        for i in range(cols+1):
            u=i/cols
            ripple=(.039*sin(2*pi*(2*u+.34*v))+.018*sin(2*pi*(5*u-.43*v)))*sin(pi*u)
            yy=ripple*(.45+.55*sin(pi*v))+(-.011 if back==0 else .011)
            zz=2.2+4*v + (.055*sin(pi*u) - .045*sin(2*pi*u)**2)*sin(pi*v)
            verts.append((-3.8+7.6*u,yy,zz))
plane=(cols+1)*(rows+1)
def face(f,slot):
    faces.append(f)
    slots.append(slot)
for j in range(rows):
    for i in range(cols):
        a=j*(cols+1)+i
        f=(a,a+1,a+cols+2,a+cols+1)
        tone=2 if (i in (0,cols-1) or j in (0,rows-1)) else (0 if j>=8 else 1)
        face(f,tone)
        face(tuple(t+plane for t in reversed(f)),tone)
row=lambda j:[j*(cols+1)+i for i in range(cols+1)]
edges=row(0)[:-1]+[j*(cols+1)+cols for j in range(rows)]+row(rows)[:0:-1]+[j*(cols+1) for j in range(rows,0,-1)]
for a,b in zip(edges,edges[1:]+edges[:1]):
    face((a,b,b+plane,a+plane),2)
mesh=bpy.data.meshes.new("Drafted canvas with woven hem")
mesh.from_pydata(verts,[],faces)
for m in (canvas,dark,seam):
    mesh.materials.append(m)
for p,k in zip(mesh.polygons,slots):
    p.material_index=k
    p.use_smooth=True
o=bpy.data.objects.new("Canvas | ochre upper and charcoal skirt",mesh)
scene.collection.objects.link(o)
parts.append(o)
for x in (-3.27,-2.21,-1.11,0,1.11,2.21,3.27):
    cyl("Capped suspension pin",(x,0,6.303),.046,.259,brass,8)
    cyl("Cushioned binding ring",(x,0,6.139),.076,.055,zinc,10,"Y")
for x in (-3.755,3.755):
    for z in (2.31,3.56,4.83,6.04):
        cyl("Side eyelet",(x,0,z),.058,.12,brass,8,"Y")

# Keep editable named pieces in the recipe; batch their evaluated corner
# normals and material slots into one mesh, one draw primitive per material.
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
verts,faces,channels,normals=[],[],[],[]
mats=[iron,zinc,base,paint,canvas,dark,seam,brass]
slotsByName={m.name:i for i,m in enumerate(mats)}
for part in parts:
    q=part.evaluated_get(deps)
    m=q.to_mesh()
    try:
        first=len(verts)
        normal_matrix=q.matrix_world.to_3x3().inverted_safe().transposed()
        verts.extend(tuple(q.matrix_world@v.co) for v in m.vertices)
        for f in m.polygons:
            faces.append(tuple(first+j for j in f.vertices))
            channels.append(slotsByName[m.materials[f.material_index].name])
            normals.extend(tuple((normal_matrix@m.corner_normals[i].vector).normalized()) for i in f.loop_indices)
    finally:
        q.to_mesh_clear()
for o in parts:
    bpy.data.objects.remove(o,do_unlink=True)
mesh=bpy.data.meshes.new("Pillar screen | batched draw primitives")
mesh.from_pydata(verts,[],faces)
for m in mats:
    mesh.materials.append(m)
for f,k in zip(mesh.polygons,channels):
    f.material_index=k
    f.use_smooth=True
mesh.normals_split_custom_set(normals)
root=bpy.data.objects.new("E03 · Ground-centred canopy screen",mesh)
scene.collection.objects.link(root)
parts=[root]

bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
dest=out/"e3-suspended-pillar-screen.glb"
bpy.ops.export_scene.gltf(filepath=str(dest),export_format="GLB",use_selection=True,
                         export_animations=False,export_apply=True,export_texcoords=False)
glb=dest.read_bytes()
assert struct.unpack_from("<4sII",glb)==(b"glTF",2,len(glb))
tree=json.loads(glb[20:20+struct.unpack_from("<I",glb,12)[0]])
count=sum(tree["accessors"][p["indices"]]["count"]//3 for m in tree["meshes"] for p in m["primitives"])
assert len(glb)<240000 and count<5500 and not tree.get("images")
assert len(tree["meshes"])==1 and len(tree["meshes"][0]["primitives"])==8
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(dest))
bpy.context.view_layer.update()
fresh=sorted(scene.objects,key=lambda o:o.name)
points,polys=[],[]
for o in fresh:
    start=len(points)
    points.extend(o.matrix_world@v.co for v in o.data.vertices)
    polys.extend(tuple(start+i for i in p.vertices) for p in o.data.polygons)
lo=[min(p[i] for p in points) for i in range(3)]
hi=[max(p[i] for p in points) for i in range(3)]
assert all(abs(a-b)<1e-4 for a,b in zip(lo,[-4.8,-.8,0]))
assert all(abs(a-b)<1e-4 for a,b in zip(hi,[4.8,.8,7]))
bvh=BVHTree.FromPolygons(points,polys,all_triangles=True)
def casts(level):
    return sum(bvh.ray_cast(Vector((i*.2,sign*4,level)),Vector((0,-sign,0)),8)[0] is not None
                 for sign in (-1,1) for i in range(-16,17))
bands=[.85,1.7,2.1,3,4,5,7.2]
hits=[casts(y) for y in bands]
assert hits==[0,0,0,66,66,66,0],hits
for x in (-4,4):
    for z in (.10,1.7,3,5,6.94):
        assert bvh.ray_cast(Vector((x,-4,z)),Vector((0,1,0)),8)[0] is not None
(out/"pillar-blender.json").write_text(json.dumps(dict(
    boundsBlender=[lo,hi],raysBothFaces={"yM":bands,"hits":hits,"perHeight":66},
    bytes=len(glb),triangles=count,drawPrimitives=8,sha256=hashlib.sha256(glb).hexdigest()),indent=2)+"\n")
if len(args)==1:
    raise SystemExit(0)

# Studio crop; no additional screen geometry is exported.
floor=mat("Studio warm roadway",(.19,.174,.147),.03,.86)
concrete=mat("Floor stripe ochre",(.37,.21,.09),.02,.87)
box("Studio slab only",(0,0,-.125),(160,160,.25),floor,.0)
for x in (-5.5,5.5):
    box("Studio path paint",(x,0,.001),(.11,35,.002),concrete,0)
for x in (-5.5,5.5):
    box("Studio author height tick",(x,.4,1.05),(.052,.052,2.1),zinc,.01)
scene.render.engine="CYCLES"
scene.cycles.samples=34
scene.cycles.adaptive_threshold=.035
scene.cycles.use_denoising=False
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG"
scene.render.image_settings.quality=94
scene.view_settings.view_transform="AgX"
scene.world=bpy.data.worlds.new("Warm East coast sky")
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs[0].default_value=(.37,.46,.57,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=.48
def light3(kind,pos,target,power,color,size):
    bpy.ops.object.light_add(type=kind,location=pos)
    o=bpy.context.object
    o.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat("-Z","Y").to_euler()
    o.data.energy=power
    o.data.color=color
    if kind=="SUN": o.data.angle=size
    else: o.data.shape="DISK";o.data.size=size
light3("SUN",(-7,-6,12),(0,0,1.7),2.6,(1,.82,.65),.11)
light3("AREA",(1,5,8),(-2,0,2.3),1050,(.53,.78,1),8)
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
def view(name,eye,to,lens,w,h):
    cam.location=eye
    cam.rotation_euler=(Vector(to)-Vector(eye)).to_track_quat("-Z","Y").to_euler()
    cam.data.lens=lens
    scene.render.resolution_x=w
    scene.render.resolution_y=h
    scene.render.filepath=str(out/(name+".jpg"))
    bpy.ops.render.render(write_still=True)
view("nov25-e3-pillar-screen",(-8,-16,5.6),(0,0,3.55),42,1300,890)
view("nov25-e3-pillar-gap",(2,-10,1.7),(-.15,0,3.3),36,780,1040)

"""Author the W7a opening landing perch, check the reimport, and render its fit."""
from collections import Counter
import bpy
import hashlib
import json
from pathlib import Path
import sys
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
assert len(args) in (1, 2), "Pass OUTPUT [native replay JSON for renders]"
out = Path(args[0])
out.mkdir(parents=True, exist_ok=True)
center = Vector((-151., 46.62, 0.))  # Three -151, 0, -46.62; +Y faces away from start.
objects = []
def material(name, color, metallic=.15, rough=.48, emit=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    p.inputs["Emission Color"].default_value = (*color, 1)
    p.inputs["Emission Strength"].default_value = emit
    return m
steel = material("Perch • heat treated gunmetal", (.069, .107, .125), .52)
deckmat = material("Perch • graphite nonslip plate", (.116, .15, .153), .31, .66)
oxide = material("Perch • saffron powder coat", (.67, .22, .037), .31, .38)
concrete = material("Perch • sandstone aggregate", (.38, .32, .22), .02, .83)
light = material("Perch • desaturated cyan reflectors", (.052, .58, .63), .24, .29, .16)
bolts = material("Perch • blackened fasteners", (.105, .15, .166), .65, .27)

def box(name, loc, dim, mat, bevel=.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = "W7a landing | " + name
    obj.dimensions = dim
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        edge = obj.modifiers.new("Formed edges", "BEVEL")
        edge.width = bevel
        edge.segments = 2
        obj.modifiers.new("Weighted planes", "WEIGHTED_NORMAL")
    objects.append(obj)
    return obj

def beam(name, a, b, width, depth, mat):
    a, b = Vector(a), Vector(b)
    obj = box(name, (a+b)/2, (width, depth, (b-a).length), mat, .013)
    obj.rotation_euler = (b-a).to_track_quat("Z","Y").to_euler()

# A single deck mesh, with genuinely inset materials instead of two
# coincident surfaces. Its outside dimensions are the stock test box.
edges_x = [-1.70,-1.47,-.765,-.575,-.095,.095,.575,.765,1.47,1.70]
edges_y = [-1.12,-1.003,-.948,1.12]
verts, faces, slots, indices = [], [], [], {}
def quad(points, slot):
    for point in points:
        if point not in indices:
            indices[point] = len(verts)
            verts.append(point)
    faces.append(tuple(indices[p] for p in points))
    slots.append(slot)
for ix,(a,b) in enumerate(zip(edges_x,edges_x[1:])):
    for iy,(c,d) in enumerate(zip(edges_y,edges_y[1:])):
        slot = 1 if ix in (0,8) else 2 if iy == 1 and ix in (2,4,6) else 0
        quad([(a,c,4.4),(b,c,4.4),(b,d,4.4),(a,d,4.4)],slot)
        quad([(a,d,4.16),(b,d,4.16),(b,c,4.16),(a,c,4.16)],0)
rim = ([(x,edges_y[0]) for x in edges_x[:-1]] +
       [(edges_x[-1],y) for y in edges_y[:-1]] +
       [(x,edges_y[-1]) for x in edges_x[:0:-1]] +
       [(edges_x[0],y) for y in edges_y[:0:-1]])
for (a,b),(c,d) in zip(rim,rim[1:]+rim[:1]):
    quad([(a,b,4.16),(c,d,4.16),(c,d,4.4),(a,b,4.4)],0)
seams = Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]))
assert all(count == 2 for count in seams.values())
mesh = bpy.data.meshes.new("Perch deck with integrated treads")
mesh.from_pydata(verts,[],faces)
for m in (deckmat,oxide,concrete):
    mesh.materials.append(m)
for f,slot in zip(mesh.polygons,slots):
    f.material_index = slot
obj = bpy.data.objects.new("W7a landing | deck (exact collision volume)",mesh)
bpy.context.collection.objects.link(obj)
objects.append(obj)
for x in (-1.57,1.57):
    box("flat front reflector", (x,-1.115,4.28), (.193,.008,.063), light, .002)
for x in (-1.29,1.29):
    for y in (-.52,.75):
        box("pier footing", (x,y,.115), (.69,.58,.23), concrete, .033)
        box("column root catch plate", (x,y,.243), (.42,.37,.056), bolts, .012)
        box("folded load column", (x,y,2.23), (.25,.24,3.98), steel, .023)
        box("painted impact sleeve", (x,y,.56), (.299,.288,.61), oxide, .027)
    beam("side web rising", (x,-.51,.7), (x,.75,3.97), .125,.12,steel)
    beam("side web descending", (x,.75,.7), (x,-.51,3.97), .125,.12,steel)
    box("underdeck channel", (x,.03,4.05), (.29,2.02,.25), steel, .019)
    box("cyan lip lozenge", (x,-1.119,4.29), (.27,.012,.061), light, .004)
for y in (-.68,.81):
    box("transverse beam", (0,y,4.05), (3.25,.25,.26), oxide, .023)
# Deliberately no raised rail or dressing in the audited landing envelope.
anchor_donor = set(bpy.context.scene.objects)-set(objects)
glb = out/"w7a-pole-one-perch.glb"
bpy.ops.object.select_all(action="DESELECT")
for obj in objects:
    obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True,
                         export_animations=False,export_apply=True)
for o in objects:
    bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
bpy.context.view_layer.update()
fresh = sorted(set(bpy.context.scene.objects)-anchor_donor,key=lambda o:o.name)
assert all(o.type == 'MESH' for o in fresh)
tris = sum(len(o.data.polygons) for o in fresh)
points = [o.matrix_world @ v.co for o in fresh for v in o.data.vertices]
lo = [min(v[i] for v in points) for i in range(3)]
hi = [max(v[i] for v in points) for i in range(3)]
assert abs(lo[2])<1e-6 and max(abs(a-b) for a,b in zip(hi,[1.7,1.12,4.4]))<1e-5
assert abs(lo[1]+1.125)<.006
# Any accessory above the box top would invalidate the simple deck collision.
assert max(v.z for v in points)<4.40001
dressing = []
for o in fresh:
    if "exact collision volume" in o.name:
        pts = [o.matrix_world @ v.co for v in o.data.vertices]
        bounds = [[f(v[i] for v in pts) for i in range(3)] for f in (min,max)]
        for a,b in zip(bounds,[[-1.7,-1.12,4.16],[1.7,1.12,4.4]]):
            assert all(abs(q-r)<1e-5 for q,r in zip(a,b))
        continue
    # The near-faces and support legs participate in the motor fit.
    verts = [center+o.matrix_world@v.co for v in o.data.vertices]
    o.data.calc_loop_triangles()
    dressing.append(dict(name=o.name, vertices=[round(k,6) for v in verts for k in (v.x,v.z,-v.y)],
                         triangles=[i for t in o.data.loop_triangles for i in t.vertices]))
raw = json.dumps(dressing,separators=(",",":"))+"\n"
(out/"perch-dressing.json").write_text(raw)
collision_sha = hashlib.sha256(raw.encode()).hexdigest()
info = dict(asset=glb.name,sha256=hashlib.sha256(glb.read_bytes()).hexdigest(), bytes=glb.stat().st_size,
            triangles=tris,local_bounds=[lo,hi],dressing_sha256=collision_sha,
            center_three=[-151,0,-46.62],deck_size_three=[3.4,.24,2.24],deck_top_y=4.4)
(out/"perch-export.json").write_text(json.dumps(info,indent=2)+"\n")
if len(args)==1:
    raise SystemExit(0)

review = json.loads(Path(args[1]).read_text())
assert review["dressingSha"] == collision_sha
for o in fresh:
    o.matrix_world = Matrix.Translation(center) @ o.matrix_world
def xyz(p):
    return Vector((p[0],-p[2],p[1]))
def dot(p, radius, mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=radius,location=p)
    bpy.context.object.data.materials.append(mat)
accent = material("Review only • measured cyan motion",(.055,.72,.83),.04,.29,.75)
amber = material("Review only • arrival eye",(.83,.265,.062),.08,.32,.30)
frames = review["frames"]
for _,feet,phase,_ in frames[::6]:
    if phase=='zip' and (xyz(feet)-xyz(review['centre']['start'])).length>4:
        dot(xyz(feet)+Vector((0,0,.51)),.103,accent)
dot(xyz(review["centre"]["end"])+Vector((0,0,.35)),.19,amber)

scene = bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=28
scene.cycles.adaptive_threshold=.055
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG'
scene.render.image_settings.quality=92
scene.view_settings.view_transform='AgX'
scene.world=bpy.data.worlds.new("Grapple • warm morning")
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get("Background")
bg.inputs[0].default_value=(.39,.52,.68,1)
bg.inputs[1].default_value=.48
bpy.ops.object.light_add(type='SUN',location=(-152,31,19))
sun=bpy.context.object
sun.rotation_euler=Vector((-.45,.56,-.7)).to_track_quat('-Z','Y').to_euler()
sun.data.energy=2.45
sun.data.angle=.1
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
def view(name,loc,to,lens,width,height):
    cam.location=loc
    cam.rotation_euler=(Vector(to)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens
    scene.render.resolution_x=width
    scene.render.resolution_y=height
    scene.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)
view('nov25-w7a-perch-start',xyz(review['centre']['start'])+Vector((0,0,1.7)),
     (-150,44,6.1),32,660,874)
view('nov25-w7a-perch-arrival',(-143.7,52.0,6.55),(-150.75,46.35,3.15),35,900,720)

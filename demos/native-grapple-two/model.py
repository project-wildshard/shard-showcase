"""Rebuild and reimport the second W7a landing tower. Load a fresh W08 donor."""
import bpy
import hashlib
import json
from pathlib import Path
import sys
from mathutils import Vector, Matrix

args=sys.argv[sys.argv.index("--")+1:]
assert len(args) in (1,2)
out=Path(args[0])
out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
center=Vector((-172,70.2,0))
top,width,depth=8.2,3.4,2.6

def mat(name,rgb,metal=.20,rough=.55,emission=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    n=m.node_tree.nodes.get("Principled BSDF")
    n.inputs["Base Color"].default_value=(*rgb,1)
    n.inputs["Metallic"].default_value=metal
    n.inputs["Roughness"].default_value=rough
    n.inputs["Emission Color"].default_value=(*rgb,1)
    n.inputs["Emission Strength"].default_value=emission
    return m
M=[mat("Blackened structural steel",(.052,.082,.092),.56),
   mat("Saffron enamel",(.63,.22,.038),.36),
   mat("Graphite nonslip plate",(.128,.15,.154),.32,.67),
   mat("Cut sandstone aggregate",(.32,.275,.211),.08,.81),
   mat("Turquoise reflectors",(.038,.52,.56),.22,.38,.21)]
verts,faces,slots=[],[],[]
cube=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
def cuboid(loc,d,slot,rot=None):
    i=len(verts)
    q=Vector(loc)
    for z in (-1,1):
        for y in (-1,1):
            for x in (-1,1):
                v=Vector((x*d[0]/2,y*d[1]/2,z*d[2]/2))
                verts.append(tuple(q+(rot@v if rot is not None else v)))
    for f in cube:
        faces.append(tuple(i+k for k in f))
        slots.append(slot)
def strut(a,b,w,d,i=0):
    a,b=Vector(a),Vector(b)
    v=b-a
    cuboid((a+b)/2,(w,d,v.length),i,v.to_track_quat("Z","Y"))
def finish(name,mats):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    for m in mats: mesh.materials.append(m)
    for face,slot in zip(mesh.polygons,slots):face.material_index=slot
    o=bpy.data.objects.new(name,mesh)
    scene.collection.objects.link(o)
    verts.clear(); faces.clear(); slots.clear()
    return o

# Exactly one box used as the floor collider; detail stays below its top.
cuboid((0,0,top-.12),(width,depth,.24),0)
deck=finish("Pole 2 exact floor deck",[M[2]])
for x in (-1.30,1.30):
    for y in (-.91,.91):
        cuboid((x,y,.155),(.72,.61,.31),3)
        cuboid((x,y,.337),(.47,.43,.054),0)
        cuboid((x,y,4.12),(.238,.21,7.56),0)
        for z in (.66,3.98,7.69):
            cuboid((x,y,z),(.32,.30,.40),1)
            for dx in (-.105,.105):
                cuboid((x+dx,y-.156,z),(.048,.018,.048),0)
    for z in (4.05,7.87):
        cuboid((x,0,z),(.27,2.27,.22),0)
    for z0,z1 in ((.74,3.83),(4.20,7.63)):
        strut((x,-.86,z0),(x,.86,z1),.14,.13)
        strut((x,.86,z0),(x,-.86,z1),.14,.13)
for y in (-.91,.91):
    for z in (4.05,7.87):
        cuboid((0,y,z),(2.63,.235,.21),1)
    strut((-1.30,y,.52),(1.30,y,3.94),.13,.135)
    strut((1.30,y,4.19),(-1.30,y,7.67),.13,.135)
for x in (-1.62,1.62):
    cuboid((x,0,7.998),(.115,2.47,.15),1)
for y in (-1.295,1.295):
    for x in (-1.29,0,1.29):
        cuboid((x,y,8.066),(.34,.035,.07),4)
    for x in (-.8,.8):
        cuboid((x,y,8.01),(.38,.035,.115),1)
tower=finish("Pole 2 landing tower frame",M)
before=set(scene.objects)-{deck,tower}
bpy.ops.object.select_all(action="DESELECT")
for o in (deck,tower):o.select_set(True)
glb=out/"w7a-pole-two-tower.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True,export_animations=False)
for o in (deck,tower):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
bpy.context.view_layer.update()
dressing=[]
fresh=sorted(set(scene.objects)-before,key=lambda o:o.name)
assert len(fresh)==2
triangles=0
for o in fresh:
    vertices=[o.matrix_world@v.co for v in o.data.vertices]
    o.data.calc_loop_triangles()
    triangles+=len(o.data.loop_triangles)
    if "exact floor deck" in o.name:
        extents=[[f(v[k] for v in vertices) for k in range(3)] for f in (min,max)]
        for dims,b in zip(extents,[(-1.7,-1.3,7.96),(1.7,1.3,8.2)]):
            assert all(abs(x-y)<1e-5 for x,y in zip(dims,b))
        continue
    assert max(v.z for v in vertices)<top
    dressing.append({"name":o.name,"vertices":[round(k,6) for v in vertices for k in
                      (v.x+center.x,v.z,-v.y-center.y)],
                     "triangles":[i for t in o.data.loop_triangles for i in t.vertices]})
raw=json.dumps(dressing,separators=(",",":"))+"\n"
(out/"pole-two-dressing.json").write_text(raw)
(out/"pole-two-export.json").write_text(json.dumps({
    "bytes":glb.stat().st_size,"triangles":triangles,"sha256":hashlib.sha256(glb.read_bytes()).hexdigest(),
    "dressing_sha256":hashlib.sha256(raw.encode()).hexdigest(),"origin_three":[-172,0,-70.2],
    "deck_size_three":[width,.24,depth],"deck_top_y":top
},indent=2)+"\n")
if len(args)==1:
    raise SystemExit(0)

motion=json.loads(Path(args[1]).read_text())
assert motion["secondDressingSha"]==hashlib.sha256(raw.encode()).hexdigest()
for o in fresh:o.matrix_world=Matrix.Translation(center)@o.matrix_world
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(out/"w7a-pole-one-perch.glb"))
for o in set(scene.objects)-before:o.matrix_world=Matrix.Translation((-151,46.62,0))@o.matrix_world

def xyz(p):return Vector((p[0],-p[2],p[1]))
def ribbon(name,points,m):
    cv=bpy.data.curves.new(name,'CURVE'); cv.dimensions='3D'; cv.bevel_depth=.044; cv.bevel_resolution=2
    spl=cv.splines.new('POLY');spl.points.add(len(points)-1)
    for q,v in zip(spl.points,points):q.co=(*v,1)
    o=bpy.data.objects.new(name,cv);scene.collection.objects.link(o);cv.materials.append(m)
def ball(name,pos,m,r=.20):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=r,location=pos)
    o=bpy.context.object;o.name=name;o.data.materials.append(m)

paths=[mat("Proof | cyan first hop",(.055,.70,1),.0,.5,2),mat("Proof | amber second hop",(1,.44,.059),.0,.5,2)]
for i,hop in enumerate(motion["centre"]):
    pts=[xyz(hop["start"])]+[xyz(f[1]) for f in hop["frames"][::3]]+[xyz(hop["end"])]
    ribbon(f"Proof overlay | hop {i+1}",[v+Vector((0,0,.21)) for v in pts],paths[i])
    ball("Proof | touched down",pts[-1]+Vector((0,0,.24)),paths[i])
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
world=bpy.data.worlds.new("Soft west blue")
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.25,.38,.55,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.42
scene.world=world
l=bpy.data.lights.new("Afternoon","SUN");l.energy=2.15;l.angle=.16
o=bpy.data.objects.new("Afternoon",l);scene.collection.objects.link(o);o.rotation_euler=(.61,-.44,-.72)
cam=bpy.data.cameras.new("Route view")
o=bpy.data.objects.new("Route view",cam);scene.collection.objects.link(o);scene.camera=o
cam.clip_end=800
scene.render.engine="CYCLES";scene.cycles.samples=24;scene.cycles.use_denoising=False
scene.view_settings.view_transform='AgX'
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='WEBP';scene.render.image_settings.quality=89
for name,pos,target,lens,size in (
    ("route",(-185,14,32),(-158,46,6),48,(1440,940)),
    ("second",(-156,51,13),(-171.3,69.3,8.8),51,(1140,950)),
):
    o.location=pos;aim(o,target);cam.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(out/f"nov26-w7a-two-{name}.webp")
    bpy.ops.render.render(write_still=True)

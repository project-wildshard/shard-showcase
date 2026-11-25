"""Render two labeled route colors on the exact C2 art; no changes to the GLB."""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector

src, proof, out = map(Path, sys.argv[sys.argv.index("--")+1:])
data = json.loads(proof.read_text())
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=str(src))
scene=bpy.context.scene
def point(feet):
    x,y,z=feet
    return (x-55,212-z,y+.29)
def marks(feet,name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Emission Color"].default_value=(*color,1)
    bs.inputs["Emission Strength"].default_value=.8
    verts,faces=[],[]
    radius=.23
    for x,y,z in map(point,feet):
        i=len(verts)
        verts.extend(((x-radius,y,z),(x,y+radius,z),(x+radius,y,z),(x,y-radius,z),(x,y,z+.11)))
        faces.extend(tuple(i+k for k in f) for f in ((0,4,1),(1,4,2),(2,4,3),(3,4,0),(0,1,2,3)))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);o.data.materials.append(m)
# Paths converge in G2; draw the common exit segment once.
for i,name,color in [(1,"West ramp capsule samples",(.07,.80,.60)),(5,"East ramp capsule samples",(.24,.58,1.))]:
    rows=data["samples"][i]["frames"][::3]
    if i==5: rows=[r for r in rows if r["feet"][0]<87]
    marks([r["feet"] for r in rows],name,color)
scene.world=bpy.data.worlds.new("Court skylight");scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs[0].default_value=(.34,.48,.64,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=.57
bpy.ops.object.light_add(type="SUN",location=(-23,18,34))
sun=bpy.context.object
sun.rotation_euler=Vector((.36,-.34,-.84)).to_track_quat("-Z","Y").to_euler()
sun.data.energy=2.4;sun.data.angle=.125;sun.data.color=(1,.86,.68)
scene.render.engine="CYCLES";scene.cycles.samples=20;scene.cycles.use_denoising=False
scene.cycles.adaptive_threshold=.073;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="WEBP";scene.render.image_settings.quality=94
scene.view_settings.view_transform="AgX"
bpy.ops.object.camera_add()
c=bpy.context.object;scene.camera=c
def render(name,eye,target,lens,w,h,ortho=0):
    c.location=eye;c.rotation_euler=(Vector(target)-c.location).to_track_quat("-Z","Y").to_euler()
    c.data.type="ORTHO" if ortho else "PERSP"
    if ortho: c.data.ortho_scale=ortho
    c.data.lens=lens;scene.render.resolution_x=w;scene.render.resolution_y=h
    scene.render.filepath=str(out/(name+".webp"))
    bpy.ops.render.render(write_still=True)
render("nov25-e11c-pit-walk-overview",(37,-46,96),(1,-3,0),28,1360,900,118)
render("nov25-e11c-pit-walk-ramps",(-19,18,7.7),(1,3,1.6),24,1190,760)

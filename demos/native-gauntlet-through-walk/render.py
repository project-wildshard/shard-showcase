"""Render the real assembled court assets with capsule traces overlaid."""
import bmesh, bpy, json, sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from geometry import load

src,source,out=map(Path,sys.argv[sys.argv.index("--")+1:])
record=load(src)
proof=json.loads(source.read_text())
scene=bpy.context.scene
# Suppress only the coincident C2 G1 copy on this review stage, so the copper
# edge paint of the retained C1 ramp stays legible. No source asset is edited.
for obj in record["c2-pit"]:
    if not obj.name.startswith("03 "):continue
    bm=bmesh.new();bm.from_mesh(obj.data)
    def is_g1(f):
        z=[184-(obj.matrix_world@v.co).y for v in f.verts]
        return min(z)<189.99 and max(z)<=190.001
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if is_g1(f)],context="FACES")
    bm.to_mesh(obj.data);bm.free()
def marks(frames,name,color):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    bs=mat.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Emission Color"].default_value=(*color,1)
    bs.inputs["Emission Strength"].default_value=1.05
    verts,faces=[],[]
    for row in frames:
        x,z,y=row["feet"][0]-55,184-row["feet"][2],row["feet"][1]+.22
        k=len(verts)
        verts+= [(x-.271,z,y),(x,z+.271,y),(x+.271,z,y),(x,z-.271,y),(x,z,y+.14)]
        faces+= [tuple(k+j for j in ids) for ids in ((0,4,1),(1,4,2),(2,4,3),(3,4,0),(0,1,2,3))]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);scene.collection.objects.link(ob);ob.data.materials.append(mat)
west=proof["samples"][1]["frames"][::3]
east=proof["samples"][5]["frames"][::3]
# Avoid doubled dots where both routes practically overlap (the entry and G2).
marks(west,"West measured capsule path",(.09,.85,.64))
marks([r for r in east if r["feet"][2]>145.95 and r["feet"][0]<90],"East measured capsule path",(.30,.56,1.0))
scene.world=bpy.data.worlds.new("Gauntlet skylight")
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes["Background"]
bg.inputs[0].default_value=(.34,.46,.67,1);bg.inputs[1].default_value=.63
bpy.ops.object.light_add(type="SUN",location=(-39,31,51))
sun=bpy.context.object
sun.rotation_euler=Vector((.46,-.49,-.8)).to_track_quat("-Z","Y").to_euler()
sun.data.color=(1,.83,.65);sun.data.energy=2.55;sun.data.angle=.15
scene.render.engine="CYCLES";scene.cycles.samples=24;scene.cycles.use_denoising=False
scene.cycles.adaptive_threshold=.075;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="WEBP";scene.render.image_settings.quality=94
scene.view_settings.view_transform="AgX"
bpy.ops.object.camera_add()
cam=bpy.context.object;scene.camera=cam
def shot(n,pos,target,w,h,ortho=None,lens=30):
    cam.location=pos
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.type="ORTHO" if ortho else "PERSP"
    if ortho:cam.data.ortho_scale=ortho
    else:cam.data.lens=lens
    scene.render.resolution_x=w;scene.render.resolution_y=h
    scene.render.filepath=str(out/f"nov25-e11c-through-{n}.webp")
    bpy.ops.render.render(write_still=True)
shot("overview",(94,-59,144),(14,6,0),1450,1120,165)
shot("g1",(-31,18,10),(-18,-6,1.5),1220,800,None,27)

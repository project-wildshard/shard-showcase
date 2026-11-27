"""E12g phase-three cargo block: one static asset, checked in the existing Titan bowl."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[3]
args = sys.argv[sys.argv.index("--")+1:]
out = Path(args[0])
out.mkdir(parents=True, exist_ok=True)
assets = root / "public/assets/wildshard-art"
arena = assets / "wsc-scene-008-titan-bowl.glb"
pin = "cd4b20016133bab16940d85f0b3319aecd19708626a5fe9cdb35f68f83a92021"
assert hashlib.sha256(arena.read_bytes()).hexdigest() == pin
layout = json.loads((root / "project/layouts/wsc-scene-008-titan-bowl.json").read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, c, metal, rough, glow=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*c,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    for k,v in (("Base Color",(*c,1)),("Metallic",metal),("Roughness",rough),
                ("Emission Color",(*c,1)),("Emission Strength",glow)):
        bs.inputs[k].default_value=v
    return m

iron=mat("Ablated petrol iron",(.045,.10,.13),.72,.52)
oxide=mat("Oxide freight panels",(.34,.122,.043),.48,.64)
rust=mat("Darker oxide freight panels",(.18,.071,.04),.40,.72)
steel=mat("Rubbed steel faces",(.20,.26,.30),.8,.41)
shadow=mat("Inboard seal",(.023,.035,.040),.22,.84)
light=mat("Honey ceramic insets",(.95,.35,.06),.22,.46,.7)
buckets={}
def box(name,m,dim,pos,bevel=0,a=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object
    o.name=name
    o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.rotation_euler.y=a
    o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new("Beaten corners","BEVEL")
        b.width=bevel
        b.segments=1
        o.modifiers.new("Weighted panel normals","WEIGHTED_NORMAL")
        bpy.ops.object.convert(target="MESH")
    buckets.setdefault(m.name,[]).append(o)

# +X is the axle, +Y is direction of travel, pivot on the roll axis.
box("Dark inner chassis",shadow,(7.78,3.82,3.04),(0,0,0),.19)
# Two broad rails on each long side; four bearing-cage corners along X.
for s in (-1,1):
    for h in (-1,1):
        box("Long folded corner beam",iron,(8,.31,.29),(0,s*1.845,h*1.455),.055)
    box("Outer cage cheek",iron,(.28,3.92,3.20),(s*3.86,0,0),.22)
    box("Recessed hub block",steel,(.07,1.54,1.50),(s*3.965,0,0),.21)
    box("Inset hub",shadow,(.033,.94,.88),(s*3.9835,0,0),.15)
    box("Cooling core",light,(.03,.31,.31),(s*3.985,0,0),.045)
for i,x in enumerate((-2.72,-.91,.91,2.72)):
    for s in (-1,1):
        face=oxide if (i+int(s>0))%2 else rust
        box("Oil-aged load door",face,(1.70,.21,2.46),(x,s*1.88,0),.09)
        box("Door recess",shadow,(1.20,.052,.95),(x,s*1.97,.13),0)
        for j in (-1,0,1):
            box("Rolled reinforcing rib",steel,(.25,.050,.86),(x+j*.37,s*1.974,.13),0,
                math.radians((7 if i%2 else -7)))
        box("Lower wear rail",iron,(1.48,.070,.24),(x,s*1.960,-1.03),0)
        if i in (0,3):
            box("Inset end beacon",light,(.30,.036,.11),(x,s*1.979,.93),.027)
        box("Widthwise skids, both roll faces",iron,(.29,3.69,.27),(x,0,s*1.465),.07)
        for j in (-1,1):
            box("Wear insert",steel,(.22,.59,.09),(x,j*1.20,s*1.55),0)

reduced=[]
for name, obs in sorted(buckets.items()):
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    bpy.ops.object.join()
    ob=bpy.context.object
    ob.name=name
    bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    reduced.append(ob)
bpy.ops.object.select_all(action="DESELECT")
for ob in reduced: ob.select_set(True)
p=out/"e12g-overflow-cargo-block.glb"
bpy.ops.export_scene.gltf(filepath=str(p),export_format="GLB",use_selection=True,export_animations=False)
raw=p.read_bytes()
doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
prim=[item for m in doc["meshes"] for item in m["primitives"]]
tris=sum(doc["accessors"][item["indices"]]["count"]//3 for item in prim)
assert len(prim)==6 and tris<=2800 and len(raw)<180000
assert not any(k in doc for k in ("textures","images","animations","skins"))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(p))
scene=bpy.context.scene
cargo=list(scene.objects)
pts=[ob.matrix_world @ v.co for ob in cargo if ob.type=="MESH" for v in ob.data.vertices]
lo=[min(v[i] for v in pts) for i in range(3)]
hi=[max(v[i] for v in pts) for i in range(3)]
assert max(abs(a-b) for a,b in zip([*lo,*hi],[-4,-2,-1.6,4,2,1.6]))<1e-5,(lo,hi)

bpy.ops.import_scene.gltf(filepath=str(arena))
bowl=[ob for ob in scene.objects if ob.type=="MESH" and ob not in cargo]
def mesh_tree(obs):
    points, polygons=[],[]
    for ob in obs:
        k=len(points)
        points.extend(ob.matrix_world@v.co for v in ob.data.vertices)
        polygons.extend(tuple(k+i for i in f.vertices) for f in ob.data.polygons)
    return BVHTree.FromPolygons(points,polygons)
floor=mesh_tree([o for o in bowl if o.name.startswith(("01 ","02 ","03 "))])
cover=[o for o in bowl if o.name.startswith("07 ")]
assert floor and cover and len({o.name.split(" | ")[0].split(".")[0] for o in cover})>=4

# Continuous conservative envelope: axle does not steer within each proposed
# path. A full revolution cannot outrun a circle circumscribed about Y/Z.
sweep_radius=math.hypot(2,1.6)
r0,r1=14,44
corridor=4.
outer_radius=math.hypot(r1+sweep_radius,corridor)
assert outer_radius<layout["floor_radius"]-4
tests=[]
for heading in layout["lane_headings_degrees_east_toward_south"]:
    a=math.radians(heading)
    f=Vector((math.cos(a),-math.sin(a),0))
    x=Vector((-f.y,f.x,0))
    # Check exact cover vertices against their lane-aligned bounding boxes.
    gaps=[]
    for ob in cover:
        vertices=[ob.matrix_world @ v.co for v in ob.data.vertices]
        xs=[x.dot(v) for v in vertices]
        ys=[f.dot(v) for v in vertices]
        gaps.append(max(min(xs)-corridor,-corridor-max(xs),
                        min(ys)-(r1+sweep_radius),r0-sweep_radius-max(ys)))
    assert min(gaps)>5,(heading,min(gaps))
    samples=[]
    for i in range(77):
        for j in range(17):
            xy=f*(r0-sweep_radius+(r1-r0+2*sweep_radius)*i/76)+x*(-4+j*.5)
            hit,normal,*_=floor.ray_cast(xy+Vector((0,0,5)),Vector((0,0,-1)),5.1)
            assert hit is not None and abs(normal.z)>.9999
            samples.append(hit.z)
    assert min(samples)>-.00001 and max(samples)<.106
    tests.append(dict(heading_deg=heading,projected_cover_gap_m=round(min(gaps),4),
                      floor_samples=len(samples),max_sampled_surface_relief_m=round(max(samples),4)))

(out/"e12g-overflow-cargo-block-proof.json").write_text(json.dumps(dict(
    scope="Art and placement envelope only. No authored move, collider, attack, telegraph, timing or encounters.",
    catalogue_id="WSC-SCENE-008",arena_sha256=pin,
    bytes=len(raw),triangles=tris,material_primitives=len(prim),
    sha256=hashlib.sha256(raw).hexdigest(),dimensions_m=[8,4,3.2],
    dimensions_semantics="8 across lane, 4 along lane, 3.2 tall proposed art; centered local X axle",
    preview_centre_travel_radius_m=[r0,r1], axle_section_bounding_radius_m=round(sweep_radius,6),
    lane_edge_margin_per_side_m=1, rim_horizontal_lower_bound_m=round(52-outer_radius,6), tests=tests,
),indent=2)+"\n")

if "--proof-only" not in args:
    a=math.radians(-135)
    pos=Vector((24*math.cos(a),24*math.sin(a),0))
    # Local +Y points along the chosen 135-degree lane.
    roll=Matrix.Rotation(math.radians(27),4,"X")
    support=-min((roll @ v).z for v in pts)
    t=Matrix.Translation(pos+Vector((0,0,support+.077))) @ Matrix.Rotation(a-math.pi/2,4,"Z") @ roll
    for ob in cargo:
        if ob.parent not in cargo: ob.matrix_world=t@ob.matrix_world
    scene.render.engine="CYCLES"
    scene.cycles.samples=32
    scene.cycles.use_denoising=False
    scene.cycles.adaptive_threshold=.07
    scene.world=bpy.data.worlds.new("Slate arena review")
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value=(.25,.40,.62,1)
    bg.inputs[1].default_value=.65
    def aim(o,target):
        o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
    def area(name,at,target,energy,size,c):
        d=bpy.data.lights.new(name,"AREA"); d.energy=energy;d.size=size;d.color=c
        o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=at;aim(o,target)
    d=bpy.data.lights.new("Arena broad key","SUN"); d.energy=1.6
    o=bpy.data.objects.new(d.name,d); scene.collection.objects.link(o); o.rotation_euler=(.38,-.45,-.35)
    area("Honey side bounce",pos+Vector((2,-9,9)),pos,2600,6,(1,.67,.33))
    area("Roof spill",pos+Vector((-8,3,14)),pos,3800,9,(.65,.87,1))
    for name,delta,target,lens,dims in (
        ("approach",(11,11,4.3),(0,0,1.6),47,(1320,900)),
        ("lane",(18,-9,14),(1,-1,1.1),42,(1320,900)),
    ):
        bpy.ops.object.camera_add(location=pos+Vector(delta))
        camera=bpy.context.object; camera.data.lens=lens; aim(camera,pos+Vector(target));scene.camera=camera
        scene.render.resolution_x,scene.render.resolution_y=dims
        scene.render.image_settings.file_format="JPEG"
        scene.render.image_settings.quality=94
        scene.render.filepath=str(out/f"overflow-{name}.jpg")
        bpy.ops.render.render(write_still=True)

"""Static W06 practice plank and pinned 20 m staging study. Blender 4.3."""
import hashlib
import json
import math
import random
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import clear_scene, export, output_directory

repo = HERE.parents[2]
out = output_directory()
clear_scene()
scene = bpy.context.scene
rng = random.Random(603)


def material(name, color, metal=0, rough=.68):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    return m


pine = [material("Sun-worn larch " + str(i), c) for i, c in enumerate(
    [(.43,.235,.116), (.52,.31,.166), (.62,.393,.213), (.55,.325,.158)])]
iron = material("Blue-black iron", (.08,.105,.112), .59, .46)
lift = material("Rubbed iron", (.27,.30,.29), .68, .42)
orange = material("Faded vermilion paint", (.47,.052,.034), 0, .78)
red = material("Vermilion showing through", (.61,.073,.043), 0, .74)
grain = material("Split grain", (.29,.137,.071), 0, .82)
bare = material("Exposed wood", (.64,.405,.202), 0, .80)


def mesh(name, verts, faces, mat):
    d = bpy.data.meshes.new(name)
    d.from_pydata(verts, [], faces)
    d.materials.append(mat)
    o = bpy.data.objects.new(name, d)
    scene.collection.objects.link(o)
    return o


def block(name, p, dim, mat, bevel=.012):
    x,y,z = p
    a,b,c = [i*.5 for i in dim]
    o = mesh(name, [(x+i*a,y+j*b,z+k*c) for k in [-1,1] for j in [-1,1] for i in [-1,1]],
             [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)], mat)
    if bevel:
        m = o.modifiers.new("Chamfered edges", "BEVEL")
        m.width, m.segments = bevel, 1
        o.modifiers.new("Weighted edges", "WEIGHTED_NORMAL")
    return o


def layers(name, center, radius, mat, thickness, n=16):
    x,y,z = center
    v = [(x+radius*math.cos(i*math.tau/n), y+j*thickness/2,
          z+radius*math.sin(i*math.tau/n)) for j in [-1,1] for i in range(n)]
    f = [tuple(range(n)), tuple(range(2*n-1,n-1,-1))]
    f += [(i, n+i, n+(i+1)%n, (i+1)%n) for i in range(n)]
    return mesh(name, v, f, mat)


# -Y is the face. The graphics use no image texture: decal fragments follow
# individual boards and preserve the visible board gaps.
for i, dx in enumerate((-.352,-.176,0,.176,.352)):
    top = 2.03 + (i % 3 - 1)*.014
    low = 1.10 + (i % 2 - .5)*.016
    block("Larch plank " + str(i+1), (dx,0,(top+low)/2), (.17,.104,top-low), pine[i%4], .013)
    for k in range(15):
        x = dx + rng.uniform(-.072,.072)
        z = rng.uniform(low+.021,top-.026)
        l = min(rng.uniform(.017,.22), top-z-.015)
        width = rng.uniform(.0008,.0029)
        mesh("Sawed grain", [(x,-.0528,z),(x+width,-.0528,z+l*.56),
             (x+width*.11,-.0528,z+l),(x-width*.55,-.0528,z+l*.42)],
             [(0,1,2,3)], grain if k%4 else bare)
    for z in (1.20, 1.94):
        layers("Hammered face peg",(dx,-.057,z),.020,lift,.012,6)
    left, right = max(dx-.080,-.232), min(dx+.080,.232)
    if left < right:
        xs = [left+(right-left)*j/10 for j in range(11)]
        def h(x):
            return math.sqrt(max(0,.232**2-x*x))
        upper=[(x,-.0535,1.56+h(x)*(1+rng.uniform(-.014,.014))) for x in xs]
        lower=[(x,-.0535,1.56-h(x)*(1+rng.uniform(-.014,.014))) for x in xs[::-1]]
        mesh("Handpainted signal roundel",upper+lower,[tuple(reversed(range(22)))],orange if i%2 else red)

for num in range(37):
    col = rng.choice([-2,-1,0,1,2])
    x = col*.176 + rng.uniform(-.075,.075)
    z = rng.uniform(1.38,1.73)
    if x*x+(z-1.56)**2 < .222**2:
        w = rng.uniform(.0023,.0056)
        mesh("Missing paint",[(x-w,-.0542,z-w),(x+w,-.0542,z-w*.4),
             (x+w*.5,-.0542,z+w*2.5),(x-w*.2,-.0542,z+w*.9)],[(0,1,2,3)],bare)

block("Joiner back bar low", (0,.084,1.20),(.94,.055,.116),iron)
block("Joiner back bar high", (0,.084,1.954),(.94,.055,.116),iron)
for x in (-.43,.43):
    for z in (1.20,1.954):
        layers("Rear hex bolt",(x,.117,z),.025,lift,.015,6)
block("Post", (0,.10,.74),(.165,.175,1.48),pine[0],.014)
block("Weathered foot", (0,.12,.055),(.58,.45,.11),iron,.023)
block("Foot dark cap", (0,.12,.12),(.27,.28,.08),lift,.014)
# Bake edits into one material-partitioned mesh, not dozens of GLB nodes.
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = next(o for o in scene.objects if o.name == "Larch plank 3")
bpy.ops.object.convert(target="MESH")
bpy.ops.object.join()
target_mesh = bpy.context.object
target_mesh.name = "W06 Practice plank"
part = [target_mesh]
asset = out/"w3b-practice-plank.glb"
export(part, asset)
raw = asset.read_bytes()
assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
g=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
assert not any(k in g for k in ('images','animation','animations','skins','cameras'))
triangle_count = sum(g["accessors"][p["indices"]]["count"]//3
                     for m in g["meshes"] for p in m["primitives"])
verts=[o.matrix_world@v.co for o in part for v in o.data.vertices]
bounds=[max(v[i] for v in verts)-min(v[i] for v in verts) for i in range(3)]
assert len(g["meshes"]) == len(g["nodes"]) == 1 and len(raw) < 75000
bpy.data.objects.remove(target_mesh, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(asset))
assert len(scene.objects) == 1 and next(iter(scene.objects)).type == "MESH"


def import_donor(name, expected, x, y):
    path=repo/"public/assets/wildshard-art"/name
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    incoming=sorted(set(scene.objects)-before,key=lambda o:o.name)
    coords=[o.matrix_world@v.co for o in incoming if o.type=="MESH"
            for v in o.data.vertices]
    assert coords
    lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
    shift=Vector((x-(lo.x+hi.x)*.5,y-(lo.y+hi.y)*.5,-lo.z))
    for o in incoming:
        if o.parent not in incoming:
            o.location += shift
    return {"file":name,"sha256":expected,"stage_xy_m":[x,y],
            "world_translation_m":[round(p,4) for p in shift],
            "unscaled_bounds_m":[round(p,4) for p in hi-lo]}


# First two are the other W3b demonstration subjects; the backstop anchors
# the staging context. No W3b counter, effects or course changes.
donors = [
    import_donor("wsc-prop-078-soft-practice-dummy.glb",
                 "f8170426252c1c84d15f8c5fe503d70e6fc3602a58608fd2c42306a941a9b566",-2.30,.22),
    import_donor("wsc-prop-029-straw-bale-target.glb",
                 "065d475508d3dcbbdad2b295f5ec417572a2505eb1280e8c9c5da7f7e72542a0",2.34,.27),
    import_donor("wsc-module-006-range-backstop.glb",
                 "be6d2b41b97f6b81a2ffbdc6aa833ca82b4b9be1af821bcb2d3701ebfac8b9b6",0,3.4)
]
floor=material("Dusty clay lane",(.31,.214,.136),0,.86)
stone=material("Quiet lane stripe",(.56,.47,.29),0,.85)
block("Review yard ground",(0,0,-.09),(50,65,.18),floor,0)
for x in (-3.64,3.64):
    block("Review lane boundary",(x,-8,.016),(.08,25,.032),stone,.006)
for x in (-2.3,0,2.34):
    block("Review floor station",(x,-1.38,.013),(1.25,.09,.026),stone,.005)

world=bpy.data.worlds.new("Range daylight")
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.44,.60,.86,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.37
scene.world=world
sun=bpy.data.lights.new("West sun","SUN")
sun.energy=2.5
sun.angle=math.radians(7)
sun.color=(1,.82,.61)
key=bpy.data.objects.new("West sun",sun)
scene.collection.objects.link(key)
key.rotation_euler=Vector((.4,.55,-.72)).to_track_quat("-Z","Y").to_euler()
d=bpy.data.lights.new("Front sky patch","AREA")
d.energy,d.size=420,4
d.color=(.75,.85,1)
area=bpy.data.objects.new("Front sky patch",d)
scene.collection.objects.link(area)
area.location=(.25,-4.5,5)
area.rotation_euler=(Vector((0,0,1.3))-area.location).to_track_quat("-Z","Y").to_euler()

cam=bpy.data.objects.new("W06 study camera",bpy.data.cameras.new("W06 study camera"))
scene.collection.objects.link(cam)
scene.camera=cam
cam.data.sensor_fit="HORIZONTAL"
scene.render.engine="CYCLES"
scene.cycles.samples=44
scene.cycles.use_denoising=False
scene.cycles.max_bounces=5
scene.view_settings.view_transform="AgX"
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG"
scene.render.image_settings.quality=91


def render(name, p, target, lens, wh):
    cam.location=p
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=wh
    scene.render.filepath=str(out/(name+".jpg"))
    bpy.ops.render.render(write_still=True)


render("plank-detail", (1.44,-3.8,2.19), (0,0,1.2), 63, (920,1000))
render("practice-trio", (0,-7.45,1.7), (0,.12,1.21), 41, (1220,770))
width=1240
lens=36/(2*math.tan(math.radians(25)))
render("range-20m", (0,-20,1.7), (0,0,1.47), lens, (width,700))
report={
    "scope":"Static W06 art study; no in-game placement, scoring, hit, burn, or stagger wiring.",
    "pin":"docs/plans/kitchen-sink-v2/slices/W3b-bow-crossbow-ammo.md and W06 polished mockup",
    "file":asset.name,"bytes":len(raw),"triangles":triangle_count,
    "sha256":hashlib.sha256(raw).hexdigest(),"nominal_asset_bounds_m":[round(v,4) for v in bounds],
    "camera":{"eye_m":1.7,"ground_distance_m":20,"horizontal_fov_deg":50,
              "image_width_px":width,"roundel_nominal_width_px":round(width*lens*.464/(36*20),2)},
    "unchanged_donors":donors}
(out/"practice.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))

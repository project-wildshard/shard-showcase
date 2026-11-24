"""W2b editorial stock display. Two reusable retail fixtures, no host logic."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

out = output_directory()
scene = bpy.context.scene
asset_dir = Path(__file__).resolve().parents[3] / "public/assets/wildshard-art"
clear_scene()


def pbr(name, color, metallic, roughness):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = (*color, 1)
    n.inputs["Metallic"].default_value = metallic
    n.inputs["Roughness"].default_value = roughness
    return m


iron = pbr("Grey enamel", (.061,.102,.119), .40, .57)
ochre = pbr("Mustard enamel", (.41,.235,.074), .26, .55)
oak = [pbr("Dark oak " + str(i), c, .0, .63) for i,c in enumerate([
    (.093,.041,.023), (.112,.049,.024), (.127,.052,.025), (.107,.045,.025)])]
back = pbr("Blue wool liner", (.037,.072,.082), .02, .83)
brass = pbr("Burnished brass", (.47,.27,.092), .66, .47)
felt = pbr("Green felt", (.045,.108,.088), .04, .85)


def block(name, center, dimensions, mat, bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod = o.modifiers.new("Art bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return o


def bolt(name, center, mat, radius=.017):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=radius, depth=.012,
                                      location=center, rotation=(math.pi/2,0,0))
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    return o


def finish(name, maker):
    before = set(scene.objects)
    maker()
    b = [o for o in scene.objects if o not in before]
    bpy.ops.object.select_all(action="DESELECT")
    for o in b:
        o.select_set(True)
    bpy.context.view_layer.objects.active = b[0]
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    # Local pivot = bottom center, good for repeated placement.
    scene.cursor.location = (0,0,0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    f = out / (name + ".glb")
    bpy.ops.export_scene.gltf(filepath=str(f), export_format="GLB", use_selection=True,
                             export_animations=False, export_texcoords=False)
    blob = f.read_bytes()
    assert struct.unpack_from("<4sII", blob) == (b"glTF",2,len(blob))
    doc = json.loads(blob[20:20+struct.unpack_from("<I",blob,12)[0]])
    count = sum(doc["accessors"][p["indices"]]["count"]//3 for p in doc["meshes"][0]["primitives"])
    assert len(blob) < 65536 and count < 1600, (name,len(blob),count)
    return f, {"bytes":len(blob),"triangles":count,"sha256":hashlib.sha256(blob).hexdigest()}


def rack():
    block("Wool-lined backing", (0,.018,1.47),(2.38,.09,2.38),back,.026)
    for xx in (-1.18,1.18):
        block("Enamel upright", (xx,-.022,1.40),(.109,.17,2.69),iron,.021)
        block("Low kick foot", (xx,-.02,.045),(.20,.53,.09),iron,.017)
        for zz in (.33,2.44):
            bolt("Upright badge rivet", (xx,-.116,zz),brass,.024)
    for zz in (.21,2.63):
        block("Lower or upper oak stretcher", (0,-.035,zz),(2.47,.17,.135),oak[2],.018)
    for xx in (-.43,.48):
        block("Brass divider", (xx,-.065,1.44),(.031,.035,2.20),brass,0)
    for xx in (-.81,.0,.83):
        block("Label bezel", (xx,-.123,.345),(.32,.041,.11),ochre,.013)
        block("Blank reversible label", (xx,-.151,.345),(.245,.018,.060),iron,0)
    for xx,z0 in [(-.88,.78),(-.88,1.83),(-.115,1.09),(-.115,1.79),(.84,1.03),(.84,1.79)]:
        block("Decorative stock cradle", (xx,-.12,z0),(.20,.17,.115),oak[1],0)
        block("Felt isolator", (xx,-.198,z0+.045),(.145,.075,.050),felt,0)


def riser():
    block("Counter riser foundation", (0,0,.045),(1.16,1.07,.09),iron,.035)
    for i in range(6):
        z=.126+i*.064
        block("Stacked face plank", (0,0,z),(1.09,1.00,.071),oak[i%4],.009)
    block("Green felt display surface", (0,0,.502),(1.21,1.075,.092),felt,.032)
    for xx in (-.46,.46):
        for yy in (-.41,.41):
            block("Enamel corner restraint", (xx,yy,.26),(.095,.085,.37),iron,0)
    block("Riser display label", (0,-.515,.31),(.39,.07,.128),ochre,.019)
    block("Slate caption plate", (0,-.56,.312),(.31,.035,.080),iron,.012)
    for xx in (-.155,.155):
        bolt("Corner inset", (xx,-.582,.313),brass,.011)


fixtures = {}
fixtures["wall"] = finish("w2b-stock-wall", rack)
fixtures["riser"] = finish("w2b-counter-riser", riser)
clear_scene()


def import_one(path):
    previous = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    o, = [o for o in scene.objects if o not in previous and o.type=="MESH"]
    return o


def bounds(obj):
    p = [obj.matrix_world @ Vector(co) for co in obj.bound_box]
    return [[round(fun(v[i] for v in p),5) for i in range(3)] for fun in (min,max)]


wall = import_one(fixtures["wall"][0])
riser_o = import_one(fixtures["riser"][0])
riser_o.location = (1.99,-.52,0)
donors = {
    "spear": (-.85,-.285,1.315),
    "sword": (.0,-.26,1.15),
    "bow": (.75,-.28,1.38),
    "crossbow": (1.99,-.52,.675),
}
numbers = {"sword":1,"spear":2,"bow":3,"crossbow":4}
models = {}
for slug, at in donors.items():
    f = asset_dir / f"wsc-gear-{numbers[slug]:03d}-{slug}.glb"
    o = import_one(f)
    o.location = at
    if slug=="crossbow":
        o.rotation_euler.z = math.pi
    bpy.context.view_layer.update()
    models[slug] = {"glb":f.name,"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),
                    "translation_blender":at,"bounds_blender":bounds(o)}
wmin,wmax=bounds(wall)
rmin,rmax=bounds(riser_o)
for a,b in zip(("spear","sword"),("sword","bow")):
    assert models[b]["bounds_blender"][0][0]-models[a]["bounds_blender"][1][0] > .25
for slug in ("spear","sword","bow"):
    lo,hi=models[slug]["bounds_blender"]
    assert lo[0]>wmin[0] and hi[0]<wmax[0]
    assert lo[2]>=.28 and hi[2]<2.60 and hi[1]<-.12, (slug,lo,hi)
lo,hi=models["crossbow"]["bounds_blender"]
assert all(rmin[i]<lo[i]<hi[i]<rmax[i] for i in (0,1)), (lo,hi,rmin,rmax)
assert .001 < lo[2]-.548 < .08, (lo,hi)
assert rmin[0]-wmax[0]>.05
(out/"w2b-stock-display.json").write_text(json.dumps({
    "readiness":"static modular shop fixture art and merchandising layout; no native shop room, selection or inventory logic",
    "source":"W2b stock list; WSC-ARCH-006 related study; four exact inventory donors",
    "assets":{k:v[1] for k,v in fixtures.items()},"inventory":models,
},indent=2)+"\n")


def aim(o,pos):
    o.rotation_euler=(Vector(pos)-o.location).to_track_quat("-Z","Y").to_euler()


def lamp(name,at,look,power,tint,size):
    data=bpy.data.lights.new(name,"AREA")
    data.energy,data.color,data.size=power,tint,size
    o=bpy.data.objects.new(name,data); scene.collection.objects.link(o); o.location=at; aim(o,look)


if os.getenv("WILDSHARD_VALIDATE_ONLY") != "1":
    studio = pbr("Mineral studio", (.043,.068,.077), .03, .74)
    block("Stage",(.5,0,-.17),(200,200,.30),studio,0)
    wall_mat = pbr("Dark workshop wall", (.043,.064,.069), .0, .87)
    block("Backdrop",(.5,1.08,2.40),(200,.06,5),wall_mat,0)
    lamp("Warm diffuse shop light",(-2.1,-3.8,4.0),(.25,0,1.5),865,(1,.79,.54),3.5)
    lamp("Overcast storefront", (2.6,-2.0,3.2),(.55,0,1.15),540,(.48,.73,1),2.8)
    lamp("Riser lip", (1.1,.54,2.85),(1.45,-.31,.65),325,(1,.56,.26),1.7)
    scene.world=bpy.data.worlds.new("Workshop world")
    scene.world.color=(.13,.18,.21)
    camera=bpy.data.cameras.new("Shop study")
    cam=bpy.data.objects.new(camera.name,camera)
    scene.collection.objects.link(cam); scene.camera=cam
    camera.type="ORTHO"
    scene.render.engine="CYCLES"
    scene.cycles.samples=36
    scene.cycles.use_denoising=False
    scene.view_settings.view_transform="AgX"
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="JPEG"
    scene.render.image_settings.quality=90
    for label, at, target, scale, res in [
        ("wall", (2.25,-7.9,3.7),(.49,-.04,1.34),4.45,(1440,1000)),
        ("riser",(3.26,-3.2,2.16),(1.99,-.48,.41),1.64,(1140,920)),
    ]:
        cam.location=at; aim(cam,target); camera.ortho_scale=scale
        scene.render.resolution_x,scene.render.resolution_y=res
        scene.render.filepath=str(out/f"nov24-w2b-stock-{label}.jpg")
        bpy.ops.render.render(write_still=True)

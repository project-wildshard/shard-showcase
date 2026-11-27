"""E10d Room 4 environment: sealed study and matched idle/warning renders."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import clear_scene, export, output_directory

out = output_directory()
clear_scene()
scene = bpy.context.scene
donors = {
    "plate": ("wsc-prop-064-metal-floor-plates.glb", "7e4eef8077b1d59fd31d17235ef1cedca8bab9910c0c283bcf5546fae144ed85"),
    "bay": ("wsc-arch-002-industrial-wall-bay.glb", "24f3a7736d111033d724f0f6244c4d10f757fe3066ea1b8b12d5ef60a5a6f625"),
    "door": ("wsc-prop-063-round-vault-bulkhead.glb", "25db93c5d45901a6599674ea857982700f57705c1b171e23978140537e41eedf"),
}
assets = HERE.parents[2] / "public/assets/wildshard-art"


def read_glb(f):
    before = set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(f))
    bpy.context.view_layer.update()
    new = set(scene.objects)-before
    result = [(o.name,o.data,o.matrix_world.copy()) for o in sorted(new,key=lambda o:o.name)
              if o.type == "MESH"]
    for o in new:
        bpy.data.objects.remove(o,do_unlink=True)
    assert result
    return result


templates = {}
for key,(name,sha) in donors.items():
    f = assets/name
    assert hashlib.sha256(f.read_bytes()).hexdigest() == sha
    templates[key] = read_glb(f)


def place(key,name,p,yaw=0):
    matrix = Matrix.Translation(Vector(p)) @ Matrix.Rotation(yaw,4,"Z")
    result = []
    for n,d,t in templates[key]:
        o = bpy.data.objects.new(name+" | "+n,d)
        scene.collection.objects.link(o)
        o.matrix_world = matrix @ t
        result.append(o)
    return result


def mat(n,c,metal=.4,rough=.47,emission=0):
    m = bpy.data.materials.new(n)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*c,1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    b.inputs["Emission Color"].default_value = (*c,1)
    b.inputs["Emission Strength"].default_value = emission
    return m


iron = mat("Blued furnace casing",(.047,.060,.067),.57,.58)
graphite = mat("Recessed graphite",(.013,.023,.028),.31,.44)
zinc = mat("Worn zinc rails",(.21,.26,.28),.68,.37)
copper = mat("Oxide copper shield",(.22,.092,.041),.64,.48)
gold = mat("Burnt ochre safety ink",(.41,.174,.037),.28,.59)
low = mat("Inactive ceramic",(.14,.077,.036),.26,.63,.016)
lit = mat("Lockdown stripe amber",(.98,.22,.022),.28,.52,3.4)
lit_edge = mat("Warning inset bright amber",(.98,.49,.095),.27,.44,4.3)
cyan = mat("Recessed turquoise status",(.035,.45,.53),.17,.5,1.8)
bulb = mat("Vault amber diffuser",(.95,.39,.085),.11,.45,3.8)


def mesh_obj(n,vs,fs,m):
    d = bpy.data.meshes.new(n)
    d.from_pydata(vs,[],fs)
    d.update()
    d.materials.append(m)
    o = bpy.data.objects.new(n,d)
    scene.collection.objects.link(o)
    return o


def box(n,p,d,m,bevel=0,yaw=0):
    x,y,z = [v*.5 for v in d]
    vs = [(i*x,j*y,k*z) for k in (-1,1) for j in (-1,1) for i in (-1,1)]
    fs = [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    o = mesh_obj(n,vs,fs,m)
    o.location = p
    o.rotation_euler.z = yaw
    if bevel:
        mod = o.modifiers.new("Edge wear radius","BEVEL")
        mod.width,mod.segments = bevel,1
        o.modifiers.new("Face normals","WEIGHTED_NORMAL")
    return o


def rect_ring(n,w,h,e,y,depth,m):
    def cut(w,h,e):
        x,z=w/2,h/2
        return [(-x+e,-z),(x-e,-z),(x,-z+e),(x,z-e),
                (x-e,z),(-x+e,z),(-x,z-e),(-x,-z+e)]
    loops = [cut(w,h,e),cut(w-.25,h-.25,e*.74)]
    vs = [(x,q,z) for q in (y-depth/2,y+depth/2) for l in loops for x,z in l]
    fs = []
    for i in range(8):
        j=(i+1)%8
        fs += [(i,j,j+8,i+8),(16+i,24+i,24+j,16+j),
               (i,16+i,16+j,j),(8+i,8+j,24+j,24+i)]
    return mesh_obj(n,vs,fs,m)


hatch = [
    box("Hatch · sealed back", (0,.035,0),(2.36,.21,2.13),graphite,.065),
    rect_ring("Hatch · cut-corner frame",2.45,2.21,.24,-.115,.16,zinc),
    rect_ring("Hatch · inner gasket",2.21,1.97,.15,-.144,.12,graphite),
    box("Hatch · pressure panel",(0,-.12,0),(1.91,.12,1.65),iron,.058),
    box("Hatch · visor slot",(0,-.204,.43),(1.44,.053,.19),graphite,.027),
    box("Hatch · status strip",(0,-.234,.43),(.63,.014,.043),cyan,.007),
    box("Hatch · lower split",(0,-.201,-.13),(1.64,.035,.056),zinc,.009),
]
for sign in (-1,1):
    hatch += [box("Hatch · clamp cover",(sign*.62,-.227,-.41),(.34,.11,.39),copper,.045),
              box("Hatch · pad marker",(sign*1.02,-.205,.60),(.081,.019,.29),gold,.008)]

# An inset plus two chevrons, sized for one central clear patch of PROP-064.
# Hot reference export uses two named materials; idle uses local overrides.
tile = [box("Tile warning · ceramic strips",(0,0,.003),(2.58,.24,.006),lit,.002),
        box("Tile warning · edge wafer",(0,0,.006),(2.30,.055,.005),lit_edge,.001)]
for sign in (-1,1):
    for x in (-.88,.88):
        tile.append(box("Tile warning · offset chevron",(x,sign*.32,.0028),
                        (.53,.105,.0056),lit,.001,sign*.44))
pinned = {}
for parts,key in ((hatch,"hatch"),(tile,"tile")):
    file = out/f"vault-r4-{key}.glb"
    export(parts,file)
    data = file.read_bytes()
    assert data[:4]==b"glTF" and struct.unpack_from("<I",data,8)[0]==len(data)
    doc = json.loads(data[20:20+struct.unpack_from("<I",data,12)[0]])
    triangles = sum(doc["accessors"][p["indices"]]["count"]//3
                    for m in doc["meshes"] for p in m["primitives"])
    assert len(data)<105000 and triangles<2800
    assert not any(doc.get(k) for k in ("images","animations","skins","cameras"))
    pinned[key] = {"file":file.name,"bytes":len(data),"triangles":triangles,
                   "sha256":hashlib.sha256(data).hexdigest()}
    for o in parts:
        bpy.data.objects.remove(o,do_unlink=True)
    templates[key] = read_glb(file)

R = 12.0
pitch = 3.155
# All intact donors inside the clear radius; fill rim with continuous
# foundation instead of destructively cutting or exporting the donor plates.
plate_meshes = []
coords = []
for j in range(-4,5):
    for i in range(-4,5):
        x,y = i*pitch,j*pitch
        if math.hypot(abs(x)+pitch/2,abs(y)+pitch/2) > R:
            continue
        coords.append((i,j))
        plate_meshes += place("plate",f"Plate {i},{j}",(x,y,-.101))
assert len(coords)==29
wall_n=21
step=math.tau/wall_n
span=2*R*math.tan(step/2)
rim=R/math.cos(step/2)


def disc(n,r,z,m):
    angles=[(i+.5)*step for i in range(wall_n)]
    return mesh_obj(n,[(-r*math.sin(a),r*math.cos(a),z) for a in angles],
                    [tuple(range(wall_n))],m)


disc("Worn perimeter floor continuous under inserts",rim+.10,-.005,zinc)
hatches = []
for i in range(wall_n):
    a=i*step
    radial=Vector((-math.sin(a),math.cos(a),0))
    def loc(r,z):
        return tuple(radial*r+Vector((0,0,z)))
    box("Deep continuous wall shell",loc(12.15,2.83),(span+.05,.31,5.69),iron,0,a)
    if i in (0,10):
        place("door","Sealed Vault bulkhead",loc(11.77,0),a)
        box("Bulkhead overhead casing",loc(11.54,3.75),(3.43,.69,1.07),copper,.10,a)
    elif i in (2,19):
        hatches += place("hatch","Sealed spawn hatch",loc(11.44,1.42),a)
    else:
        place("bay","Shared lower wall bay",loc(11.92,0),a)
    box("Upper recess",loc(11.78,3.65),(3.32,.32,.93),graphite,.054,a)
    box("Top panel blue rim",loc(11.76,4.93),(3.77,.32,.24),zinc,.041,a)
    if i%2==0 or i in (19,):
        box("Warm wall fixture",loc(11.53,4.12),(1.13,.29,.21),copper,.06,a)
        box("Amber diffuser",loc(11.34,4.10),(.87,.091,.09),bulb,.019,a)
    c=a+step/2
    box("Deep angular rib",(-11.53*math.sin(c),11.53*math.cos(c),3.09),
        (.24,.45,4.88),zinc,.051,c)
disc("Sealed roof",rim+.1,5.6,graphite).data.polygons[0].flip()

# Probe the exact reimported local pad after placement on five plates.
# A flat mark does not replace the plate or need a duplicated donor mesh.
def bvh(objs):
    vs,fs=[],[]
    for o in objs:
        n=len(vs)
        vs.extend(o.matrix_world@v.co for v in o.data.vertices)
        fs.extend(tuple(n+i for i in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(vs,fs)


slab = bvh(plate_meshes)
stripe = []
gap = []
for i in (-2,-1,0,1,2):
    pos=(i*pitch,0,.006)
    pieces=place("tile","Five-lane stripe",pos)
    bpy.context.view_layer.update()
    for o in pieces:
        for v in o.data.vertices:
            p=o.matrix_world@v.co
            q=slab.ray_cast(Vector((p.x,p.y,.15)),Vector((0,0,-1)),.32)[0]
            assert q is not None and p.z-q.z>.003,(p,q)
            gap.append(p.z-q.z)
    stripe.extend(pieces)
assert len(hatches)==22
on_mats=[(slot,slot.material) for o in stripe for slot in o.material_slots]
for slot,_ in on_mats:
    slot.link="OBJECT"

def area(n,p,target,w,color,size):
    d=bpy.data.lights.new(n,"AREA")
    d.energy,d.color,d.size=w,color,size
    o=bpy.data.objects.new(n,d)
    scene.collection.objects.link(o)
    o.location=p
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()


# Cross light reveals steel, but remains fixed during the comparison.
area("Warm far floor key",(0,8.0,4.9),(0,2,0),1175,(1,.62,.32),6)
area("Cold door fill",(-5,-5,4.8),(0,4,1),1700,(.45,.72,1),7)
area("Warm left accent",(-8,5,4.7),(-4,1,1.1),620,(1,.54,.23),4)
area("Warm right accent",(8,5,4.7),(4,1,1.1),680,(1,.57,.25),4)
area("Near diffuse key",(2,-6,4.9),(0,-2,0),510,(.64,.78,1),6)
bpy.ops.object.camera_add(location=(.86,-8.8,1.70))
cam=bpy.context.object
scene.camera=cam
cam.data.lens=24
cam.rotation_euler=(Vector((0,3.1,1.30))-cam.location).to_track_quat("-Z","Y").to_euler()
scene.render.engine="CYCLES"
scene.cycles.samples=52
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.045
scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.render.resolution_x,scene.render.resolution_y=1420,930
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG"
scene.render.image_settings.quality=91
sweep_path=os.environ.get("WSC_VAULT_SWEEP")
for state in (() if sweep_path else ("idle","warning")):
    for slot,original in on_mats:
        slot.material=low if state=="idle" else original
    scene.render.filepath=str(out/f"nov24-vault-r4-{state}.jpg")
    if not os.environ.get("WILDSHARD_VALIDATE_ONLY"):
        bpy.ops.render.render(write_still=True)
(out/"vault-r4-validation.json").write_text(json.dumps({
    "room_apothem_m": R,"wall_bays":wall_n,"whole_plates":len(coords),
    "hatches":2,"sealed_bulkheads":2,"active_tiles":5,
    "warn_five_tile_positions_blender_m":[[i*pitch,0,.006] for i in range(-2,3)],
    "pad_surface_rays":len(gap),"pad_gap_m":[min(gap),max(gap)],
    "assets":pinned,"donor_sha256":{k:v[1] for k,v in donors.items()},
    "runtime":False,"native_placement":False},indent=2)+"\n")


if sweep_path:
    # Use the timing fixture's 30-Hz states on exact authored donor plates.
    # Keep the old five-insert comparison intact when this option is absent.
    sweep=json.loads(Path(sweep_path).read_text())
    assert sweep["tile_sha256"] == pinned["tile"]["sha256"]
    assert sorted((q["col"],q["row"]) for q in sweep["slots"]) == sorted(coords)
    assert all(abs(x-y)<1e-6 for x,y in zip((sweep["pitch"],sweep["hz"],sweep["warningFrames"]),(pitch,30,30)))
    for o in stripe:
        bpy.data.objects.remove(o,do_unlink=True)
    active=mat("Sweep active · vermilion ceramic",(1,.035,.007),.28,.44,1.65)
    active_edge=mat("Sweep active · hot center",(1,.086,.013),.25,.42,3.7)
    strike_slots={}
    sweep_gaps=[]
    for q in sweep["slots"]:
        x,y,z=q["xyz"]
        key=(q["col"],q["row"])
        assert abs(x-key[0]*pitch)<1e-6 and abs(-z-key[1]*pitch)<1e-6
        assert abs(y-.006)<1e-6
        objects=place("tile",f"Sweep slot {key}",(x,-z,y))
        bpy.context.view_layer.update()
        slots=[]
        for o in objects:
            for v in o.data.vertices:
                p=o.matrix_world@v.co
                t=slab.ray_cast(Vector((p.x,p.y,.15)),Vector((0,0,-1)),.32)[0]
                assert t is not None and p.z-t.z>.003, (key,p,t)
                sweep_gaps.append(p.z-t.z)
            for slot in o.material_slots:
                original=slot.material
                hot=(low if "ceramic strips" in o.name else active_edge
                     if "bright" in original.name else active)
                slot.link="OBJECT"
                slots.append((slot,original,hot))
        strike_slots[key]=slots
    proof={"reimport_pad_vertices":len(sweep_gaps),"min_pad_gap_m":min(sweep_gaps),
           "max_pad_gap_m":max(sweep_gaps),"same_plates":len(coords),
           "camera_eye_blender_m":[.0,-10.9,1.70],"timebase":30}
    cam.location=(0,-10.9,1.70)
    cam.data.lens=22
    cam.rotation_euler=(Vector((0,1.8,-.8))-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.render.resolution_x,scene.render.resolution_y=740,1000
    scene.cycles.samples=32
    scene.cycles.adaptive_threshold=.065
    for case in sweep["preview"]:
        for q in case["states"]:
            for slot,warn,hot in strike_slots[(q["col"],q["row"])]:
                slot.material={"idle":low,"warning":warn,"active":hot}[q["state"]]
        scene.render.filepath=str(out/f"vault-r4-sweep-{case['frame']}.jpg")
        if not os.environ.get("WILDSHARD_VALIDATE_ONLY"):
            bpy.ops.render.render(write_still=True)
    (out/"vault-r4-sweep-geometry.json").write_text(json.dumps(proof,indent=2)+"\n")

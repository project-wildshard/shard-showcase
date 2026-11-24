"""E10b entrance record plaque and two visual states of a room-door beacon."""
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
repo = Path(__file__).resolve().parents[3]
donor = repo / "public/assets/wildshard-art/wsc-arch-007-training-vault-portal.glb"
scene = bpy.context.scene
clear_scene()


def shade(name, rgb, metal=.0, rough=.55, emit=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*rgb,1)
    n = m.node_tree.nodes["Principled BSDF"]
    for key,val in {"Base Color":(*rgb,1), "Metallic":metal, "Roughness":rough,
                    "Emission Color":(*rgb,1), "Emission Strength":emit}.items():
        n.inputs[key].default_value = val
    return m


gunmetal = shade("Slate enamel", (.055,.103,.12), .40)
bezel = shade("Oxide brass", (.36,.179,.063), .58, .44)
warm = shade("Earth fired orange", (.26,.11,.048), .14)
ink = shade("Glazed ink", (.012,.024,.031), .20, .4)
linen = shade("Warm porcelain", (.71,.62,.43), .0, .65)
neutral = shade("Unlit glyph", (.12,.25,.258), .04, .64)
cyan = shade("Access cyan", (.018,.45,.55), .14, .42, .42)
amber = shade("Seal amber", (.74,.17,.044), .16, .43, .42)


def cube(name, at, dims, m, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=at)
    o=bpy.context.object
    o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if bevel:
        mod=o.modifiers.new("Silhouette bevel","BEVEL")
        mod.width,mod.segments=bevel,1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return o


def bar(name,a,b,y,thickness,m):
    x,z=(a[0]+b[0])/2,(a[1]+b[1])/2
    o=cube(name,(x,y,z),(math.dist(a,b)+thickness,.003,thickness),m)
    o.rotation_euler.y=-math.atan2(b[1]-a[1],b[0]-a[0])
    return o


def stud(x,y,z,metal=bezel):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.027,depth=.016,
                                      location=(x,y,z),rotation=(math.pi/2,0,0))
    o=bpy.context.object; o.name="Rivet"; o.data.materials.append(metal)


FONT = {
    "B": [[(0,0),(0,1),(.7,1),(1,.77),(.7,.52),(0,.52)],
          [(.7,.52),(1,.27),(.7,0),(0,0)]],
    "E": [[(1,1),(0,1),(0,0),(1,0)],[(0,.52),(.74,.52)]],
    "S": [[(1,1),(.17,1),(0,.81),(.15,.60),(.84,.40),(1,.20),(.80,0),(0,0)]],
    "T": [[(0,1),(1,1)],[(.5,1),(.5,0)]],
}


def record():
    cube("Ribbed base", (0,0,.06),(.70,.52,.12),gunmetal,.036)
    cube("Ceramic post",(0,.025,.53),(.22,.24,.93),warm,.023)
    for z in (.185,.81):
        cube("Steel cuff",(0,.01,z),(.29,.29,.11),gunmetal,.018)
    cube("Plaque enclosure",(0,0,1.10),(1.07,.25,.62),gunmetal,.047)
    cube("Bronze bezel",(0,-.132,1.10),(.97,.052,.53),bezel,.029)
    cube("Dark face",(0,-.16,1.10),(.878,.028,.438),ink,.018)
    for x in (-.425,.425):
        for z in (.905,1.294):
            stud(x,-.163,z)
    for j, letter in enumerate("BEST"):
        for stroke in FONT[letter]:
            path=[(-.176+j*.097+x*.062,1.182+z*.078) for x,z in stroke]
            for a,b in zip(path,path[1:]):
                bar("Porcelain label",a,b,-.177,.012,linen)
    # Empty slot, not a fabricated completion time. Front kept clear for runtime text.
    for x in (-.225,-.103,.103,.225):
        cube("No recorded result cell",(x,-.178,1.052),(.083,.004,.021),neutral)
    for z in (1.028,1.077):
        cube("Separator",(0,-.178,z),(.018,.004,.018),neutral)
    cube("Thin enamel stripe",(0,-.176,.941),(.375,.005,.013),cyan)


def lamp(sealed=False):
    cube("Locating plate",(0,0,.282),(.35,.087,.55),gunmetal,.037)
    cube("Metal brow",(0,-.055,.288),(.30,.10,.43),bezel,.026)
    cube("Ink lens matrix",(0,-.117,.288),(.24,.04,.35),ink,.017)
    for zz in (.096,.479):
        stud(0,-.119,zz,linen)
    mat=amber if sealed else cyan
    for x in (-.091,.091):
        cube("Light bar",(x,-.143,.289),(.015,.006,.16),mat)
    lines=[((-.048,.339),(.048,.239)),((-.048,.239),(.048,.339))] if sealed else [
        ((-.040,.339),(.040,.288)),((.040,.288),(-.040,.239))]
    for a,b in lines:
        bar("State glyph",a,b,-.144,.019,mat)


def make(name, fn):
    start=set(scene.objects)
    fn()
    parts=[o for o in scene.objects if o not in start]
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join()
    o=bpy.context.object
    o.name=o.data.name=name
    scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    f=out/(name+".glb")
    bpy.ops.export_scene.gltf(filepath=str(f),export_format="GLB",
                             use_selection=True,export_animations=False,export_texcoords=False)
    b=f.read_bytes()
    assert struct.unpack_from("<4sII",b)==(b"glTF",2,len(b))
    d=json.loads(b[20:20+struct.unpack_from("<I",b,12)[0]])
    n=sum(d["accessors"][p["indices"]]["count"]//3 for p in d["meshes"][0]["primitives"])
    assert len(b)<65536 and not any(k in d for k in ("images","skins","animations"))
    clear_scene()
    return f, {"bytes":len(b),"triangles":n,"sha256":hashlib.sha256(b).hexdigest()}


parts={
    "record":make("e10b-vault-record-plate",record),
    "open":make("e10b-vault-seal-open",lamp),
    "sealed":make("e10b-vault-seal-closed",lambda:lamp(True)),
}


def import_objects(path, p):
    prev=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objs=[o for o in scene.objects if o not in prev]
    for o in objs:
        if o.parent not in objs:o.location+=Vector(p)
    bpy.context.view_layer.update()
    return [o for o in objs if o.type=="MESH"]


def bounds(objs):
    vv=[o.matrix_world@Vector(v) for o in objs for v in o.bound_box]
    return [[round(fn(v[i] for v in vv),5) for i in range(3)] for fn in (min,max)]


portal=import_objects(donor,(0,.96,0))
pmin,pmax=bounds(portal)
# Plate is outside the shell footprint; two state samples sit on the mock door-side rail.
plate=import_objects(parts["record"][0],(pmin[0]-.80,-.46,0))
open_=import_objects(parts["open"][0],(pmax[0]+.60,-.30,1.02))
closed=import_objects(parts["sealed"][0],(pmax[0]+1.06,-.30,1.02))
a,b=bounds(plate)
assert abs(a[2])<.0001 and pmin[0]-b[0]>.22
a,b=bounds(open_); c,d=bounds(closed)
assert c[0]-b[0]>.10
assert [round(b[i]-a[i],4) for i in range(3)]==[round(d[i]-c[i],4) for i in range(3)]
assert bounds(portal)==[pmin,pmax]
receipt={
    "scope":"E10b visual fixtures only; no time tracking, seals, checkpoint, interaction or collision",
    "donor":donor.name,"donor_sha256":hashlib.sha256(donor.read_bytes()).hexdigest(),
    "portal_scale_unchanged":True, "plate_shell_separation_m":round(pmin[0]-bounds(plate)[1][0],5),
    "state_variant_envelopes_equal":True,
    "files":{k:v[1] for k,v in parts.items()},
}
(out/"e10b-vault-checkpoint-fixtures.json").write_text(json.dumps(receipt,indent=2)+"\n")

if os.getenv("WILDSHARD_VALIDATE_ONLY") != "1":
    stone=shade("Basalt stage",(.052,.072,.078),.03,.83)
    cube("Stage",(0,0,-.15),(200,200,.30),stone)
    cube("Shared fixture sample rail",(pmax[0]+.83,-.16,1.30),(.97,.19,.71),gunmetal,.035)
    cube("Rail foot",(pmax[0]+.83,-.11,.07),(.80,.58,.14),warm,.028)
    cube("Rail leg",(pmax[0]+.83,-.08,.56),(.17,.25,1.03),gunmetal,.018)
    scene.world=bpy.data.worlds.new("Vault studio")
    scene.world.color=(.13,.19,.25)

    def aim(o,target):
        o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()

    for name,pos,to,power,size,c in [
        ("Entrance amber",(-4,-4,5),(-1,0,1.35),920,3.6,(1,.73,.49)),
        ("Portal slate",(5,-3.8,5.5),(1,0,1.15),1250,4.7,(.56,.78,1)),
        ("Wall wash",(-.8,3,6.3),(0,0,1.45),1780,3.6,(.36,.66,1)),
    ]:
        l=bpy.data.lights.new(name,"AREA");l.energy,l.size,l.color=power,size,c
        o=bpy.data.objects.new(name,l);scene.collection.objects.link(o);o.location=pos;aim(o,to)
    c=bpy.data.cameras.new("Vault fixture review")
    camera=bpy.data.objects.new(c.name,c)
    scene.collection.objects.link(camera);scene.camera=camera;c.type="ORTHO"
    scene.render.engine="CYCLES";scene.cycles.samples=40;scene.cycles.use_denoising=False
    scene.view_settings.view_transform="AgX"
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=91
    mid=(pmin[0]+pmax[0])*.5 +.16
    for name,pos,to,scale,w,h in [
        ("approach",(mid+3.15,-15,6.2),(mid,.42,1.65),pmax[0]-pmin[0]+3.40,1430,1000),
        ("states",(pmax[0]+1.25,-3.8,2.02),(pmax[0]+.83,-.30,1.30),1.42,1170,850),
    ]:
        camera.location=pos;aim(camera,to);c.ortho_scale=scale
        scene.render.resolution_x,scene.render.resolution_y=w,h
        scene.render.filepath=str(out/("nov24-e10b-vault-"+name+".jpg"))
        bpy.ops.render.render(write_still=True)

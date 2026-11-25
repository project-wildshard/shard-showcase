"""Portable W10a fence-line foliage and exact archive-chute fit. Blender 4.3+."""
import hashlib
import json
import math
import os
from pathlib import Path
import random
import runpy
import struct
import sys

import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import clear_scene, export, output_directory

out = output_directory()
verify_only = os.environ.get("WILDSHARD_VALIDATE_ONLY")
rng = random.Random(50326)
clear_scene()


def mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    m.use_backface_culling = False
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = .86
    return m


class Plant:
    def __init__(self, name, colors):
        self.name = name
        self.mats = [mat(n,c) for n,c in colors]
        self.v, self.f, self.ids = [], [], []

    def add(self, vs, fs, m):
        i = len(self.v)
        self.v.extend(vs)
        self.f.extend(tuple(i+j for j in f) for f in fs)
        self.ids.extend([m]*len(fs))

    def blade(self, a, d, l, h, w, m, drop=0):
        cross = Vector((-d.y,d.x,0))
        b = a + d*l*.31 + Vector((0,0,h*.56))
        c = a + d*l*.71 + Vector((0,0,h))
        tip = a + d*l + Vector((0,0,h-drop))
        self.add([a-cross*w*.28,a+cross*w*.28,b-cross*w,b+cross*w,c-cross*w*.53,
                  c+cross*w*.53,tip,b-d*.013+Vector((0,0,.012))],
                 [(0,1,7),(0,7,2),(1,3,7),(2,7,4),(3,5,7),(7,5,4),(4,5,6)],m)

    def stem(self, a, b, r0, r1, m):
        d = (b-a).normalized()
        u = d.cross(Vector((1,0,0))).normalized()
        v = d.cross(u)
        dirs = [u*math.cos(k*math.tau/4)+v*math.sin(k*math.tau/4) for k in range(4)]
        self.add([a+w*r0 for w in dirs]+[b+w*r1 for w in dirs],
                 [(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)],m)

    def object(self):
        d = bpy.data.meshes.new(self.name)
        d.from_pydata(self.v, [], self.f)
        d.update()
        assert not d.validate() and all(p.area > 1e-9 for p in d.polygons)
        for m in self.mats: d.materials.append(m)
        for p,m in zip(d.polygons,self.ids): p.material_index=m
        ob = bpy.data.objects.new(self.name,d)
        bpy.context.collection.objects.link(ob)
        return ob


stubble = Plant("Pressed meadow bunch", [
    ("Stubble • wet olive",(.090,.112,.031)), ("Stubble • green undershoot",(.149,.205,.045)),
    ("Stubble • gold tips",(.353,.294,.083)),
])
for i in range(43):
    yaw = i * 2.39996 + rng.uniform(-.33,.33)
    d = Vector((math.cos(yaw),math.sin(yaw),0))
    a = d*rng.uniform(.006,.11)
    height = rng.uniform(.090,.314)
    reach = rng.uniform(.14,.45)
    stubble.blade(a,d,reach,height,rng.uniform(.008,.021),
                  (0 if i%3==0 else 1) if i%6!=0 else 2,height*rng.uniform(.19,.69))

heads = Plant("Weathered roadside teasel", [
    ("Teasel • lacquer olive",(.204,.216,.071)), ("Teasel • leaf velvet",(.10,.169,.071)),
    ("Teasel • dark seed core",(.244,.126,.036)), ("Teasel • sunlit hooks",(.57,.32,.086)),
])
for i in range(6):
    yaw = i*2.39996
    direction = Vector((math.cos(yaw),math.sin(yaw),0))
    a = direction*.022
    h = rng.uniform(.49,.79)
    middle = direction*rng.uniform(.058,.119)+Vector((0,0,h*.56))
    top = direction*rng.uniform(.10,.19)+Vector((0,0,h))
    heads.stem(a,middle,.012,.008,0)
    heads.stem(middle,top,.008,.0045,0)
    for j in range(3):
        az = yaw+j*2.39996
        w = Vector((math.cos(az),math.sin(az),0))
        heads.blade(a.lerp(middle,.17+j*.31),w,.125+j*.014,.11,.022,1,.050)
    ring = [Vector((math.cos(k*math.tau/8),math.sin(k*math.tau/8),0)) for k in range(8)]
    heads.add([top+d*r+Vector((0,0,z)) for z,r in ((0,.013),(.035,.033),(.077,.029),(.114,.009)) for d in ring],
              [(q+k,q+(k+1)%8,q+(k+1)%8+8,q+k+8) for q in (0,8,16) for k in range(8)]
              + [tuple(range(24,32))],2)
    for q in range(4):
        for k,d in enumerate(ring):
            direction = d if q%2==0 else (d+ring[(k+1)%8]).normalized()
            s = Vector((-direction.y,direction.x,0))
            z = .017 + q*.024
            p = top+direction*(.027 if q<3 else .021)+Vector((0,0,z))
            tip = p+direction*.024+Vector((0,0,.016+.003*(k%3)))
            heads.add([p-s*.006,p+s*.006,p.lerp(tip,.64)+Vector((0,0,.006)),tip],[(0,1,2),(2,1,3),(2,3,0)],3)

metrics = {}
sources = {}
for key,plant,tri_limit in (("stubble",stubble,350),("teasel",heads,1200)):
    obj = plant.object()
    p = out/f"w10a-verge-{key}.glb"
    export([obj],p)
    raw = p.read_bytes()
    doc = json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
    prim = [n for mesh in doc["meshes"] for n in mesh["primitives"]]
    tris = sum(doc["accessors"][n["indices"]]["count"]//3 for n in prim)
    assert 0 < tris <= tri_limit and len(prim)==len(plant.mats) and len(raw)<90000
    assert all(doc["materials"][i]["doubleSided"] for i in range(len(plant.mats)))
    assert not any(k in doc for k in ("images","skins","animations","cameras"))
    metrics[key]={"bytes":len(raw),"triangles":tris,"draws":len(prim),"sha256":hashlib.sha256(raw).hexdigest()}
    sources[key]=p

# Existing geometry, lighting direction, fence layout and sign model. Skip old renders.
os.environ["WILDSHARD_VALIDATE_ONLY"]="1"
base = runpy.run_path(str(HERE/"paddock_chute.py"))
if verify_only is None:
    del os.environ["WILDSHARD_VALIDATE_ONLY"]
scene = bpy.context.scene
for ob in list(scene.objects):
    if ob.name.startswith("Meadow grass stubble"):
        bpy.data.objects.remove(ob,do_unlink=True)
for k,p in sources.items():
    base["templates"][k] = base["load"](p)

# Keep new foliage out of the 12 m chute as well as the post and sign mesh
# envelopes. Show placement positions in world metres so the fit is reproducible.
rng = random.Random(280285)
placed=[]
mesh_points=[]
for side in (-1,1):
    for i in range(16):
        y=.5+i*.855+rng.uniform(-.14,.14)
        x=side*(6.70+rng.uniform(.015,.52))
        placed.append(("stubble",x,y,rng.uniform(-math.pi,math.pi),rng.uniform(.72,1.14)))
    for i in range(7):
        y=.95+i*1.98+rng.uniform(-.19,.19)
        x=side*(7.36+rng.uniform(.015,.61))
        placed.append(("teasel",x,y,rng.uniform(-math.pi,math.pi),rng.uniform(.81,1.09)))

count={}
for key,x,y,yaw,scale in placed:
    count[key]=count.get(key,0)+1
    T=Matrix.Translation((x,y,-.015))@Matrix.Rotation(yaw,4,"Z")@Matrix.Scale(scale,4)
    for mesh,mo in base["templates"][key]:
        ob=bpy.data.objects.new(key.capitalize()+" | shared imported mesh",mesh)
        scene.collection.objects.link(ob)
        ob.matrix_world=T@mo
        mesh_points += [ob.matrix_world@v.co for v in mesh.vertices]
bpy.context.view_layer.update()
min_lane=min(abs(v.x)-6 for v in mesh_points)
fence_outer=max(abs((o.matrix_world@v.co).x) for o in base["rail_groups"] for v in o.data.vertices)
min_fence=min(abs(v.x)-fence_outer for v in mesh_points)
sign_front=max((o.matrix_world@v.co).y for o in base["signs"] for v in o.data.vertices)
min_sign=min(v.y-sign_front for v in mesh_points)
z_min,z_max=min(v.z for v in mesh_points),max(v.z for v in mesh_points)
assert count=={"stubble":32,"teasel":14} and min_lane>.21 and min_fence>.045 and min_sign>.29,(count,min_lane,min_fence,min_sign)
assert -.019<=z_min<-.015 and .60<z_max<1.05,(z_min,z_max)

cam=base["cam"]
scene.render.resolution_x,scene.render.resolution_y=1440,900
scene.cycles.samples=36
for tag,eye,target,lens in (
    ("chute",(-4.15,-3.5,2.32),(-.35,10.4,.56),28),
    ("detail",(-6.36,1.3,.78),(-7.45,3.44,.25),40),
):
    cam.location=eye
    cam.data.lens=lens
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath=str(out/f"nov25-w10a-verge-{tag}.jpg")
    if not verify_only: bpy.ops.render.render(write_still=True)

receipt={
    "scope":"Reusable foliage and placement study; no native additions, colliders, LOD or wind shader.",
    "reference_receipt":"project/journal/2026-11-24-w10a-paddock-chute.md",
    "threshold_three_xz_m":[-40,-132],
    "exports":metrics,
    "sampled_reimported_vertices":len(mesh_points),
    "min_lateral_margin_from_lane_m":round(min_lane,4),
    "min_lateral_margin_from_fence_geometry_m":round(min_fence,4),
    "min_forward_margin_from_sign_geometry_m":round(min_sign,4),
    "height_range_m":[round(z_min,4),round(z_max,4)],
    "placements":[{"prototype":k,"world_three_xyz_m":[round(x-40,6),-.015,round(-132-y,6)],
                   "yaw_radians":round(yaw,6),"scale":round(s,6)} for k,x,y,yaw,s in placed],
}
(out/"w10a-chute-verge-proof.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps({k:v for k,v in receipt.items() if k!="placements"},indent=2))

"""W01 compass medallion and M07 paired paving ribbons, built over the verified W0b donor."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import export


def parse():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--town", required=True, type=Path, help="whole-town-WIP.glb from west-town/build.py")
    p.add_argument("--output", required=True, type=Path)
    return p.parse_args(sys.argv[sys.argv.index("--") + 1:])


args = parse()
out = args.output.resolve()
repo = Path(__file__).resolve().parents[3]
assert out != repo and repo not in out.parents
out.mkdir(parents=True, exist_ok=True)
for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(args.town))
scene = bpy.context.scene
scale = math.pi / 180


def donor_bvh():
    vs, fs, hosts = [], [], []
    for ob in scene.objects:
        if ob.type != "MESH":
            continue
        bounds = [ob.matrix_world @ Vector(p) for p in ob.bound_box]
        if (max(p.x for p in bounds) < -29 or min(p.x for p in bounds) > -8 or
            max(p.y for p in bounds) < -6 or min(p.y for p in bounds) > 4):
            continue
        i = len(vs)
        vs.extend(ob.matrix_world @ v.co for v in ob.data.vertices)
        fs.extend(tuple(i+j for j in f.vertices) for f in ob.data.polygons)
        hosts.extend([ob.name]*len(ob.data.polygons))
    return BVHTree.FromPolygons(vs,fs), hosts


def sample(bvh, hosts, x, y):
    p,n,i,_ = bvh.ray_cast(Vector((x,y,4.0)),Vector((0,0,-1)),4.1)
    assert p is not None and n.z > .98, (x,y,p,n,i)
    return p.z, hosts[i]


def check_sites():
    # Sample the underlying slab plus the inherited raised grid. Check taller obstructions too.
    # Bottom faces can intersect the slab; top faces must not coincide with any donor surface.
    results = {}
    bvh, hosts = donor_bvh()
    for label, coords, expected, top in [
        ("W01 plaza medallion", [(X*.10-26, Y*.10-3) for X in range(-24,25) for Y in range(-24,25)
                                 if X*X+Y*Y <= 24*24], (.089,.101), .105),
        ("M07 ribbon on plaza", [(x/100,y+dy/100) for x in range(-2350,-1600,5) for y in (-2.65,2.65)
                                 for dy in [*range(-39,40,4),39]], (.089,.101), .104),
        ("M07 ribbon on apron", [(x/100,y+dy/100) for x in range(-1595,-850,5) for y in (-2.65,2.65)
                                 for dy in [*range(-39,40,4),39]], (.081,.083), .095),
    ]:
        heights = []
        for x,y in coords:
            z, ob = sample(bvh,hosts,x,y)
            heights.append(z)
            assert "source ground plane" in ob, (label,x,y,z,ob)
        lo,hi = min(heights),max(heights)
        assert expected[0] < lo <= hi < expected[1] and .002 < top-hi < .016, (label,lo,hi,top)
        results[label] = {"samples":len(coords),"min_m":round(lo,6),"max_m":round(hi,6),"top_m":top,"clearance_m":round(top-hi,6)}
    return results


surface = check_sites()


def material(name, linear):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*linear, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*linear,1)
    bs.inputs["Roughness"].default_value = .81
    return m


materials = [material("Town tessera | "+n, c) for n,c in [
    ("clay blush",(.42,.14,.073)), ("fired terracotta",(.31,.08,.041)),
    ("oxide red",(.20,.049,.026)), ("limestone",(.59,.436,.255)),
    ("sandstone",(.47,.337,.197)), ("dark mortar",(.173,.115,.077)),
    ("blue slate",(.13,.219,.209)), ("ochre vein",(.53,.292,.118)),
]]
rng = random.Random(20261124)


class Stones:
    def __init__(self):
        self.v, self.f, self.m = [], [], []

    def flat(self, poly, z, index, skirt=0):
        n, i = len(poly), len(self.v)
        self.v.extend((x,y,z) for x,y in poly)
        self.f.append(tuple(range(i,i+n)))
        self.m.append(index)
        if skirt:
            self.v.extend((x,y,z-skirt) for x,y in poly)
            self.f.extend((i+j,i+j+n,i+(j+1)%n+n,i+(j+1)%n) for j in range(n))
            self.m.extend([index]*n)

    def object(self, label):
        mesh = bpy.data.meshes.new(label)
        mesh.from_pydata(self.v,[],self.f)
        mesh.update()
        assert not mesh.validate()
        for material in materials:
            mesh.materials.append(material)
        for p,i in zip(mesh.polygons,self.m):
            assert p.area > 1e-6
            p.material_index=i
        ob = bpy.data.objects.new(label,mesh)
        scene.collection.objects.link(ob)
        return ob


def polar(r,a):
    return (r*math.cos(a),r*math.sin(a))


def ring(m,r0,r1,n,z,paint,offset=0):
    # All rings align to the same continuous grout disc. No overlaid coplanar polygons.
    for i in range(n):
        a,b = math.tau*i/n+offset, math.tau*(i+1)/n+offset
        k = paint(i)
        angles = [a+.003, (a+b)*.5, b-.003]
        m.flat([polar(r1,t) for t in angles]+[polar(r0,t) for t in reversed(angles)], z, k)


def medallion():
    m = Stones()
    m.flat([polar(2.405,k*math.tau/64) for k in range(64)], -.001,5,.016)
    ring(m,2.21,2.397,32,0,lambda i: (3,4,4,3,7,4,3,4)[i%8])
    ring(m,1.97,2.201,32,0,lambda i: (0,1,1,2,1,0,1,2)[i%8])
    ring(m,1.84,1.962,32,0,lambda i: (7,3,4,3)[i%4])
    ring(m,1.40,1.831,32,0,lambda i: (1,0,0,1,0,1,1,2)[i%8])
    ring(m,.36,1.39,32,-.0004,lambda i: (0,1,0,1,2,1,0,1)[i%8])
    for i in range(8):
        a=i*math.tau/8
        reach=1.68 if i%2==0 else 1.11
        tail=polar(.22,a)
        inner=polar(.55,a)
        tip=polar(reach,a)
        l=polar(.67,a+.325)
        r=polar(.67,a-.325)
        m.flat([tail,r,tip,inner],.001,3 if i%2==0 else 4)
        m.flat([tail,inner,tip,l],.001,7 if i%2==0 else 6)
    m.flat([polar(.35,k*math.tau/16) for k in range(16)], .002,5)
    m.flat([polar(.275,k*math.tau/12) for k in range(12)], .003,6)
    m.flat([polar(.106,k*math.tau/12) for k in range(12)], .004,3)
    return m.object("W01 terracotta compass medallion")


def strip():
    m = Stones()
    m.flat([(0,-.39),(3.75,-.39),(3.75,.39),(0,.39)], -.001,5,.016)
    for j,(y0,y1) in enumerate([(-.387,-.298),(-.292,-.112),(-.105,.105),(.112,.292),(.299,.387)]):
        n = 12 if j in (0,4) else 10
        for i in range(n):
            x0,x1 = 3.75*i/n,3.75*(i+1)/n
            x0+=.005 if i else .002
            x1-=.005 if i+1<n else .002
            chamfer=.013 if j in (0,4) else .022
            color = [rng.choice([3,4,7]),rng.choice([0,1,1,2]),(4,3,7,3,4)[i%5],
                     rng.choice([0,1,1,2]),rng.choice([3,4,7])][j]
            m.flat([(x0+chamfer,y0),(x1-chamfer,y0),(x1,y0+chamfer),
                    (x1,y1-chamfer),(x1-chamfer,y1),(x0+chamfer,y1),
                    (x0,y1-chamfer),(x0,y0+chamfer)], 0,color)
    return m.object("M07 repeatable 3.75m inlaid paving ribbon")


compass, ribbon = medallion(),strip()
for name, ob in [("w0b-plaza-compass-medallion",compass),("w0b-east-gate-paving-ribbon",ribbon)]:
    dest = out/f"{name}.glb"
    export([ob],dest)
    ob.data.calc_loop_triangles()
    print(f"{name}: {dest.stat().st_size} B, {len(ob.data.loop_triangles)} triangles",flush=True)

# Ring body portion sits 5–15 mm above the measured donor before the 4 mm decorative crown.
compass.location = (-26,-3,.105)
ribbon.hide_render = True
placements=[]
for side in [-1,1]:
    for i in range(4):
        x=-23.5+3.75*i
        z=.104 if i<2 else .095
        ob=ribbon.copy()
        scene.collection.objects.link(ob)
        ob.location=(x,side*2.65,z)
        ob.hide_render=False
        placements.append({"x":x,"y":side*2.65,"z":z})
receipt={"donor_sha256":hashlib.sha256(args.town.read_bytes()).hexdigest(),
         "ray_fit":surface,"ribbons":placements,"medallion_center_m":[-26,-3,.105]}
(out/"fit.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt),flush=True)

# These two staged camera views are not native gameplay.
scene.render.engine="CYCLES"
scene.cycles.samples=30
scene.cycles.use_denoising=False
scene.render.resolution_x,scene.render.resolution_y=1410,900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG"
scene.render.image_settings.quality=92
scene.world.use_nodes=True
background=scene.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value=(.27,.42,.63,1)
background.inputs["Strength"].default_value=.48
scene.view_settings.view_transform="AgX"
bpy.ops.object.light_add(type="SUN",rotation=(.39,-.86,-.36))
sun=bpy.context.object
sun.data.energy=3.1
sun.data.angle=scale*8
sun.data.color=(1.0,.865,.71)
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
for name,loc,target,lens in [
    ("medallion",(-19,-.8,4.6),(-31,-1.1,1.95),32),
    ("ribbons",(-23.3,-.8,4.1),(-10,0,2.30),32),
]:
    cam.location=loc
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.lens=lens
    cam.data.clip_end=250
    scene.render.filepath=str(out/f"{name}.jpg")
    bpy.ops.render.render(write_still=True)

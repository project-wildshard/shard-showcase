"""Build the W8b south route as a compact overlay; never modify the donor."""
import argparse
import json
import math
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

p = argparse.ArgumentParser()
p.add_argument("base", type=Path, help="climb-rock-editable.blend from west-climb-rock")
p.add_argument("out", type=Path)
p.add_argument("--render", action="store_true")
args = p.parse_args(sys.argv[sys.argv.index("--") + 1:])
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(args.base.resolve()))
scene = bpy.context.scene
donor = bpy.data.objects["CLIMB | crag mesh 44m zone / crown 16m"]
combined = bpy.data.objects["CLIMB | north chimney and exterior ladder"]

# Match the seven disconnected massing blocks by exact source coordinates.
# They are combined with the cave fins and north ladder in the evaluated donor.
# Remove those placeholders only from our review copy, not the archived source.
expected = [( -216 + i % 2 * 2, -72 + i * 2.6, 1 + .726 * (i + 1) * 2.2 / 1.6) for i in range(7)]
import bmesh
mesh = bmesh.new()
mesh.from_mesh(combined.data)
vertices = [v for v in mesh.verts if any(
    abs(abs(v.co.x-x)-1.95) < 2e-5 and abs(abs(v.co.y-y)-1.45) < 2e-5
    and min(abs(v.co.z), abs(v.co.z-h)) < 2e-5 for x,y,h in expected)]
assert len(vertices) == 56, len(vertices)
assert len({f for v in vertices for f in v.link_faces}) == 42
bmesh.ops.delete(mesh, geom=vertices, context="VERTS")
mesh.to_mesh(combined.data)
mesh.free()

ring = BVHTree.FromPolygons([donor.matrix_world @ v.co for v in donor.data.vertices],
                           [tuple(f.vertices) for f in donor.data.polygons])
def face_y(x, h):
    result = ring.ray_cast(Vector((x, -91, min(h,15.9997))), Vector((0, 1, 0)), 50)[0]
    assert result is not None, (x, h)
    return result.y

route = bpy.data.collections.new("W8b | South face pitches")
scene.collection.children.link(route)

def material(name, color, roughness=.84):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = roughness
    return m

mats = [material(*v) for v in [
    ("Weathered schist", (.26,.25,.207)),
    ("Burnt iron strata", (.32,.232,.156)),
    ("Frosted seam", (.34,.334,.271)),
    ("Black fracture", (.117,.128,.121)),
    ("Banded yellow broaches", (.59,.279,.062)),
    ("Eroded blue basalt", (.128,.22,.21)),
    ("Pale foot ferrules", (.46,.421,.314)),
    ("Old cedar endgrain", (.29,.145,.061)),
    ("Oiled cedar rise", (.405,.226,.107)),
    ("Blackened steel", (.063,.092,.085), .53),
    ("Muted ochre crest", (.49,.266,.08)),
]]
rng = random.Random(82503)

class Geometry:
    def __init__(self):
        self.v, self.f, self.m = [], [], []
    def add(self, points, faces, m):
        n = len(self.v)
        self.v.extend(points)
        self.f.extend(tuple(n+i for i in f) for f in faces)
        self.m.extend([m]*len(faces))
    def prism(self, quad, back, material_index):
        self.add([*quad, *back], [(0,1,2,3),(7,6,5,4),(0,4,5,1),
                                (1,5,6,2),(2,6,7,3),(3,7,4,0)], material_index)
    def box(self, xyz, size, m):
        x,y,z = xyz
        a,b,c = (v/2 for v in size)
        q = [(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
        self.prism(q, [(u,v,w-2*c) for u,v,w in q], m)
    def link(self, name):
        data = bpy.data.meshes.new(name)
        data.from_pydata(self.v, [], self.f)
        for m in mats:
            data.materials.append(m)
        for f,m in zip(data.polygons,self.m):
            f.material_index = m
        data.validate()
        data.update()
        obj = bpy.data.objects.new(name, data)
        route.objects.link(obj)
        return obj

V = Vector
pitches = [
    (V((-216,-72.30,.06)), V((-216,-69.05,5.35))),
    (V((-216,-67.41,5.35)), V((-214.5,-65.16,10.75))),
    (V((-214.5,-63.35,10.75)), V((-212.6,-60.30,16.00))),
]
parts, receipt = [], []
width = 1.88
for index, (toe, lip) in enumerate(pitches):
    travel = lip-toe
    planar = V((travel.x, travel.y, 0))
    side = V((planar.y,-planar.x,0)).normalized()
    outwards = side.cross(travel).normalized()
    assert outwards.y < 0 and outwards.z > 0
    sample_points = [toe + t/80*travel + (u/10-.5)*width*side
                     for t in range(81) for u in range(11)]
    gaps = [face_y(s.x,s.z)-s.y for s in sample_points]
    assert min(gaps) > .09, (index,min(gaps))
    skin = Geometry()
    # Strata face stitches visual interruptions flush to the real planar climb
    # surface. Embedded back surface seats past the surveyed crag side.
    stops = (0,.092,.206,.314,.453,.54,.686,.786,.906,1)
    for j,(a,b) in enumerate(zip(stops,stops[1:])):
        lo, hi = toe+travel*a, toe+travel*b
        q = [lo-side*width/2, lo+side*width/2, hi+side*width/2, hi-side*width/2]
        backing = [V((s.x,face_y(s.x,s.z)+.51,s.z)) for s in q]
        skin.prism(q,backing,(1,0,2,0,1,0,2,0,1)[j])
    parts.append(skin.link(f"Pitch {index+1} | planar schist and embedded backing"))
    holds = Geometry()
    for k in range(11):
        for lane in (-1,1):
            t = .066 + k*.081 + .018*(lane>0)
            center = toe + travel*t + side*(lane*.36 + rng.uniform(-.115,.115))
            s = rng.uniform(.118,.204)
            grip = rng.uniform(.068,.123)
            base, tip = [], []
            for n in range(7):
                v = n*math.tau/7 + .37*k
                radial = side*(math.cos(v)*s) + travel.normalized()*(math.sin(v)*s*.7)
                base.append(center + radial - outwards*.009)
                tip.append(center + radial*.69 + outwards*grip)
            fs = [tuple(range(6,-1,-1)), tuple(range(7,14))]
            fs.extend((i,(i+1)%7,7+(i+1)%7,7+i) for i in range(7))
            holds.add([*base,*tip],fs,4 if k in (1,4,7,10) and lane==-1 else (5 if lane>0 and k%3==0 else 6))
    parts.append(holds.link(f"Pitch {index+1} | 22 climb grips"))
    receipt.append({"pitch":index+1, "toe_three":[round(v,3) for v in (toe.x,toe.z,-toe.y)],
        "lip_three":[round(v,3) for v in (lip.x,lip.z,-lip.y)],"plane_width_m":width,
        "angle_deg":round(math.degrees(math.atan2(travel.z, planar.length)),3),
        "minimum_shell_clearance_m":round(min(gaps),4), "samples":len(gaps)})

# Fit planks to the rotated cross-sections rather than cutting a straight
# seam across the diagonal pitches. The exit sill overlaps the stock crown.
rests = Geometry()
rest_proof=[]
deck_samples=[]
def edge_at(pitch, endpoint, x):
    a,b = pitches[pitch]
    origin = pitches[pitch][endpoint]
    return origin.y-(x-origin.x)*(b.x-a.x)/(b.y-a.y)

for i,(lip, end) in enumerate([(pitches[0][1],pitches[1][0]),
                              (pitches[1][1],pitches[2][0]),
                              (pitches[2][1],V((-212.6,-55.8,16))) ]):
    x = lip.x
    floor = lip.z + (.038 if i==2 else .018)
    front = lambda u: edge_at(i,1,u)-.035
    back = lambda u: edge_at(i+1,0,u)+.045 if i<2 else end.y
    steps = math.ceil((back(x)-front(x))/.21)
    boundary=lambda u,t: front(u)*(1-t)+back(u)*t
    for j in range(steps):
        u,v=x-1.37,x+1.37
        f,g=j/steps,(j+1)/steps
        q=[(u,boundary(u,f)+.003,floor),(v,boundary(v,f)+.003,floor),
           (v,boundary(v,g)-.003,floor),(u,boundary(u,g)-.003,floor)]
        rests.prism(q,[(x1,y1,z1-.122) for x1,y1,z1 in q],8 if j%4==0 else 7)
        for u in [x-.55,x,x+.55]:
            deck_samples.append((u,boundary(u,(f+g)/2),floor))
    for d in (-1,1):
        u=x+d*1.23
        a,b=front(u),back(u)
        assert b-a>.50
        rests.box((u,(a+b)/2,floor-.202),(.13,b-a,.18),9)
        for y in (a+.27,b-.28):
            rests.box((u,y,floor+.28),(.095,.095,.56),9)
            rests.box((u,y,floor+.535),(.106,.106,.08),10)
    ycenter=front(x)+.40
    q=[(x-1.22,ycenter,floor-.20),(x+1.22,ycenter,floor-.20),
       (x+.76,ycenter+.34,floor-1.20),(x-.76,ycenter+.34,floor-1.20)]
    rests.prism(q,[(u,max(v+.22,face_y(u,w)+.42),w) for u,v,w in q],3)

    ranges = [
        face_y(u,lip.z+h)-boundary(u,t/11)
        for t in range(1,11) for u in [x-.55,x,x+.55]
        for h in [.13,.45,.82,1.29,1.86]
    ] if i<2 else []
    if ranges:
        assert min(ranges)>.13, (i,min(ranges))
    else:
        for u in [x-.55,x,x+.55]:
            floor_hit=ring.ray_cast(V((u,end.y,17)),V((0,0,-1)),2)[0]
            assert floor_hit is not None and abs(floor_hit.z-16)<1e-6

    rest_proof.append({"walking_height_m":round(floor,3),
        "verified_lane_width_m":1.10,"center_run_m":round(end.y-lip.y,3),
        "minimum_run_across_verified_lane_m":round(min(back(u)-front(u) for u in [x-.55,x+.55]),3),
        "minimum_core_clearance_m":round(min(ranges),4) if ranges else None,
        "summit_top_matches_m":16 if i==2 else None,"core_samples":len(ranges),
        "deck_samples":steps*3})
parts.append(rests.link("South route | two cedar rest ledges and summit sill"))

bpy.ops.object.select_all(action="DESELECT")
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
file=out/"w8b-rock-three-pitches.glb"
bpy.ops.export_scene.gltf(filepath=str(file),export_format="GLB",
                          use_selection=True,export_animations=False)
raw=file.read_bytes()
n=struct.unpack_from("<I",raw,12)[0]
doc=json.loads(raw[20:20+n])
assert len(doc["nodes"])==7 and not doc.get("animations")
tris=sum(doc["accessors"][v["indices"]]["count"]//3 for m in doc["meshes"] for v in m["primitives"])
assert len(raw)<300000 and tris<5000
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(file))
after=set(scene.objects)-before
assert sum(len(o.data.polygons) for o in after if o.type=="MESH")==tris
deck=next(o for o in after if o.type=="MESH" and "two cedar rest ledges" in o.name)
# Reimport vertices include glTF axis conversion: ensure exported seating
# did not move or rotate floor samples relative to the 16 m donor.
bpy.context.view_layer.update()
tree = BVHTree.FromPolygons([deck.matrix_world @ v.co for v in deck.data.vertices],
                           [tuple(f.vertices) for f in deck.data.polygons])
for x,y,h in deck_samples:
    hit=tree.ray_cast(V((x,y,h+.1)),V((0,0,-1)),.2)[0]
    assert hit is not None and abs(hit.z-h)<.0001, (x,y,h,hit)
for o in after:
    bpy.data.objects.remove(o,do_unlink=True)
(out/"receipt.json").write_text(json.dumps({"pitches":receipt,"rests":rest_proof,
    "archived_massing_removed_from_review_copy":7,"nodes":7,"triangles":tris,
    "bytes":len(raw),"limitations":"Static art. Archived baseline is unchanged. No climb motor, collision, mantle or playable route."},indent=2)+"\n")
if args.render:
    render=Path(__file__).with_name("render.py")
    exec(compile(render.read_text(),str(render),"exec"))
print("ROCK THREE-PITCH FIT PASS", tris, len(raw), flush=True)

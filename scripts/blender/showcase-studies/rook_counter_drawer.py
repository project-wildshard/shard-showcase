"""A removable shallow parts drawer at the front of Rook's established bench."""
import hashlib
import json
import math
import os
from pathlib import Path
import runpy
import sys

import bpy
from mathutils import Matrix, Vector

here = Path(__file__).resolve().parent
out = Path(sys.argv[-1]).resolve()
render = os.environ.get("WSC_METADATA_ONLY") != "1"
os.environ["WSC_METADATA_ONLY"] = "1"
forge = runpy.run_path(str(here / "rook_forge_fixtures.py"))
base = forge["base"]
repo = here.parents[2]
old = json.loads((repo / "project/layouts/w2b-rook-forge-fit.json").read_text())
assert json.loads((out / "w2b-rook-forge-fit.json").read_text()) == old

# Use the existing material and baked-mesh tooling, not another kit.
box, pin, artifact = (forge[k] for k in ("box", "pin", "artifact"))
wood, nest, brass, steel, iron = (forge[k] for k in ("wood", "nest", "brass", "steel", "iron"))
key = "w2b-rook-counter-drawer"
box("Walnut drawer bottom", (0,0,.012), (.364,.114,.024), wood, .006)
box("Oilcloth bed", (0,0,.0255), (.344,.093,.004), nest, 0)
for y in (-.051,.051):
    box("Framed long edge", (0,y,.032), (.354,.010,.033), wood, .003)
for x in (-.177,.177):
    box("Short end cheek", (x,0,.032), (.010,.108,.032), wood, .003)
    pin("Small bronze fixing", (x,0,.0485), .004, .002, brass)
for x in (-.109,.020,.125):
    box("Drawer stock separator", (x,0,.029), (.004,.090,.011), wood, 0)
for x,y,z,r,m in ((-.148,-.018,.037,.018,steel),(-.137,.021,.035,.014,iron),
                  (-.068,-.009,.039,.023,brass),(-.022,.018,.035,.013,steel),
                  (.061,.018,.038,.019,iron),(.088,-.020,.036,.013,brass),
                  (.152,-.009,.037,.013,steel)):
    # Indented, two-tone workshop samples, not functional hardware.
    pin("Oiled machine spacer", (x,y,z), r, 2*(z-.0275), m)
    pin("Dark inset", (x,y,2*z-.0275+.0005), r*.43, .001, nest)
box("Flush pull escutcheon", (0,-.057,.03), (.074,.004,.012), brass, .002)
box("Dark pull", (0,-.059,.03), (.048,.002,.005), iron, 0)
glb, meta = artifact(key, 1200)

# Check all approach-facing footprint samples against the actual counter cloth.
bvh = forge["bvh"]
transform = forge["counter_t"]
x,y = .650,-1.223
original = [.42,.88,-1.148,-.892]
heights = []
for ix in range(17):
    for iy in range(9):
        p = Vector((x+(ix/16-.5)*.364, y+(iy/8-.5)*.120,1.78))
        hit, normal, *_ = bvh.ray_cast(p,Vector((0,0,-1)),.96)
        assert hit is not None and normal.z > .985, (ix,iy,hit,normal)
        heights.append(hit.z)
assert max(heights)-min(heights)<.001 and 1.027<min(heights)<1.032
where = transform @ Matrix.Translation((x,y,max(heights)+.0005))
obs = base["imported"](glb)
for ob in obs:
    if ob.parent not in obs:
        ob.matrix_world = where @ ob.matrix_world
bpy.context.view_layer.update()
inverse = transform.inverted()
pts = [inverse @ ob.matrix_world @ v.co for ob in obs if ob.type == "MESH" for v in ob.data.vertices]
extent = [(min(v[i] for v in pts),max(v[i] for v in pts)) for i in range(3)]
gap = original[2]-extent[1][1]
edge = extent[1][0]+1.313
assert gap>.015 and edge>.02
assert abs(extent[2][0]-where.translation.z)<.001
assert extent[0][0] > .295 and extent[0][1] < 1.065
r = lambda v: round(v,6)
scene = bpy.context.scene
scene.frame_set(19)
scene.cycles.samples = 42
if render:
    del os.environ["WSC_METADATA_ONLY"]
    base["camera"](scene,key+"-context",(.20,-6.25,1.85),(.62,-1.48,1.40),(1440,900),lens=36)
    base["camera"](scene,key+"-detail",(1.78,-2.87,1.90),(1.93,-1.76,1.10),(1200,880),lens=64)

(out / (key+"-proof.json")).write_text(json.dumps(dict(
    scope="Removable decorative counter stock. No ammo pickup, crafting, purchases or collision.",
    catalogue_id="WSC-SCENE-002",
    counter_sha256=old["counter_sha256"],
    actor_sha256=old["actor_sha256"],
    prior_fixture_hashes={k:v["sha256"] for k,v in old["exports"].items()},
    drawer=meta,
    raw_counter_xz=[x,-y],
    proposed_placement_blender=[r(v) for v in where.translation],
    yaw_degrees=-7,
    footprint_ray_samples=len(heights),
    counter_contact_height_m=[r(min(heights)),r(max(heights))],
    local_footprint_m=[[r(v) for v in row] for row in extent[:2]],
    bench_stand_gap_m=r(gap),
    front_edge_margin_m=r(edge),
),indent=2)+"\n")

"""Build the proposed last-door handoff from the source rooms, not exported scenes."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
RECIPES = ROOT / "scripts/blender/showcase-studies"
ASSETS = ROOT / "public/assets/wildshard-art"
OUT = Path(sys.argv[-1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
os.environ["WSC_METADATA_ONLY"] = "1"
os.environ["WILDSHARD_VALIDATE_ONLY"] = "1"
os.environ["WSC_VAULT_FINAL_DOOR"] = "1"
os.environ.pop("WSC_VAULT_SWEEP", None)
# Read Room 3 first; its builder clears the current scene. Preserve mesh data and
# materials explicitly, then reconstruct only the authored last-door landing.
try:
    runpy.run_path(str(RECIPES/"vault_climb_room.py"))
except SystemExit as exc:
    if exc.code not in (None, 0):
        raise
room3 = [(o.name, o.data.copy(), o.matrix_world.copy()) for o in bpy.context.scene.objects
         if o.type == "MESH" and o.name.startswith(
             ("Last-door landing", "Last-door tread", "05 last door / static bulkhead",
              "Static final door jamb", "Last-door apron", "Upper landing"))]
assert any(n.startswith("Last-door landing") for n,_,_ in room3)
assert any(n.startswith("05 last door / static bulkhead") for n,_,_ in room3)
room4 = runpy.run_path(str(RECIPES/"vault_lockdown_room.py"))
scene = bpy.context.scene
box, mat = room4["box"], room4["mat"]
shift = Vector((21.5, -20.4, 9.5))
bpy.context.view_layer.update()
r4_meshes = [o for o in scene.objects if o.type == "MESH"]
for o in list(scene.objects):
    if o.type in ("MESH","LIGHT"):
        o.location += shift

steel = mat("Handoff · shingled zinc", (.105,.149,.162), .64,.45)
edge = mat("Handoff · cold structural shell", (.046,.071,.082), .50,.55)
copper = mat("Handoff · worn copper guards", (.37,.136,.058), .59,.49)
cyan = mat("Handoff · blue route inset", (.033,.42,.57), .25,.40,1.8)
parts = []
render_hide = []
def use(o,role):
    parts.append((o,role))
    return o

for o in r4_meshes:
    name=o.name
    # Only the sampled center strip needs exact plate collision; full-room art is retained.
    role = ("room4-floor" if name.startswith(("Plate 0,1 |", "Plate 0,2 |", "Plate 0,3 |", "Worn perimeter floor")) else
            "entrance" if name.startswith(("Test mouth", "Test entrance")) else None)
    if role:
        use(o,role)
    if name.startswith("Sealed roof"):
        render_hide.append(o)
for n,data,m in room3:
    o=bpy.data.objects.new(n,data)
    scene.collection.objects.link(o)
    o.matrix_world=m
    if n.startswith("05 last door / static"):
        use(o,"sealed-control").hide_render=True
    else:
        use(o,"room3-landing")

def donor(name,p,yaw,role):
    f=ASSETS/"wsc-module-021-open-circular-vault-door.glb"
    assert hashlib.sha256(f.read_bytes()).hexdigest()=="dcaca9e40d0e6421fdd62c1dedf537e7004ad0016b05144beed419377682cc68"
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(f))
    bpy.context.view_layer.update()
    new=sorted(set(scene.objects)-before,key=lambda o:o.name)
    rot=Matrix.Translation(p) @ Matrix.Rotation(yaw,4,"Z")
    meshes=[(o.name,o.data,o.matrix_world.copy()) for o in new if o.type=="MESH"]
    for o in new:
        bpy.data.objects.remove(o,do_unlink=True)
    for n,data,m in meshes:
        o=bpy.data.objects.new(name+" | "+n,data)
        scene.collection.objects.link(o)
        o.matrix_world=rot@m
        use(o,role)
donor("Existing open final bulkhead",(18,0,8.51),-1.57079632679,"open-final")

def b(name,p,d,m,role=None):
    o=box(name,p,d,m)
    return use(o,role) if role else o

b("Turn · first landing extension",(20.94,0,9.35),(3.80,3.10,.30),steel,"turn-deck")
b("Turn · straight walk to lockdown",(21.50,-4.99,9.35),(3.0,6.90,.30),steel,"throat-deck")
b("Turn · end guard",(22.91,0,10.90),(.26,3.10,2.80),edge,"guard")
b("Turn · outer guard",(21.0,1.63,10.90),(4.10,.22,2.80),edge,"guard")
for x in (19.92,23.08):
    b("Throat · wall",(x,-5.0,10.90),(.18,6.90,2.80),edge,"guard")
    b("Throat · copper hand strip",(x+(.103 if x<21 else -.103),-5,10.35),(.06,6.7,.12),copper)
    for y in (-2.6,-4.6,-6.6):
        b("Throat · recessed lamp",(x+(.108 if x<21 else -.108),y,11.25),(.05,.70,.065),cyan)
for y in (-2.7,-4.6,-6.5):
    b("Throat · directional floor joint",(21.5,y,9.507),(2.32,.025,.009),copper)

def world(v):
    return (186+v.x,-50+v.z,-64-v.y)

bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
rows=[]
for o,role in sorted(parts,key=lambda item:item[0].name):
    ev=o.evaluated_get(deps)
    mesh=ev.to_mesh()
    try:
        mesh.calc_loop_triangles()
        verts=[round(c,6) for v in mesh.vertices for c in world(ev.matrix_world@v.co)]
        ix=[i for t in mesh.loop_triangles for i in t.vertices]
        if ix:
            rows.append(dict(role=role,name=o.name,vertices=verts,triangles=ix))
    finally:
        ev.to_mesh_clear()
room4_points=[world(o.matrix_world@v.co) for o in r4_meshes for v in o.data.vertices]
bounds=[[round(fn(p[i] for p in room4_points),4) for i in range(3)] for fn in (min,max)]
for i,(low,high) in enumerate(((151,221),(-50,-30),(-99,-29))):
    assert low<=bounds[0][i]<=bounds[1][i]<=high, bounds
gap=bounds[0][2]-(-59.15)
assert gap>=2.9, gap
(OUT/"handoff-collision.json").write_text(json.dumps(rows,separators=(",",":"))+"\n")
(OUT/"handoff-layout.json").write_text(json.dumps(dict(room4_art_bounds=bounds,
    room3_room4_gap_z_m=round(gap,4),room4_center=[207.5,-40.5,-43.6],
    final_door=[204,-40.5,-64],room4_door=[207.5,-40.5,-55.61]),indent=2)+"\n")

receipt=OUT/"handoff-walk.json"
if not receipt.exists() or os.environ.get("WSC_HANDOFF_VALIDATE_ONLY") == "1":
    sys.exit(0)
data=json.loads(receipt.read_text())
assert data["collision_sha256"]==hashlib.sha256((OUT/"handoff-collision.json").read_bytes()).hexdigest()
assert all(row["complete"] and row["air"]==0 for row in data["open"])
cam=scene.camera
area=room4["area"]
area("Bend cold soffit",(21.5,-1.1,12.25),(21.5,-2,9.5),450,(.52,.80,1),3)
area("Tunnel warm crosslight",(22.35,-6.2,11.96),(21.3,-5,9.4),260,(1,.58,.28),1.8)
area("Landing blue fill",(15.5,-2.1,12.75),(18,0,9.3),460,(.51,.77,1),3)
scene.cycles.samples=24
scene.cycles.adaptive_threshold=.06
def shoot(name,eye,target,size,ortho=None):
    cam.location=eye
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.type="ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale=ortho
    else:
        cam.data.lens=23
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(OUT/f"{name}.jpg")
    bpy.ops.render.render(write_still=True)

shoot("vault-lockdown-arrival",(21.50,-5.65,11.20),(21.5,-15,10.1),(780,1020))
for o in render_hide:
    o.hide_render=True
points=data["trace"]
curve=bpy.data.curves.new("Recorded capsule feet","CURVE")
curve.dimensions="3D"
curve.bevel_depth=.051
spline=curve.splines.new("POLY")
spline.points.add(len(points)-1)
for sp,(x,y,z) in zip(spline.points,points):
    sp.co=(x-186,-64-z,y+50+.055,1)
curve.materials.append(cyan)
ob=bpy.data.objects.new("Measured route",curve);scene.collection.objects.link(ob)
shoot("vault-lockdown-turn",(23.8,-12.0,32),(20.3,-8.6,9.5),(1160,970),29)

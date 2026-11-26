"""Reimport the exact G2 donor and its optional handoff for physics or renders."""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/"native-gauntlet-through-walk"))
import geometry

args=sys.argv[sys.argv.index("--")+1:]
assets,out=map(Path,args[:2])
candidate=out/"e11c-g2-c3-threshold.glb"
scene=bpy.context.scene
# Reuse exact existing scene assembly and common local origin (55,0,184).
base=out/"original-geometry.json"
geometry.export(assets,base)
old=json.loads(base.read_text())
cap=[g for g in old if g["name"]=="10 G2 exit stub.001" and g["asset"]=="c2-pit"]
assert len(cap)==1 and len(cap[0]["triangles"])==36
pts=list(zip(*(iter(cap[0]["vertices"]),)*3))
assert abs(min(p[0] for p in pts)-109.505)<.001
assert abs(max(p[0] for p in pts)-109.995)<.001

before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(candidate))
new=sorted(set(scene.objects)-before,key=lambda o:o.name)
assert len(new)==5
for o in new:
    if o.parent not in new:
        o.location.x+=55
        o.location.y-=30
bpy.context.view_layer.update()
parts=[]
all_triangles=0
for o in new:
    assert o.type=="MESH"
    verts=[]
    for v in o.data.vertices:
        x,y,z=o.matrix_world@v.co
        verts.extend(round(p,7) for p in (x+55,z,184-y))
    o.data.calc_loop_triangles()
    tris=[i for t in o.data.loop_triangles for i in t.vertices]
    all_triangles+=len(tris)//3
    if not o.name.startswith("90 "):
        parts.append(dict(asset="g2-handoff",name=o.name,vertices=verts,triangles=tris))
payload={"original":old,"extension":parts,"capName":cap[0]["name"]}
(out/"corridor.json").write_text(json.dumps(payload,separators=(",",":"))+"\n")
(out/"g2-export.json").write_text(json.dumps({"bytes":candidate.stat().st_size,"triangles":all_triangles,
    "donor_sha256":geometry.ASSETS[-1][2],"extension_sha256":hashlib.sha256(candidate.read_bytes()).hexdigest(),
    "original_parapet_clearance_m":7.,"old_cap_x_range_m":[109.505,109.995],
    "structural_extension_triangles":sum(len(p["triangles"])//3 for p in parts)},indent=2)+"\n")
if len(args)==2:raise SystemExit(0)

def pos(p):return Vector((p[0]-55,184-p[2],p[1]))
def aim(o,target):o.rotation_euler=(pos(target)-o.location).to_track_quat("-Z","Y").to_euler()
motion=json.loads(Path(args[2]).read_text())
cap_obj=bpy.data.objects.get(cap[0]["name"])
assert cap_obj and tuple(m.name for m in cap_obj.data.materials)==("Blind portal recess",)
cap_obj.hide_render=True
rays=[pos(k["feet"])+Vector((0,0,.14)) for k in motion["samples"][1]["frames"] if k["feet"][0]>91 and k["feet"][2]>193]
path=bpy.data.curves.new("Audit replay","CURVE");path.dimensions="3D";path.bevel_depth=.035;path.bevel_resolution=2
sp=path.splines.new("POLY");sp.points.add(len(rays)-1)
for pt,v in zip(sp.points,rays):pt.co=(*v,1)
o=bpy.data.objects.new(path.name,path);scene.collection.objects.link(o)
mat=bpy.data.materials.new("Audit overlay | cyan, not asset");mat.use_nodes=True
n=mat.node_tree.nodes["Principled BSDF"];n.inputs["Base Color"].default_value=(.02,.8,1,1);n.inputs["Emission Color"].default_value=(.02,.8,1,1);n.inputs["Emission Strength"].default_value=2.3
path.materials.append(mat)
world=bpy.data.worlds.new("Muted dusk sky");world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.20,.29,.41,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.51
scene.world=world
light=bpy.data.lights.new("Low afternoon sun","SUN");light.energy=1.75;light.angle=.14
sun=bpy.data.objects.new("Low afternoon sun",light);scene.collection.objects.link(sun);sun.rotation_euler=(.68,-.32,.52)
cam=bpy.data.cameras.new("G2 review");o=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(o);scene.camera=o
scene.render.engine='CYCLES';scene.cycles.samples=25;scene.cycles.use_denoising=False
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='WEBP';scene.render.image_settings.quality=87
for key,where,target,raster,lens in (
    ("eye",(103,1.7,214),(121,.95,208),(804,1748),34),
    ("overhead",(108,43,253),(115,1,210),(1440,960),34),
):
    o.location=pos(where);aim(o,target);cam.lens=lens
    if key=="eye":cam.sensor_fit="VERTICAL"
    else:cam.sensor_fit="HORIZONTAL"
    scene.render.resolution_x,scene.render.resolution_y=raster
    scene.render.filepath=str(out/f"nov26-g2-c3-{key}.webp")
    bpy.ops.render.render(write_still=True)

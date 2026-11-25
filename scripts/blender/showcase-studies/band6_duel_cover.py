"""Build the original Band 6 tall screen and low return as two reusable meshes."""
import hashlib
import json
import os
from math import pi
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out = output_directory()
clear_scene()
scene = bpy.context.scene


def material(n, c, m=0, r=.51, e=0):
    d = bpy.data.materials.new(n)
    d.use_nodes = True
    d.diffuse_color = (*c, 1)
    p = d.node_tree.nodes["Principled BSDF"]
    for k, x in {"Base Color":(*c,1),"Metallic":m,"Roughness":r,
                 "Emission Color":(*c,1),"Emission Strength":e}.items():
        p.inputs[k].default_value = x
    return d


graphite = material("Folded dark grey steel",(.072,.111,.120),.55)
char = material("Dark ceramic seams",(.033,.050,.057),.23)
steel = material("Machined kick plates",(.201,.243,.251),.73)
rust = material("Band 6 old oxide red",(.44,.118,.040),.35,.62)
copper = material("Copper enamel on shoulders",(.68,.253,.071),.46)
light = material("Blue glass indicators",(.029,.51,.61),.34,.34,.28)
marker = material("Pale stencilled dots",(.79,.67,.42),.09,.68)
orange = material("Low barrier warm orange",(.68,.194,.044),.37)
gasket = material("Low barrier undercut shadow",(.09,.066,.059),.3)
parts = []


def box(n,at,dim,m,b=.012):
    bpy.ops.mesh.primitive_cube_add(size=1,location=at)
    o=bpy.context.object
    o.name=n
    o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if b and min(dim) > .075:
        mod=o.modifiers.new("Pressed shell bevel","BEVEL")
        mod.width=min(b,min(dim)*.21)
        mod.segments=1
        o.modifiers.new("Weighted plate normals","WEIGHTED_NORMAL")
    o.data.materials.append(m)
    parts.append(o)
    return o


def bolt(n,x,y,z,sz):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=sz,depth=.024,
        location=(x,y,z),rotation=(pi/2,0,0))
    q=bpy.context.object
    q.name=n
    q.data.materials.append(steel)
    parts.append(q)


def artifact(name,limit):
    path=out/(name+".glb")
    # Bake visual bevels and consolidate each finish into one draw.
    # The procedural pieces remain separate and editable in this source.
    by_finish={}
    for o in parts:
        by_finish.setdefault(o.data.materials[0].name,[]).append(o)
    reduced=[]
    for key, originals in sorted(by_finish.items()):
        bpy.ops.object.select_all(action="DESELECT")
        for o in originals:
            o.select_set(True)
        bpy.context.view_layer.objects.active=originals[0]
        bpy.ops.object.convert(target="MESH")
        if len(originals)>1:
            bpy.ops.object.join()
        body=bpy.context.object
        body.name=name+" | "+key
        reduced.append(body)
    export(reduced,path)
    raw=path.read_bytes()
    assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
    doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
    primitives=[p for m in doc["meshes"] for p in m["primitives"]]
    tris=sum(doc["accessors"][p["indices"]]["count"]//3 for p in primitives)
    assert len(primitives)==len(by_finish)
    assert tris<=limit and not any(k in doc for k in ("images","skins","animations","cameras"))
    for o in reduced:
        bpy.data.objects.remove(o,do_unlink=True)
    parts.clear()
    return path,{"bytes":len(raw),"triangles":tris,"draws":len(primitives),"sha256":hashlib.sha256(raw).hexdigest()}


# A continuous core stops eye rays through the cosmetic joints. Everything is
# inside the documented footprint; neither artwork grows the barrier.
box("Continuous sight screen backing",(0,0,1.50),(11.98,.48,3),char,.021)
for i in range(6):
    x=(i-2.5)*1.98
    box("Folded steel screen bay",(x,0,1.54),(1.937,.556,2.732),graphite,.044)
    box("Upper seam header",(x,0,2.913),(1.93,.486,.152),rust,.031)
    for s in (-1,1):
        box("Oxide lower kick plate",(x,s*.282,.451),(1.86,.026,.56),rust,.014)
        for q in (-.76,.76):
            bolt("Captive corner bolt",x+q,.284*s,.759,.038)
        for j in range(3):
            box("Deep stamped vent tray",(x-.48+j*.47,s*.280,2.07),(.32,.02,.26),char,.007)
            box("Rib inside vent tray",(x-.48+j*.47,s*.291,2.07),(.249,.016,.064),steel,.005)
for x in (-5.925,-3.96,-1.98,0,1.98,3.96,5.925):
    box("Capped structural rib",(x,0,1.51),(.15,.6,2.95),steel,.017)
    box("Cast footing",(x,0,.118),(.15,.6,.236),graphite,.011)
for s in (-1,1):
    for x in (-5.72,5.72):
        box("Brass corner bumper",(x,s*.276,1.235),(.27,.040,.45),copper,.017)
        for k in range(3):
            box("Corner count stripe",(x,s*.297,1.124+.10*k),(.15,.006,.035),char,.001)
    for x in (-4.97,4.97):
        box("Static cyan service lens",(x,s*.295,2.65),(.39,.01,.060),light,.001)
screen,hi=artifact("e6-sight-screen",4800)

# Fold the return exactly as in coverPiece('half'). +Z in the map is −Y here.
box("Low continuous long block",(0,0,.530),(5,.798,1.060),orange,.021)
box("Low continuous right return",(2.9,-1.1,.530),(.798,3,1.060),orange,.018)
for i in range(5):
    x=(i-2)*.985
    box("Cast orange long cladding",(x,0,.562),(.955,.784,1.003),orange,.041)
    box("Bedded long wear cap",(x,0,1.040),(.957,.789,.120),steel,.018)
    for side in (-1,1):
        box("Recessed long kick panels",(x,side*.389,.392),(.77,.022,.417),gasket,.011)
        box("Pale edge ticks",(x+.28,side*.398,.827),(.193,.004,.067),marker,.001)
for i in range(3):
    y=-.10-i*1.0
    box("Cast orange return cladding",(2.90,y,.563),(.78,.96,1.003),orange,.041)
    box("Bedded return wear cap",(2.90,y,1.038),(.79,.954,.124),steel,.018)
    for side in (-1,1):
        box("Recessed return kick panels",(2.90+side*.389,y,.392),(.022,.775,.417),rust,.011)
        box("Inset locator",(2.90+side*.396,y,.827),(.008,.21,.064),light,.002)
low,lo=artifact("e6-low-cover-return",1800)


def reimport(path):
    prior=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects=sorted((o for o in set(scene.objects)-prior if o.type=="MESH"),key=lambda o:o.name)
    bpy.context.view_layer.update()
    return objects


def vv(objects):
    return [o.matrix_world@v.co for o in objects for v in o.data.vertices]


def bvh(obs):
    pp, ff=[],[]
    for ob in obs:
        i=len(pp)
        pp.extend(vv([ob]))
        ff.extend(tuple(i+n for n in f.vertices) for f in ob.data.polygons)
    return BVHTree.FromPolygons(pp,ff)


S,H=reimport(screen),reimport(low)
def bounds(objects):
    p=vv(objects)
    return [(round(min(v[i] for v in p),5),round(max(v[i] for v in p),5)) for i in range(3)]


assert bounds(S)==[(-6.,6.),(-.3,.3),(0.,3.)],bounds(S)
assert bounds(H)==[(-2.5,3.3),(-2.6,.4),(0.,1.1)],bounds(H)


def sees(tree,a,b):
    a,b=Vector(a),Vector(b)
    return tree.ray_cast(a,(b-a).normalized(),(b-a).length)[0] is None


trees=[bvh(S),bvh(H)]
xs=[-2.25+j*.125 for j in range(37)]
results={}
for z in (.85,1.70,3.1):
    hits=[]
    for t in trees:
        hits.append(sum(not sees(t,(x,-8,z),(x,8,z)) for x in xs))
    results[str(z)]=hits
assert results=={"0.85":[37,37],"1.7":[37,0],"3.1":[0,0]},results
for z in (.20,.85,1.04):
    for y in (-2.36,-2,-1.5,-1,-.5):
        assert not sees(trees[1],(2.20,y,z),(4.40,y,z))


# Put both rebuilt assets on their surveyed Round 5 rows, not hand-staged yaws.
screenXZ=(37,28.62693304105358)
lowXZ=(24.47554083283783,20.41477750540468)
sightYaw=-.5235987755982991
lowYaw=.03516129780801075
cmd=lambda xz,z=0:Vector((xz[0]-screenXZ[0],screenXZ[1]-xz[1],z))
for items,xz,yaw in ((S,screenXZ,sightYaw),(H,lowXZ,lowYaw)):
    xf=Matrix.Translation(cmd(xz)) @ Matrix.Rotation(yaw,4,"Z")
    for o in items:
        o.matrix_world=xf@o.matrix_world
bpy.context.view_layer.update()
packs=[(44,16.502577388071437),(30,40.75128869403572)]
A=bvh(S)
assert not sees(A,cmd(packs[0],1.70),cmd(packs[1],1.70))
assert sees(A,cmd(packs[0],3.1),cmd(packs[1],3.1))
receipt={
 "scope":"Static art meshes with reimported ray proof. No runtime detection, collision or encounter.",
 "archive":"Raynos/project-wildshard-singleplayer@ce1cf050b3/art/showcase-template/round-5-blockout",
 "blobs":{"layout.js":"5d019a020361c47187ec889f2bc947f82cd9f98a","lab.js":"51a3b4bef1f2d4891172164d10893d98d450a3b9","placement.js":"6a067ec22a8e07f1d99a9d495d23063d2863ab10"},
 "sourceCounts":{"sightwall":14,"half":31,"packs":12},
 "sightwall":{"xz":screenXZ,"yaw":sightYaw,"dimensions_xyz":[12,3,.6],**hi},
 "half":{"xz":lowXZ,"yaw":lowYaw,"long_xyz":[5,1.1,.8],"return_xyz":[.8,1.1,3],**lo},
 "pack_midpoint_pair_xz":packs,
 "pack_center_eye_blocked_at_y":[1.7],
 "pack_center_eye_clear_at_y":[3.1],
 "local_face_samples_each":len(xs),"cast_eyes_m":results,
 "face_hit_order":["tall","low"],"return_blocked_rays":15
}
(out/"e6-duel-cover.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt),flush=True)
if os.getenv("WILDSHARD_VALIDATE_ONLY")=="1":
    sys.exit(0)


floor=material("Review dusty mill grade",(.168,.139,.102),.10,.91)
# Textured review ground only: the two repeated art meshes stay textureless.
n=floor.node_tree.nodes
link=floor.node_tree.links.new
coord=n.new("ShaderNodeTexCoord")
grit=n.new("ShaderNodeTexNoise")
grit.inputs["Scale"].default_value=4.4
grit.inputs["Detail"].default_value=3.1
link(coord.outputs["Object"],grit.inputs["Vector"])
tint=n.new("ShaderNodeValToRGB")
tint.color_ramp.elements[0].position=.18
tint.color_ramp.elements[0].color=(.071,.045,.031,1)
tint.color_ramp.elements[1].position=.82
tint.color_ramp.elements[1].color=(.24,.186,.127,1)
link(grit.outputs["Fac"],tint.inputs[0])
node=n["Principled BSDF"]
link(tint.outputs["Color"],node.inputs["Base Color"])
bump=n.new("ShaderNodeBump")
bump.inputs["Distance"].default_value=.061
bump.inputs["Strength"].default_value=.39
link(grit.outputs["Fac"],bump.inputs["Height"])
link(bump.outputs[0],node.inputs["Normal"])
box("Review factory grade",(0,1,-.080),(150,150,.16),floor,0)
world=bpy.data.worlds.new("Dry East evening")
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.25,.37,.55,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.48
scene.world=world


def lamp(n,kind,p,t,watts,radius,color):
    l=bpy.data.lights.new(n,kind)
    l.energy,l.color=watts,color
    if kind=="SUN":l.angle=radius
    else:l.size=radius
    o=bpy.data.objects.new(n,l)
    scene.collection.objects.link(o)
    o.location=p
    o.rotation_euler=(Vector(t)-o.location).to_track_quat("-Z","Y").to_euler()


lamp("Furnace-zone last sun","SUN",(-24,-14,18),(0,0,0),2.79,.11,(1,.76,.54))
lamp("Open yard sky bounce","AREA",(0,-13,9),(0,0,1),2100,9,(.50,.70,1))
lamp("Return edge fill","AREA",(-13,8,6),cmd(lowXZ,1),540,6,(.68,.81,1))
cam=bpy.data.objects.new("Band 6 review",bpy.data.cameras.new("Band 6 review"))
scene.collection.objects.link(cam)
scene.camera=cam
scene.render.engine="CYCLES"
scene.cycles.samples=52
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.067
scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX"
scene.render.resolution_x=1440
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="JPEG"
scene.render.image_settings.quality=93
u=cmd(lowXZ)
for n,at,t,lens in [
 ("sight-screen",Vector((-9.5,-13.5,3.05)),Vector((0,0,1.34)),39),
 ("low-return",u+Vector((6,-6.7,2.34)),u+Vector((.66,-.75,.48)),40)
]:
    cam.location=at
    cam.rotation_euler=(t-at).to_track_quat("-Z","Y").to_euler()
    cam.data.lens=lens
    scene.render.filepath=str(out/(n+".jpg"))
    bpy.ops.render.render(write_still=True)

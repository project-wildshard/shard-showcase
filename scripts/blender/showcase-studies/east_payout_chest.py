"""E1d Band 1 static art: new East steel chest, pinned haul-crate context."""
import hashlib
import json
import math
from pathlib import Path
import os
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

S=bpy.context.scene
O=output_directory()
crate=Path(__file__).resolve().parents[3]/"public/assets/wildshard-art/haul-crate.glb"
PIN="d7a5f8fcb2b835d0c0c77c3051ebd950ed449dc2c563e10779fdc5f01cc6bb44"
assert hashlib.sha256(crate.read_bytes()).hexdigest()==PIN
clear_scene()


def mat(name,c,metal=0,rough=.52,e=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    n=m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value=(*c,1)
    n.inputs["Metallic"].default_value=metal
    n.inputs["Roughness"].default_value=rough
    n.inputs["Emission Color"].default_value=(*c,1)
    n.inputs["Emission Strength"].default_value=e
    return m


steel=mat("Blued powdercoat",(.070,.123,.142),.48,.41)
shadow=mat("Rubber seam",(.023,.032,.037),.12,.69)
steel_light=mat("Edge wear",(.255,.335,.357),.64,.38)
amber=mat("East safety amber",(.64,.215,.038),.30,.41)
amber_lit=mat("Readiness diode",(.98,.41,.041),.13,.33,1.2)
paint=mat("Stamped warm enamel",(.88,.79,.53),.15,.48,.11)
ink=mat("Aged ink",(.037,.051,.055),.10,.58)


def box(name,p,d,m,b=.025,s=1):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object
    o.name=name
    o.dimensions=d
    o.data.materials.append(m)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if b:
        z=o.modifiers.new("Edge bevel","BEVEL")
        z.width=b
        z.segments=s
        bpy.ops.object.modifier_apply(modifier=z.name)
    return o


def front_text(body,x,y,z,size,material):
    c=bpy.data.curves.new(body,"FONT")
    c.body,c.size,c.align_x,c.align_y=body,size,"CENTER","CENTER"
    c.resolution_u=3
    o=bpy.data.objects.new(body,c)
    S.collection.objects.link(o)
    o.rotation_euler.x=math.pi/2
    o.location=(x,y,z)
    c.materials.append(material)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target="MESH")


def bolt(p,rad,dep,m,orient):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=rad,depth=dep,
                                       location=p,rotation=orient)
    o=bpy.context.object
    o.name="Recessed fastener"
    o.data.materials.append(m)


# Fixed closed shell. Interior and opening are deliberately out of scope.
base=box("Welded lower shell",(0,0,.316),(1.32,.91,.57),steel,.048)
box("Peripheral rubber seam",(0,0,.613),(1.352,.936,.063),shadow,.020)
box("Pressed lid",(0,0,.724),(1.40,.97,.181),amber,.049)
box("Dark inlaid lid crown",(0,0,.828),(1.08,.77,.085),steel,.027)
for side in (-1,1):
    box("Skid",(.476*side,0,.045),(.311,.842,.09),shadow,.021)
    box("Side shock rail",(.666*side,0,.162),(.068,.91,.189),steel_light,.023)
    box("Lid shock rail",(.623*side,0,.816),(.147,.94,.151),steel_light,.022)
    box("Front lock seat",(.438*side,-.479,.593),(.209,.071,.199),shadow,.023)
    box("Lid latch",(.438*side,-.49,.623),(.095,.069,.120),steel_light,.012)
    box("Latch slot",(.438*side,-.527,.590),(.064,.006,.037),ink,.004)
    box("Rear hinge barrel",(.41*side,.472,.613),(.219,.055,.072),steel_light,.013)
    for z in (.24,.466):
        bolt((.576*side,-.45,z),.024,.035,steel_light,(math.pi/2,0,0))
    for y in (-.296,.293):
        bolt((.584*side,y,.899),.027,.010,ink,(0,0,0))
    for j in range(3):
        mark=box("Hazard cutout",(.255*side+j*.045*side,-.456,.176),
                 (.027,.008,.062),amber,.003)
        mark.rotation_euler.y=math.radians(-15)
box("Front registration plate",(0,-.466,.375),(.584,.039,.203),shadow,.019)
box("Enamel plaque lip",(0,-.489,.375),(.521,.020,.154),steel_light,.010)
box("Dark plaque insert",(0,-.502,.375),(.496,.012,.135),ink,.006)
front_text("SCRIP",.037,-.509,.386,.098,paint)
# A coin-shaped visual signifier; no financial or pickup behavior.
bolt((-.164,-.509,.383),.033,.012,amber,(math.pi/2,0,0))
box("Status slot",(0,-.491,.567),(.202,.026,.039),ink,.011)
for x in (-.058,0,.058):
    box("Amber status lamp",(x,-.506,.569),(.039,.010,.015),amber_lit,.004)
box("Lid stripe",(0,0,.874),(.087,.674,.017),amber,.005)

bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active=base
bpy.ops.object.join()
chest=bpy.context.object
chest.name="E1d | East Band 1 Scrip chest"
bpy.context.scene.cursor.location=(0,0,0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
# Fit all trim and the grounding pivot into the archival envelope.
bounds=[[fn(v.co[k] for v in chest.data.vertices) for k in range(3)] for fn in (min,max)]
for v in chest.data.vertices:
    for k,target in enumerate((1.4,1.0,.9)):
        lo,hi=(b[k] for b in bounds)
        v.co[k]=target*((v.co[k]-lo)/(hi-lo)-(.5 if k<2 else 0))
chest.data.update()
f=O/"e1d-band1-scrip-chest.glb"
export([chest],f)
raw=f.read_bytes()
assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
assert not set(doc)&{"images","animations","skins","extensionsRequired"}
ms,=doc["meshes"]
tri=sum(doc["accessors"][p["indices"]]["count"]//3 for p in ms["primitives"])
assert len(raw)<163840 and tri<2350,(len(raw),tri)


def mesh_in(path):
    old=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    return sorted((o for o in set(S.objects)-old if o.type=="MESH"),key=lambda o:o.name)


def get_bounds(objects):
    vs=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    return [[fn(v[k] for v in vs) for k in range(3)] for fn in (min,max)]


clear_scene()
o,=mesh_in(f)
assert o.location.length<1e-6
o.data.calc_loop_triangles()
assert len(o.data.loop_triangles)==tri
lo,hi=get_bounds([o])
extent=[round(b-a,4) for a,b in zip(lo,hi)]
assert extent[0]<=1.402 and extent[1]<=1.003 and extent[2]<=.912, extent
assert abs(lo[2])<.002


def camera(p,target,fl):
    d=bpy.data.cameras.new("Payout study camera")
    o=bpy.data.objects.new(d.name,d)
    S.collection.objects.link(o)
    o.location=p
    aim(o,target)
    d.lens=fl
    S.camera=o


def aim(o,target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()


def light(pos,target,power,c,size):
    d=bpy.data.lights.new("Soft gallery light","AREA")
    d.energy,d.color,d.size,d.shape=power,c,size,"DISK"
    o=bpy.data.objects.new(d.name,d)
    S.collection.objects.link(o)
    o.location=pos
    aim(o,target)


def ground(look,c):
    m=mat(look,c,.05,.77)
    n=m.node_tree.nodes
    links=m.node_tree.links
    tex=n.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=7
    tex.inputs["Detail"].default_value=3
    coords=n.new("ShaderNodeTexCoord")
    links.new(coords.outputs["Object"],tex.inputs["Vector"])
    bump=n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.34
    bump.inputs["Distance"].default_value=.075
    links.new(tex.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs[0],n["Principled BSDF"].inputs["Normal"])
    bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,-.003))
    bpy.context.object.data.materials.append(m)


def world(c):
    S.world=bpy.data.worlds.new("Cool perimeter ambience")
    S.world.color=c


def render(slug,w,h):
    S.render.engine="CYCLES"
    S.cycles.samples=40
    S.cycles.use_denoising=False
    S.render.resolution_x,S.render.resolution_y=w,h
    S.render.resolution_percentage=100
    S.render.image_settings.file_format="JPEG"
    S.render.image_settings.quality=92
    S.view_settings.view_transform="AgX"
    S.view_settings.look="AgX - Medium High Contrast"
    S.render.filepath=str(O/f"nov24-east-payout-{slug}.jpg")
    bpy.ops.render.render(write_still=True)


ground("Steel gallery slate",(.047,.064,.079))
world((.143,.170,.210))
light((-2.8,-3.4,3.3),(0,0,.50),370,(1,.88,.73),3.7)
light((2.6,-1.7,1.9),(0,0,.69),160,(.68,.84,1),2.1)
light((.4,1.9,2.54),(0,0,.55),270,(.53,.74,1),2.3)
camera((1.70,-3.45,1.72),(0,0,.45),63)
if os.environ.get("WSC_PAYOUT_PROOF_ONLY")!="1":
    render("detail",1500,1050)

clear_scene()
ground("Neutral East yard concrete study",(.17,.177,.164))
world((.20,.23,.28))
paintline=mat("Apron lane line",(.41,.30,.124),0,.85)
dim=mat("Staging concrete divider",(.102,.129,.137),.12,.70)
dark=mat("Stand-in steel yard rib",(.075,.10,.114),.35,.58)
a=mat("Small marker lamp",(.92,.39,.07),0,.50,1.1)
for x in (-6,4.9):
    box("Neutral stage stripe",(x,7,0.006),(.085,23,.012),paintline,0)
for y in (1.3,8.0,16.1):
    for x in (-12.5,9):
        box("Background wall segment",(x,y,1.4),(1.0,6.5,2.8),dim,.06)
        box("Steel rib",(x-.53,y,1.72),(.12,.42,3.35),dark,.024)
        box("Warm marker",(x-.61,y,2.54),(.035,.18,.39),a,.009)
box("Far yard backdrop",(0,21.2,1.9),(25,.55,3.8),dim,.08)
for x in (-7.5,-2.5,2.5,7.5):
    box("Far divider rib",(x,20.8,2.1),(.44,.21,4.2),dark,.034)

# Two script-recovered Round 5 x/z anchors. Translate to a small local
# scene, preserving offset and separation, with no inferred terrain y.
origin=(103.2476,-89.0561)
chests=((103.2476,-89.0561),(102.6855,-103.4562))
cover=((100.2476,-92.0561),(99.6855,-106.4562))


def convert(xz):
    return Vector((xz[0]-origin[0],-xz[1]+origin[1],0))


def instance(path,loc,spin=0,scale=1,recenter=False):
    obs=mesh_in(path)
    lo,hi=get_bounds(obs)
    mat=Matrix.Translation(loc)@Matrix.Rotation(spin,4,"Z")@Matrix.Scale(scale,4)
    if recenter:
        mat=mat@Matrix.Translation(Vector((-(hi[0]+lo[0])/2,-(hi[1]+lo[1])/2,-lo[2])))
    for o in obs:
        o.matrix_world=mat@o.matrix_world
    bpy.context.view_layer.update()
    return obs


placements=[]
cover_parts=[]
for c,b in zip(chests,cover):
    center,cover_center=map(convert,(c,b))
    cp=instance(f,center)
    assert (cp[0].location-center).length<1e-5
    cover_obs=instance(crate,cover_center,.18,1.07,True)
    cover_parts.extend(cover_obs)
    lo,hi=get_bounds(cover_obs)
    assert abs((lo[0]+hi[0])/2-cover_center.x)<.10 and abs((lo[1]+hi[1])/2-cover_center.y)<.10
    assert (round(center.x-cover_center.x,4),round(center.y-cover_center.y,4))==(3,-3)
    placements.append({"world_three_chest_xz":c,"world_three_cover_xz":b,
                       "local_blender_delta":[3,-3,0]})
light((-5,-5,7),(-1.3,0,1),900,(1,.73,.53),6)
light((4.6,-4.3,5.8),(0,0,.4),680,(.68,.84,1),5)
light((2.0,18,6.0),(0,12,0),1400,(1,.71,.45),7)
light((-3.7,8.4,8.4),(-.56,11,0),1550,(.56,.68,1),6)
camera((2.28,-5.25,1.7),(-1.25,5.24,.67),31)
S.render.resolution_x,S.render.resolution_y=1536,1024
bpy.context.view_layer.update()
verts,faces=[],[]
for o in cover_parts:
    faces.extend(tuple(len(verts)+j for j in p.vertices) for p in o.data.polygons)
    verts.extend(o.matrix_world @ v.co for v in o.data.vertices)
bvh=BVHTree.FromPolygons(verts,faces)
for info,xz in zip(placements,chests):
    plaque=convert(xz)+Vector((0,-.482,.385))
    p=world_to_camera_view(S,S.camera,plaque)
    ray=plaque-S.camera.location
    assert min(p.x,p.y)>0 and max(p.x,p.y)<1
    assert bvh.ray_cast(S.camera.location,ray.normalized(),ray.length)[0] is None
    info["plaque_in_approach_frame_xy"]=[round(p.x,4),round(p.y,4)]
    info["plaque_cover_only_occlusion"]=False
if os.environ.get("WSC_PAYOUT_PROOF_ONLY")!="1":
    render("approach",1536,1024)

(O/"east-payout-chest-proof.json").write_text(json.dumps({
    "scope":"Static Band 1 payout chest, no native placement, opening or economy.",
    "round5_placement_ref":"Raynos/project-wildshard-singleplayer@ce1cf050b3:art/showcase-template/round-5-blockout/placement.js",
    "placement_precision":"Source calculation rounded to four decimal places; ground height and facing are staging.",
    "cover_standin_sha256":PIN,"placements":placements,"approx_archive_placeholder_xyz":[1.4,1.0,.9],
    "glb_bounds_size_xyz":extent,"glb_bytes":len(raw),"triangles":tri,"materials":len(ms["primitives"]),
    "approach_eye_height_m":1.7,
},indent=2)+"\n")

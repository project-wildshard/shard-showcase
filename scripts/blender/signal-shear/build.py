"""Signal Shear: original stylized gatekeeper weapon and rain-bench scene."""
import bpy
import bmesh
import math
import sys
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "art/weapons/signal-shear"
RENDER = Path(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else OUT
OUT.mkdir(parents=True, exist_ok=True)
RENDER.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
weap = bpy.data.collections.new("Signal Shear | runtime"); S.collection.children.link(weap)
stage = bpy.data.collections.new("Foundry rain bench | studio"); S.collection.children.link(stage)


def material(name,color,metal=0,rough=.4,em=0,weather=False):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1)
    m.use_nodes=True
    nt=m.node_tree; bs=nt.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1); bs.inputs["Metallic"].default_value=metal
    bs.inputs["Roughness"].default_value=rough
    if em:
        bs.inputs["Emission Color"].default_value=(*color,1); bs.inputs["Emission Strength"].default_value=em
    if weather:
        n=nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value=86; n.inputs["Detail"].default_value=3
        b=nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value=.13; b.inputs["Distance"].default_value=.0024
        nt.links.new(n.outputs["Fac"],b.inputs["Height"]);nt.links.new(b.outputs["Normal"],bs.inputs["Normal"])
    return m


steel=material("01 | Charcoal nickel",(.072,.096,.125),.88,.27,weather=True)
edge=material("02 | Honed silver",(.31,.43,.49),.92,.22)
iron=material("03 | Oiled midnight",(.019,.028,.035),.71,.30)
brass=material("04 | Old yellow bronze",(.44,.22,.064),.74,.31,weather=True)
wear=material("05 | Brass brightwork",(.69,.45,.17),.81,.27)
wrap=material("06 | Black woven grip",(.036,.025,.024),.03,.51,weather=True)
glass=material("07 | Oxide signal glass",(.006,.34,.25),.24,.27,1.35)
darkglass=material("08 | Cool glazed recess",(.012,.095,.082),.50,.33)
floor=material("Studio | Old stone",(.013,.021,.033),.14,.48,weather=True)
concrete=material("Studio | Fixture casting",(.021,.046,.058),.52,.45,weather=True)
paint=material("Studio | Ochre paint",(.36,.18,.035),.31,.54)
warm=material("Studio | Amber edge",(.8,.19,.025),.1,.34,1.3)


def link(obj,c,mat):
    for old in list(obj.users_collection): old.objects.unlink(obj)
    c.objects.link(obj)
    if mat: obj.data.materials.append(mat)
    return obj


def mesh(name,v,f,c=weap):
    m=bpy.data.meshes.new(name);m.from_pydata(v,[],f)
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
    o=bpy.data.objects.new(name,m);c.objects.link(o);return o


def bevel(o,w,steps=2):
    b=o.modifiers.new("Machined edge radius","BEVEL");b.width=w;b.segments=steps
    n=o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL");n.keep_sharp=True
    return o


def block(name,pos,size,mat,c=weap,rad=.009,angle=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.rotation_euler.z=angle
    return bevel(link(o,c,mat),rad)


def peg(name,pos,r,length,mat,c=weap,axis="Z",verts=12):
    r0=(math.pi/2,0,0) if axis=="Y" else (0,0,0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=length,location=pos,rotation=r0)
    o=bpy.context.object;o.name=name
    return bevel(link(o,c,mat),min(.008,r*.24),1)


def slab(name,xy,z0,z1,mat,c=weap,r=.006):
    n=len(xy);vv=[(x,y,z) for z in (z0,z1) for x,y in xy]
    ff=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=mesh(name,vv,ff,c);o.data.materials.append(mat)
    return bevel(o,r)


# Cross-sections preserve a dark center, polished shoulder and visible edge
# even on a small render. The asymmetric toe is a fictional machinery tooth.
rows=[(.18,-.063,.085,.040),(.31,-.115,.137,.050),(.44,-.147,.186,.052),
      (.51,-.147,.164,.047),(.91,-.153,.146,.041),(1.26,-.165,.130,.033),
      (1.44,-.185,.116,.026),(1.55,-.174,.070,.019),(1.67,-.098,-.083,.005)]
vv=[]
for y,l,r,h in rows:
    b=min(.027,(r-l)*.30)
    vv.extend([(l,y,0),(l+b,y,h),(r-b,y,h),(r,y,0),(r-b,y,-h),(l+b,y,-h)])
ff=[tuple(reversed(range(6)))]
mi=[0]
for j in range(len(rows)-1):
    for k in range(6):
        ff.append((6*j+k,6*j+(k+1)%6,6*(j+1)+(k+1)%6,6*(j+1)+k))
        mi.append(0 if k in (1,4) else 1)
ff.append(tuple(range(6*(len(rows)-1),6*len(rows))));mi.append(1)
blade=mesh("Forged crescent | two edge rails",vv,ff)
for m in (steel,edge):blade.data.materials.append(m)
for p,i in zip(blade.data.polygons,mi):p.material_index=i
# Blender normals should point outward on all section surfaces.
bpy.ops.object.select_all(action="DESELECT");blade.select_set(True);bpy.context.view_layer.objects.active=blade
bpy.ops.object.mode_set(mode="EDIT");bpy.ops.mesh.select_all(action="SELECT");bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode="OBJECT")

for sign in (-1,1):
    z=sign
    def panel(name,xy,height,thick,mat,rad=.005):
        a,b=sorted((z*height,z*(height+thick)))
        return slab(name,xy,a,b,mat,r=rad)
    panel("Bronze shoulder cap", [(-.130,.29),(.111,.27),(.165,.43),(.118,.55),(-.12,.49)],.042,.018,brass)
    panel("Dark signal well",[(-.067,.53),(.059,.53),(.072,.99),(.045,1.36),(-.065,1.44),(-.090,1.18)],.036,.016,iron)
    for k in range(6):
        y=.59+k*.122
        panel("Frosted signal segment %d"%k,[(-.047,y),(.033-k*.003,y-.013),(.04-k*.003,y+.067),(-.048,y+.084)],.052,.006,glass if k<5 else darkglass,.003)
    for x,y in [(-.095,.36),(.096,.375),(-.076,.478),(.081,.457),(-.104,1.25)]:
        peg("Flush bronze pin",(x,y,z*.063),.014,.009,wear,verts=10)
    # A small die-stamped mark, drawn as recessed-looking bars.
    for k,size in enumerate((.042,.033,.022)):
        block("Foundry tally",(0.097-k*.006, .57+.03*k,z*.050),(size,.009,.004),wear,rad=.0015,angle=-.30)

jaws=[]
for sign in (-1,1):
    profile=[(.093,.081),(.24,.093),(.318,.165),(.305,.235),(.252,.218),(.205,.158),(.093,.145)]
    jaws.append(slab("Left release gate" if sign<0 else "Right release gate",
                    [(sign*x,y) for x,y in profile],-.043,.043,brass,r=.012))
    for z in (-.051,.051):
        jaws.append(peg("Release gate flush pin",(sign*.123,.134,z),.018,.011,wear,verts=10))
slab("Heat shield collar",[(-.089,.22),(.095,.22),(.104,.124),(.057,.048),(-.055,.045),(-.101,.119)],-.064,.064,steel,r=.014)
peg("Full grip underlay",(0,-.126,0),.059,.355,wrap,axis="Y")
for i in range(10):
    o=peg("Braided grip band %02d"%i,(0,.022-i*.033,0),.060-(i%2)*.002,.016,wrap if i%2 else iron,axis="Y",verts=14)
    o.rotation_euler.z=(-1 if i%2 else 1)*.14
for y in (.037,-.296):
    peg("Clamped brass grip seam",(0,y,0),.066,.027,brass,axis="Y")
slab("Octagonal counterweight",[(-.071,-.30),(.069,-.30),(.088,-.339),(.065,-.40),(-.061,-.40),(-.083,-.347)],-.044,.044,brass,r=.012)
for z in (-.05,.05):
    peg("Signal pip",(0,-.352,z),.024,.01,glass,verts=10)

# Runtime sockets / scale. Root is at the grip center; preview uses same geometry.
grip=bpy.data.objects.new("grip_socket",None);grip.location=(0,-.126,0);weap.objects.link(grip)
tip=bpy.data.objects.new("tip_socket",None);tip.location=(-.091,1.66,0);weap.objects.link(tip)
rig_data=bpy.data.armatures.new("Signal Shear rigid mechanism")
rig=bpy.data.objects.new("WSC-WPN-014_Signal_Shear",rig_data);weap.objects.link(rig)
rig.location=(0,-.126,0)
bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
def bone(name,x,y,parent=None):
    b=rig_data.edit_bones.new(name);b.head=(x,y,0);b.tail=(x,y+.10,0)
    if parent:b.parent=parent
    return b
core=bone("grip",0,0)
bone("gate_L",-.123,.260,core);bone("gate_R",.123,.260,core)
bpy.ops.object.mode_set(mode="OBJECT")
for q in rig.pose.bones:q.rotation_mode="XYZ"
def attach(o,name):
    saved=o.matrix_world.copy()
    o.parent=rig;o.parent_type="BONE";o.parent_bone=name
    bpy.context.view_layer.update();o.matrix_world=saved
for o in list(weap.objects):
    if o is not rig:attach(o,"gate_L" if o in jaws[:3] else "gate_R" if o in jaws[3:] else "grip")

S.render.fps=30
def clip(name,frames):
    for f,grip_angle,gate_angle in frames:
        for n,r in (("grip",grip_angle),("gate_L",gate_angle),("gate_R",-gate_angle)):
            q=rig.pose.bones[n];q.rotation_euler.z=math.radians(r);q.keyframe_insert(data_path="rotation_euler",frame=f,group=n)
    action=rig.animation_data.action; action.name=name; action.asset_mark()
    rig.animation_data.action=None
    track=rig.animation_data.nla_tracks.new();track.name=name
    track.strips.new(name,1,action)
    track.mute=True
clip("Signal_Release",[(1,0,0),(6,0,-8),(14,0,-26),(24,0,-26),(32,0,4),(39,0,0)])
clip("Arc_Cut",[(1,0,0),(9,33,-7),(14,-55,-16),(21,-26,-4),(31,0,0)])
for q in rig.pose.bones:q.rotation_euler.z=0
bpy.context.view_layer.update()

# Export with no stage, light or textures downloaded.
bpy.ops.object.select_all(action="DESELECT")
for o in weap.objects:o.select_set(True)
rig.location.y=0
for tr in rig.animation_data.nla_tracks:tr.mute=False
bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=str(OUT/"signal-shear.glb"),export_format="GLB",use_selection=True,export_apply=True,export_extras=True,export_animation_mode="NLA_TRACKS")
for tr in rig.animation_data.nla_tracks:tr.mute=True
for q in rig.pose.bones:q.rotation_euler.z=0
rig.location.y=-.126
bpy.context.view_layer.update()

block("Stage ground",(0,.60,-.247),(8,9,.18),floor,stage,.05)
block("Raised inspection slab",(0,.67,-.139),(1.11,2.65,.15),concrete,stage,.060,angle=-.04)
for y in (-.31,.14,1.40):
    for x in (-.37,.37):peg("Slab fastener",(x,y,-.053),.024,.020,steel,stage,verts=8)
for y in (-.23,.38,1.21):
    block("Machined nest",(0,y,-.083),(.38,.085,.085),iron,stage,.012)
for k in range(8):
    block("Painted chevron",(.45,1.71-k*.105,-.060),(.119,.033,.008),paint,stage,.002,angle=-.55)
for k in range(5):
    block("Vented cut line",(-.43,-.20+k*.065,-.060),(.11,.012,.005),iron,stage,.002)
for k in range(3):
    block("Bench status slit",(-.415,.93+k*.052,-.057),(.066,.015,.006),warm,stage,.002)

def aim(o,pt):o.rotation_euler=(Vector(pt)-o.location).to_track_quat("-Z","Y").to_euler()

def area(name,pos,pt,power,color,size):
    d=bpy.data.lights.new(name,"AREA");d.energy=power;d.color=color;d.shape="DISK";d.size=size
    o=bpy.data.objects.new(name,d);stage.objects.link(o);o.location=pos;aim(o,pt)

area("Soft silver key",(-2.5,.6,3.2),(0,.65,0),420,(.57,.76,1),2.4)
area("Warm forge edge",(1.5,2.2,1.7),(0,.75,0),230,(1,.47,.18),1.4)
area("Cold hilt kick",(.65,-1.5,.85),(0,.05,0),80,(.22,.77,1),1.1)
area("Long bevel card",(1.65,.75,3.8),(0,.7,0),150,(.85,.92,1),2.0)
world=bpy.data.worlds.new("Charcoal ambient");S.world=world;world.use_nodes=True;world.node_tree.nodes["Background"].inputs[0].default_value=(.045,.058,.07,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.30
d=bpy.data.cameras.new("Hero camera");o=bpy.data.objects.new("Hero camera",d);stage.objects.link(o);S.camera=o
o.location=(2.25,-.55,4.4);aim(o,(0,.65,-.025));d.type="ORTHO";d.ortho_scale=2.77
from mathutils import Quaternion
o.rotation_mode="QUATERNION"; o.rotation_quaternion=o.rotation_euler.to_quaternion()
o.rotation_quaternion=o.rotation_quaternion@Quaternion((0,0,1),-.28)
S.render.engine="CYCLES";S.cycles.samples=64;S.cycles.use_denoising=False
S.render.resolution_x=860;S.render.resolution_y=1070;S.render.resolution_percentage=100
S.render.image_settings.file_format="PNG"
S.view_settings.view_transform="AgX"
S.render.filepath=str(RENDER/"signal-shear-hero.png")
# Script is source of truth; blend is editable and retains the studio.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"signal-shear.blend"),compress=True)
bpy.ops.render.render(write_still=True)

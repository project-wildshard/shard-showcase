"""W0b six town gate signs; a shared frame and six interchangeable faces."""
import hashlib
import json
import math
import os
from pathlib import Path
import random
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

out = output_directory()
clear_scene()
scene = bpy.context.scene
repo = Path(__file__).resolve().parents[3]
assets = repo / "public/assets/wildshard-art"
WIDTH, HEIGHT, DEPTH = 3.32, .63, .125
A = "w0b-town-gate-nameplates"
dest = out / (A + ".glb")

GATES = (
    ("East", (.40, .090, .034), "combat road"),
    ("Stable", (.161, .119, .052), "paddock and oval"),
    ("Movers", (.035, .196, .202), "movers and grapple course"),
    ("West", (.147, .175, .085), "grapple start, climb yard, the Rock"),
    ("Park", (.046, .178, .280), "hover park and climb yard"),
    ("Range", (.223, .072, .119), "range and physics yard"),
)


def material(name, c, rough=.6, metal=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*c, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (*c, 1)
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Metallic"].default_value = metal
    return m


bronze = material("Satin bronze · perimeter", (.225, .126, .054), .38, .63)
dark = material("Blackened cast metal", (.049, .041, .034), .65, .38)
enamel = material("Warm ceramic enamel", (.79, .625, .356), .49)
letter = material("Oxide brown lettering", (.051, .029, .019), .7)
ivory = material("Bone white icon", (.87, .75, .49), .48)
washer = material("Darkened bolt recess", (.103, .085, .062), .41, .72)


def link(name, data=None):
    o = bpy.data.objects.new(name, data)
    scene.collection.objects.link(o)
    return o


def bevel(o, width, seg=1):
    if not width:
        return
    bpy.context.view_layer.objects.active = o
    mo = o.modifiers.new("Tool radius", "BEVEL")
    mo.width = width
    mo.segments = seg
    bpy.ops.object.modifier_apply(modifier=mo.name)


def prism(name, outline, front, back, ma, roundover=0):
    # CCW on the X/Z sign plane gives a normal towards local −Y.
    n = len(outline)
    vv = [(x, y, z) for y in (front, back) for x, z in outline]
    ff = [tuple(range(n)), tuple(reversed(range(n, n * 2)))]
    ff.extend((i, i+n, (i+1)%n+n, (i+1)%n) for i in range(n))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vv, [], ff)
    mesh.update()
    mesh.materials.append(ma)
    o = link(name, mesh)
    bevel(o, roundover)
    return o


def corners(w, h, e):
    x,z=w/2,h/2
    return [(-x+e,-z),(x-e,-z),(x,-z+e),(x,z-e),(x-e,z),(-x+e,z),(-x,z-e),(-x,-z+e)]


def shift(outline, x, z):
    return [(u+x, v+z) for u,v in outline]


def disc(x, z, r, n):
    return [(x+r*math.cos(math.tau*i/n),z+r*math.sin(math.tau*i/n)) for i in range(n)]


def join(name, objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    objs[0].data.name = name
    return objs[0]


frame = [
    prism("Cast tray", corners(WIDTH, HEIGHT, .065), -DEPTH, 0, dark, .012),
    prism("Beaded edge", corners(WIDTH-.031, HEIGHT-.031, .056), -.150, -.111, bronze, .007),
    prism("Ceramic panel", corners(WIDTH-.099, HEIGHT-.104, .041), -.166, -.145, enamel, .006),
]
for x in (-1.485, 1.485):
    for z in (-.163, .163):
        frame.extend((
            prism("Washer", disc(x,z,.027,12), -.176, -.160, washer, .002),
            prism("Hex head", disc(x,z,.017,6), -.185, -.175, bronze, .002),
        ))
chassis = join("Shared frame", frame)
chassis.hide_render = True

# Each set describes a pictogram as simple, reproducible strokes in X/Z.
icons = {
    "East": [[(-.086,.062),(0,.097),(.086,.062),(.074,-.031),(0,-.095),(-.074,-.031),(-.086,.062)],
             [(-.028,.024),(0,-.017),(.028,.024)]],
    "Stable": [[(-.066,.075),(-.074,.012),(-.057,-.046),(-.019,-.074),(.019,-.074),(.057,-.046),(.074,.012),(.066,.075)],
               [(-.059,-.004),(-.040,-.006)],[(.059,-.004),(.040,-.006)]],
    "Movers": [[(-.079,-.060),(.035,-.060)],[(-.032,-.003),(.079,-.003)],[(-.080,.060),(.034,.060)]],
    "West": [[(-.093,-.063),(-.028,.046),(.006,-.001),(.047,.081),(.098,-.063)],
             [(-.054,-.063),(.071,-.063)]],
    "Park": [[(-.094,-.056),(-.054,-.048),(-.009,-.024),(.025,.013),(.057,.071),(.094,.071)],
             [(-.078,-.089),(.078,-.089)]],
    "Range": [[(.087*math.cos(math.tau*i/12),.087*math.sin(math.tau*i/12)) for i in range(13)]],
}


def glyphs(name):
    f = bpy.data.curves.new(name + " title", "FONT")
    f.body = name.upper() + " GATE"
    f.align_x = "CENTER"
    f.align_y = "CENTER"
    f.size = .40
    f.resolution_u = 4
    f.extrude = 0
    f.materials.append(letter)
    o = link(name + " lettering", f)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.object
    xx=[v.co.x for v in o.data.vertices]
    zz=[v.co.y for v in o.data.vertices]
    sw = min(1, 2.12/(max(xx)-min(xx)))
    sz = .299/(max(zz)-min(zz))
    mx, mz = (max(xx)+min(xx))/2, (max(zz)+min(zz))/2
    for v in o.data.vertices:
        x,y,_ = v.co
        v.co = ((x-mx)*sw+.206,-.1685,(y-mz)*sz+.010)
    return o


def inlay(name, outline, y):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(x,y,z) for x,z in outline], [], [tuple(range(len(outline)))])
    mesh.update()
    mesh.materials.append(ivory)
    return link(name, mesh)


def stroke(name, a, b, x, plane, width=.025):
    u,v = a
    xx,zz = b
    d=math.hypot(xx-u,zz-v)
    dx,dz=(xx-u)/d*width/2,(zz-v)/d*width/2
    return inlay(name,[(u+dz+x,v-dx),(xx+dz+x,zz-dx),(xx-dz+x,zz+dx),(u-dz+x,v+dx)], plane)


spec = {}
parts=[]
for i,(name, c, destination) in enumerate(GATES):
    p = link(name + " Gate")
    p.location=((i%2-.5)*3.77, 0, (1-i//2)*.92+.9)
    shell=link("Frame · " + name, chassis.data)
    shell.parent=p
    x=-1.10
    face=[prism("Route medallion",shift(corners(.385,.380,.052),x,0),-.194,-.163,
                material(name+" route enamel",c,.45),.007),glyphs(name)]
    for j,line in enumerate(icons[name]):
        for k,(a,b) in enumerate(zip(line,line[1:])):
            face.append(stroke(f"{name} {j} / {k}",a,b,x,-.197-.000009*(j*16+k)))
        # Round junction caps avoid gapped corners in the thin inlay.
        for qx,qz in sorted({(round(a,7),round(b,7)) for a,b in line}):
            face.append(inlay("Inlay joint",disc(x+qx,qz,.0125,6),-.1973))
    if name=="Range":
        face.append(inlay("Bullseye",disc(x,0,.029,8),-.198))
    fascia=join(name+" face",face)
    fascia.parent=p
    parts.extend((p,shell,fascia))
    spec[name]={"destination":destination,"face_h":.299}

bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.export_scene.gltf(filepath=str(dest), export_format="GLB", use_selection=True, export_animations=False)
raw=dest.read_bytes()
assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
doc=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
frames=[n for n in doc["nodes"] if n["name"].startswith("Frame · ")]
assert len(frames)==6 and len({f["mesh"] for f in frames})==1
assert len(doc["meshes"]) == 7 and not any(doc.get(k) for k in ("images","skins","animations"))
tri=sum(doc["accessors"][p["indices"]]["count"]//3 for m in doc["meshes"] for p in m["primitives"])
assert len(raw)<250000 and tri<5000, (len(raw),tri)

for o in (*parts,chassis):
    bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(dest))
bpy.context.view_layer.update()
parents={name:bpy.data.objects[name+" Gate"] for name,_,_ in GATES}
fdata=None
for name,p in parents.items():
    children={o.name.split(" ")[0]:o for o in p.children}
    body,face=children["Frame"],children[name]
    fdata=fdata or body.data
    assert body.data==fdata and abs(min(v.co.x for v in body.data.vertices)+WIDTH/2)<.002
    assert abs(max(v.co.y for v in body.data.vertices))<.0001
    xs=[v.co.x for v in face.data.vertices]
    assert min(xs)>-1.32 and max(xs)<1.31

# Preview 1: six removable boards on a warm masonry swatch. No background
# geometry is exported. Preview 2: one plaque on the existing East gate only.
masonry=[
    material("Warm limestone "+str(i),c)
    for i,c in enumerate(((.44,.339,.240),(.37,.282,.201),(.49,.386,.282),(.413,.328,.248)))
]
mortar=material("Mortar gap",(.22,.172,.124))


def box(name,p,dim,ma,r=.0):
    w,d,h=dim
    x,y,z=p
    return prism(name,shift(corners(w,h,0.001),x,z),y-d/2,y+d/2,ma,r)


rng=random.Random(72)
backing=[box("Swatch mortar",(0,.31,.9),(12,.32,4.4),mortar)]
for j in range(9):
    for i in range(-9,10):
        backing.append(box("Limestone course",(.67*(i+.5*(j%2)),.118,.47*j-.90),
                    (.656,.221,.451),rng.choice(masonry),.012))

world=bpy.data.worlds.new("Town daylight")
world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.46,.58,.79,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.52
scene.world=world


def aim(o, at):
    o.rotation_euler=(Vector(at)-o.location).to_track_quat("-Z","Y").to_euler()


def area(name,at,to,energy,color,size):
    d=bpy.data.lights.new(name,"AREA")
    d.energy=energy;d.color=color;d.shape="DISK";d.size=size
    o=link(name,d);o.location=at;aim(o,to)
    return o


lights=[area("Slanted sun",(-4,-5,6),(0,0,.8),1210,(1,.80,.61),4),
        area("Sky bounce",(4,-4,3),(0,0,.9),690,(.74,.85,1),6)]
cam=link("Gate review",bpy.data.cameras.new("Gate review"))
scene.camera=cam
scene.render.engine="CYCLES"
scene.cycles.samples=36
scene.cycles.use_denoising=False
scene.view_settings.view_transform="AgX"
scene.view_settings.look="AgX - Medium High Contrast"
scene.render.image_settings.file_format="JPEG"
scene.render.image_settings.quality=92


def render(file,eye,at,dims,scale=None,lens=36):
    cam.location=eye
    aim(cam,at)
    cam.data.type="ORTHO" if scale else "PERSP"
    if scale: cam.data.ortho_scale=scale
    cam.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=dims
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/(file+".jpg"))
    if not os.environ.get("WILDSHARD_VALIDATE_ONLY"):
        bpy.ops.render.render(write_still=True)


render("nov23-town-gate-signs",(.19,-11,2.64),(0,0,.9),(1550,780),8.25)
for o in backing+lights:
    bpy.data.objects.remove(o,do_unlink=True)
for n,p in parents.items():
    if n!="East":
        for o in tuple(p.children): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.objects.remove(p,do_unlink=True)

pins=json.loads((repo/"project/layouts/w0a-east-gate-boundary-donors.json").read_text())
cached={}


def donor(k,p,n,rot=0,scale=(1,1,1)):
    if k not in cached:
        row=pins[k]
        path=assets/row["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row["sha256"]
        old=set(scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(path));bpy.context.view_layer.update()
        nodes=sorted(set(scene.objects)-old,key=lambda o:o.name)
        cached[k]=[(o.data,o.matrix_world.copy()) for o in nodes if o.type=="MESH"]
        for o in nodes: bpy.data.objects.remove(o,do_unlink=True)
    t=Matrix.Translation(p)@Matrix.Rotation(rot,4,"Z")@Matrix.Diagonal((*scale,1))
    objs=[]
    for data,m in cached[k]:
        o=link(n,data)
        o.matrix_world=t@m
        objs.append(o)
    return objs


# Same scales and origin convention as the W0a boundary study, with local X
# along the lintel here. Ray sample the original sign mounting face rather
# than assuming the sign face touches the rough brick profile.
span=donor("span",(0,0,6.245),"Original masonry span",0,(1.78,.67,.236))
for sign in (-1,1):
    donor("tower",(sign*7.84,0,0),"Original flank tower",0,(.94,.65,7.19/5.275))
    donor("banner",(sign*8.36,-1.75,2.13),"Town banner",0,(.74,)*3)
    donor("lantern",(sign*6.61,-1.94,3.14),"Town lantern",0,(.62,)*3)
    donor("planter",(sign*8.10,-3.95,0),"Flowers",0,(.84,)*3)
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
def sample_mount(z):
    depths=[]
    for i in range(33):
        x=-1.64+.1025*i
        for j in range(15):
            zz=z-.30+j*.60/14
            hit,loc,_,_,ob,_=scene.ray_cast(dg,(x,-6,zz),(0,1,0),distance=10)
            if hit and ob in span:
                depths.append(loc.y)
    return depths


# Choose the lintel band with the most masonry behind the plate. The first
# scene mockup placed its center higher, across a projecting cornice.
candidates=[(7.02+.02*i,sample_mount(7.02+.02*i)) for i in range(20)]
z,hits=max(candidates,key=lambda c:(len(c[1]),-abs(c[0]-7.12)))
assert len(hits)>250 and max(hits)-min(hits)<.36, (z,len(hits),min(hits),max(hits))
rear=min(hits)-.012
anchor_centers=[]
mount_lengths=[]
for x in (-1.485,-.495,.495,1.485):
    zz=z+.085
    hit,loc,_,_,ob,_=scene.ray_cast(dg,(x,-6,zz),(0,1,0),distance=10)
    assert hit and ob in span, (x,zz,ob)
    dep=loc.y-rear+.008
    assert .011<dep<.38, dep
    mount_lengths.append(dep)
    anchor_centers.append((x,zz,loc.y))
parents["East"].location=(0,rear,z)
for x,zz,y in anchor_centers:
    prism("Staged steel stand-off",disc(x,zz,.049,10),rear-.003,y+.008,dark,.004)
for j in range(15):
    for i in range(-9,10):
        box("Plaza paver", (1.7*i+(j%2)*.85, -19+j*1.65, -.056),
            (1.685,1.628,.11),rng.choice(masonry),.01)
box("Earth",(0,0,-.16),(190,160,.20),mortar)
sun=bpy.data.lights.new("Late town sun","SUN")
sun.energy=2.75;sun.angle=math.radians(7);sun.color=(1,.79,.56)
sun_o=link("Late town sun",sun);sun_o.rotation_euler=(.49,-.37,-.62)
area("Gate bounce",(1,-6,7),(0,0,5),470,(.66,.77,1),9)
render("nov23-east-gate-sign-fit",(3.1,-19.0,2.10),(0,0,5.5),(1470,965),lens=27)

bpy.context.view_layer.update()
p=parents["East"].location
h=scene.render.resolution_y
pa=world_to_camera_view(scene,cam,p+Vector((.18,-.17,.15)))
pb=world_to_camera_view(scene,cam,p+Vector((.18,-.17,-.15)))
assert 0<pa.x<1 and .10<pb.y<.95
(out/"validation.json").write_text(json.dumps({
    "bytes":len(raw),"unique_triangles":tri,"gates":spec,"unique_meshes":len(doc["meshes"]),
    "shared_frame_nodes":len(frames),"east_span_samples":len(hits),"east_span_y_range_m":[min(hits),max(hits)],
    "staged_stand_off_lengths_m":mount_lengths,
    "east_sign_center_m":list(p),"east_render_letter_height_px":round(abs(pa.y-pb.y)*h,1),
    "native_placement":False,
},indent=2)+"\n")

"""WSC-KIT-007 art-only tower and optional mount-aligned charged lamp."""
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

OUT = output_directory()
FAR = os.getenv("WSC_BEACON_FAR") == "1"
TOWER = "wsc-kit-007-storm-beacon" + ("-far" if FAR else "") + ".glb"
LAMP = "wsc-kit-007-storm-beacon-charged-lamp.glb"
clear_scene()


def material(name, color, rough, metal=0, glow=0):
    def lin(v):return v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4
    rgba=tuple(lin((color>>n&255)/255) for n in (16,8,0))+(1,)
    m=bpy.data.materials.new(name);m.diffuse_color=rgba;m.use_nodes=True
    q=m.node_tree.nodes.get("Principled BSDF")
    for k,v in [("Base Color",rgba),("Roughness",rough),("Metallic",metal),
                ("Emission Color",rgba),("Emission Strength",glow)]:
        q.inputs[k].default_value=v
    return m


black=material("Graphite armor",0x303c41,.72,.49)
inner=material("Charcoal crown lattice",0x292d2c,.63,.51)
warm=material("Worn ochre enamel",0xc47825,.58,.32)
steel=material("Galvanized ribs",0x647178,.54,.64)
silver=material("Machined fasteners",0x9e9d8b,.49,.70)
dark=material("Smoked lamp seat",0x4a4440,.50,.40)
opal=material("Charged opal",0xffc244,.35,.12,4.3)
wick=material("Bright tungsten",0xffdf80,.35,.30,7.0)


def finish(o,name,m):
    o.name=name;o.data.materials.append(m)
    return o


def box(name,p,d,m,bevel=.018):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=o.modifiers.new("Stamped edge","BEVEL");b.width=bevel;b.segments=1
        bpy.ops.object.modifier_apply(modifier=b.name)
    return finish(o,name,m)


def rod(name,a,b,r,m,N=10,top=None):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cone_add(vertices=N,radius1=r,radius2=r if top is None else top,
                                  depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object;o.rotation_euler=(b-a).to_track_quat("Z","Y").to_euler()
    return finish(o,name,m)


def collar(name,z,h,rad,m,r2=None):
    o=rod(name,(0,0,z),(0,0,z+h),rad,m,8,r2)
    o.rotation_euler.z=math.pi/8
    return o


def pt(r,a,z):return (r*math.cos(a),r*math.sin(a),z)


def pipe(name, points, rad, m):
    c=bpy.data.curves.new(name,"CURVE");c.dimensions="3D";c.bevel_depth=rad
    c.bevel_resolution=1;c.resolution_u=10;c.use_fill_caps=True
    spline=c.splines.new("BEZIER");spline.bezier_points.add(len(points)-1)
    for q,xyz in zip(spline.bezier_points,points):
        q.co=xyz;q.handle_left_type=q.handle_right_type="AUTO"
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o)
    c.materials.append(m);bpy.ops.object.select_all(action="DESELECT");o.select_set(True)
    bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target="MESH")
    return bpy.context.object


def join(name,objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.object.join()
    o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return o


def export(name,objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/name),export_format="GLB",use_selection=True,
                              export_animations=False,export_texcoords=False)


base=[collar("Cast foot",0,.23,1.18,black),
      collar("Foundation flange",.22,.12,1.11,steel),
      collar("Main armored pedestal",.30,2.23,1.005,black,.816),
      collar("High warning band",2.49,.24,.975,warm),
      collar("Warning band inner seal",2.71,.13,.90,inner),
      collar("Tapered upper stack",2.78,1.57,.740,black,.52),
      collar("Crown lower gasket",4.32,.09,.594,inner),
      collar("Crown warning flange",4.40,.18,.703,warm)]
details=[]
for i in range(8):
    a=math.tau*i/8+math.pi/8
    details.append(rod("Lower edge rib",pt(1.015,a,.29),pt(.821,a,2.54),.043,steel,6))
    details.append(rod("Upper edge rib",pt(.745,a,2.79),pt(.525,a,4.40),.035,steel,6))
    for j in range(0 if FAR else 7):
        z=.45+j*.31;r=1.024-(z-.30)*.085
        details.append(rod("Panel rivet",pt(r-.03,a,z),pt(r+.027,a,z),.035,silver,6))
    for j in range(0 if FAR else 3):
        z=3.00+j*.45;r=.755-(z-2.78)*.140
        details.append(rod("Small panel rivet",pt(r-.03,a,z),pt(r+.024,a,z),.028,silver,6))
    for z,r in (((.12,1.18),) if FAR else ((.12,1.18),(2.62,.975),(4.49,.705))):
        details.append(rod("Band fastener",pt(r-.032,a,z),pt(r+.028,a,z),.044,silver,6))
# Maintenance ladder is dressing; the prototype contains no traversal.
for x in (-.242,.242):
    details.append(rod("Ladder upright",(x,-1.046,.23),(x,-.95,2.86),.038,warm,8))
    for z in (.41,1.27,2.24):
        details.append(rod("Ladder stand-off",(x,-.82,z),(x,-1.047+(z-.23)*.037,z),.027,steel,8))
for j in (range(0,10,2) if FAR else range(10)):
    z=.36+j*.248;y=-1.046+(z-.23)*.0365
    details.append(rod("Ladder rung",(-.241,y,z),(.241,y,z),.024,warm,8))
if FAR:
    points=[(.88,-.34,.28),(.88,-.34,1.31),(.86,-.34,1.67),(.68,-.34,1.84)]
    details.extend(rod("Distant conduit",a,b,.071,steel,6) for a,b in zip(points,points[1:]))
else:
    details.append(pipe("Conduit",[(.88,-.34,.28),(.88,-.34,1.31),(.86,-.34,1.67),(.68,-.34,1.84)],.071,steel))
for z in (() if FAR else (.36,1.14)):
    details.append(rod("Orange conduit clamp",(.88,-.34,z),(.88,-.34,z+.067),.086,warm,8))
base.append(collar("Dark open lamp socket",4.56,.11,.418,dark))
# The cage is an open mesh assembly, not a filled cone.
for i in range(12):
    a=math.tau*i/12
    details.append(rod("Crown cage rib",pt(.48,a,4.55),pt(.84,a,5.45),.044,inner,6 if FAR else 8))
    for z,r in ((4.73,.55),(5.04,.68),(5.37,.81)):
        b=a+math.tau/12
        details.append(rod("Crown hoop segment",pt(r,a,z),pt(r,b,z),.036,inner,6 if FAR else 8))
    if not FAR:
        details.append(rod("Small crown rivet",pt(.825,a,5.37),pt(.858,a,5.37),.023,silver,6))

export(TOWER,[join("Beacon_Body_and_Socket",base),join("Beacon_Cage_and_Hardware",details)])
if FAR:
    sys.exit(0)  # Reuse the exact original charged insert.
clear_scene()
lamp=[collar("Charge cartridge lower flange",4.67,.085,.355,black),
      collar("Opal cartridge lower lens",4.75,.12,.254,opal,.321),
      collar("Opal cartridge lens",4.87,.24,.321,opal,.286),
      collar("Opal cartridge upper bevel",5.11,.103,.286,opal,.174),
      collar("Inner bright cap",5.205,.040,.142,wick,.096)]
for i in range(6):
    a=math.tau*i/6
    lamp.append(rod("Guard bar",pt(.335,a,4.74),pt(.294,a,5.14),.021,steel,6))
export(LAMP,[join("Beacon_Charged_Lamp_Insert",lamp)])

if os.getenv("WSC_BEACON_RENDER")=="1":
    clear_scene()
    def insert(path,x):
        before=set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(OUT/path))
        for o in set(bpy.context.scene.objects)-before:
            if o.parent is None:o.location.x+=x
    insert(TOWER,-1.84)
    insert(TOWER,1.84)
    insert(LAMP,1.84)
    box("Studio concrete",(0,0,-.16),(200,200,.30),material("Studio concrete mat",0x404b52,.92))
    s=bpy.context.scene;s.world.color=(.10,.13,.15)
    def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
    for p,power,size,color in [
        ((-5,-8,9),1550,6,(.80,.92,1)),((6,-4,7),2100,5,(1,.83,.59)),
        ((1,5,10),2600,5,(.63,.79,1))]:
        bpy.ops.object.light_add(type="AREA",location=p)
        o=bpy.context.object;o.data.energy=power;o.data.size=size;o.data.color=color;aim(o,(0,0,2.5))
    bpy.ops.object.camera_add(location=(5.4,-17,8.4))
    s.camera=bpy.context.object;aim(s.camera,(0,0,2.68))
    s.camera.data.type="ORTHO";s.camera.data.ortho_scale=8.7
    s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
    s.render.resolution_x=1440;s.render.resolution_y=1120;s.render.resolution_percentage=100
    s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=90
    s.render.filepath=str(OUT/"e9-storm-beacon-unlit-charged.jpg")
    bpy.ops.render.render(write_still=True)

"""WSC-KIT-006 art props: foreman desk and independent fictional quest keycard."""
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

OUT=output_directory()
DESK="wsc-kit-006-foreman-desk.glb"
CARD="wsc-kit-006-vault-keycard.glb"
clear_scene()


def mat(name,color,rough=.62,metal=0,emit=0):
    def lin(v):return v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4
    rgba=tuple(lin((color>>i&255)/255) for i in (16,8,0))+(1,)
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=rgba
    b=m.node_tree.nodes.get("Principled BSDF")
    for k,v in [("Base Color",rgba),("Roughness",rough),("Metallic",metal),
                ("Emission Color",rgba),("Emission Strength",emit)]:
        b.inputs[k].default_value=v
    return m


iron=mat("Dark bluish formed steel",0x32434b,.66,.55)
steel=mat("Brushed hardware",0x73868c,.46,.63)
ox=mat("Burnt orange drawer plates",0x9c502d,.61,.42)
wood=mat("Oiled brown worktop",0x795038,.78)
wood_edge=mat("Rubbed oak edge",0xa17a53,.71)
rubber=mat("Dark padded desk mat",0x20272c,.90)
warm=mat("Warm passive lens",0xffcd86,.39,.2,.34)
paper=mat("Manila forms",0xbfb28c,.85)
cardbody=mat("Vault copper polymer",0xc46e39,.58,.40)
cyan=mat("Cyan inventory marker",0x53e0d5,.42,.2,.7)
ivory=mat("Stencilled sand",0xdfc5a0,.82)


def box(n,p,d,m,w=.006):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if w:
        mod=o.modifiers.new("Worn edges","BEVEL");mod.width=w;mod.segments=1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(m)
    return o


def rod(n,a,b,r,m,top=None):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r,radius2=r if top is None else top,
                                  depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object;o.name=n;o.rotation_euler=(b-a).to_track_quat("Z","Y").to_euler()
    o.data.materials.append(m)
    return o


def join(name, parts):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in parts:ob.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join()
    o=bpy.context.object;o.name=name
    bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return o


def export(name,items):
    bpy.ops.object.select_all(action="DESELECT")
    for o in items:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/name),export_format="GLB",use_selection=True,
                            export_animations=False,export_texcoords=False)

# Floor-local pivot, 1.78 m worktop with a clear tabletop zone under the lamp.
frame=[box("Formed top frame",(0,0,.818),(1.74,.741,.085),iron,.019),
       box("Rolled wood edge",(0,0,.860),(1.78,.77,.058),wood_edge,.018),
       box("Worktop insert",(0,0,.888),(1.74,.735,.024),wood,.008),
       box("Runner back",(0,.325,.770),(1.54,.046,.051),iron),
       box("Knee brace",(0,.295,.209),(1.53,.051,.064),iron)]
for x in (-.794,.794):
    for y in (-.30,.30):
        frame.append(box("Desk leg",(x,y,.42),(.085,.091,.791),iron,.012))
        frame.append(box("Squarish foot",(x,y,.025),(.125,.135,.050),rubber,.01))
    frame.append(box("Side brace",(x,0,.318),(.058,.59,.046),steel))
frame.append(box("Left drawer cabinet",(-.566,.024,.51),(.407,.65,.53),iron,.021))
for z in (.333,.500,.668):
    frame.append(box("Recessed front",(-.566,-.312,z),(.371,.028,.125),ox,.012))
    frame.append(box("Dark pull slot",(-.566,-.331,z+.017),(.193,.014,.027),rubber,.006))
    frame.append(box("Folded drawer pull",(-.566,-.344,z+.024),(.134,.026,.018),steel,.004))
    for x in (-.714,-.418):
        frame.append(rod("Recessed rivet",(x,-.329,z),(x,-.337,z),.009,steel))
access=[
    box("Padded work zone",(.165,-.047,.907),(.62,.44,.013),rubber,.009),
    box("Lamp weighted base",(.614,.240,.918),(.21,.17,.037),iron,.012),
    box("Ledger",(-.552,.073,.918),(.26,.335,.039),ox,.012),
    box("Ledger pages",(-.546,.071,.926),(.245,.321,.029),paper,.007),
    box("Ledger cover",(-.553,.075,.945),(.266,.34,.011),iron,.005),
    box("Ledger spine marker",(-.661,.075,.952),(.032,.33,.006),wood_edge,.002),
]
a=(.614,.240,.934);b=(.614,.240,1.226);c=(.493,.190,1.367);d=(.373,.161,1.349)
access.extend([rod("Lamp lower arm",a,b,.026,iron),rod("Lamp upper arm",b,c,.021,steel),
               rod("Lamp crown brace",c,d,.021,iron),
               rod("Pressed lamp shade",(.366,.162,1.275),(.366,.162,1.361),.139,iron,.076),
               rod("Warm lens",(.366,.162,1.267),(.366,.162,1.278),.111,warm)])
for x,y,z in (b,c):
    access.append(rod("Pivot pin",(x,y-.032,z),(x,y+.032,z),.038,ox))
export(DESK,[join("Foreman_Desk_Geometry",frame),join("Analog_Lamp_And_Ledger",access)])
clear_scene()

# Readable fictional pickup object, no real credential or access data. XY flat, Z=0 bottom.
parts=[box("Base keycard",(0,0,.004),(.143,.087,.008),cardbody,.003),
       box("Graphite inlay",(0,0,.008),(.132,.076,.003),rubber,.001),
       box("Painted cyan bar",(-.033,0,.010),(.038,.012,.002),cyan,.001),
       box("Cyan corner indicator",(.050,.020,.010),(.013,.012,.002),cyan,.001)]
# Vault pictogram echoes the ring-and-slot marking of the orange Training Vault.
parts.extend([rod("Keyhole circle",(.025,.002,.009),(.025,.002,.011),.013,ivory),
              box("Keyhole stem",(.025,-.009,.0104),(.012,.022,.002),ivory,.001)])
for x in (-.055,-.045,-.035,-.025):
    parts.append(box("Inventory mark",(x,-.020,.010),(.003,.008,.002),steel,.0006))
export(CARD,[join("Vault_Keycard_Quest_Prop",parts)])

if os.getenv("WSC_KEYCARD_RENDER")=="1":
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(OUT/DESK))
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(OUT/CARD))
    card,=[o for o in set(bpy.context.scene.objects)-before if o.type=="MESH"]
    card.location=(.21,-.115,.914);card.rotation_euler.z=math.radians(13)
    box("Studio ground",(0,0,-.052),(100,100,.10),mat("Blue slate",0x344550,.91),0)
    s=bpy.context.scene;s.world.color=(.22,.24,.27)
    def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
    for p,power,size,color in [
        ((-3,-4,5),550,3,(1,.85,.67)),((4,-1,4),330,3,(.62,.83,1)),
        ((0,4,4),710,3,(.72,.86,1)),((.366,.16,1.257),4,.19,(1,.58,.30))]:
        bpy.ops.object.light_add(type="AREA",location=p)
        o=bpy.context.object;o.data.energy=power;o.data.size=size;o.data.color=color
        aim(o,(0,0,.6) if power>4 else (.21,-.115,.916))
    bpy.ops.object.camera_add(location=(2.05,-4.3,3.14))
    s.camera=bpy.context.object;aim(s.camera,(0,0,.705))
    s.camera.data.type="ORTHO";s.camera.data.ortho_scale=2.86
    s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
    s.render.resolution_x=1440;s.render.resolution_y=1020;s.render.resolution_percentage=100
    s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=90
    s.render.filepath=str(OUT/"e5b-keycard-desk-reimport.jpg")
    bpy.ops.render.render(write_still=True)
    s.camera.location=(.50,-.75,1.54);aim(s.camera,(.213,-.114,.916))
    s.camera.data.ortho_scale=.275
    s.render.resolution_x=1100;s.render.resolution_y=900
    s.render.filepath=str(OUT/"e5b-vault-keycard-detail.jpg")
    bpy.ops.render.render(write_still=True)

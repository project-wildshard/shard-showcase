"""E11c C2 reveal lift art: fixed frame and moving 6 m landing, built separately."""
import math, os, sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory
OUT=output_directory()
FRAME="wsc-kit-009-reveal-lift-frame.glb"
DECK="wsc-kit-009-reveal-lift-deck.glb"
clear_scene()

def material(n,c,rough=.6,metal=.4,glow=0):
    def lin(x):return x/12.92 if x<.04045 else ((x+.055)/1.055)**2.4
    rgba=tuple(lin((c>>s&255)/255) for s in (16,8,0))+(1,)
    m=bpy.data.materials.new(n);m.diffuse_color=rgba;m.use_nodes=True
    b=m.node_tree.nodes.get("Principled BSDF")
    for key,value in [('Base Color',rgba),('Roughness',rough),('Metallic',metal),
         ('Emission Color',rgba),('Emission Strength',glow)]:
        b.inputs[key].default_value=value
    return m

dark=material("Black machine steel",0x222d34,.63,.55)
iron=material("Galvanized structural steel",0x4c616a,.52,.62)
edge=material("Worn flanges",0x7c8e91,.57,.55)
paint=material("Old safety ochre",0xc18038,.64,.35)
brick=material("Panelled pit liner",0x55595a,.82,.2)
tread=material("Shot peened deck",0x666c68,.77,.39)
cyan=material("Cold passive markers",0x54bdbd,.43,.38,.45)

def box(n,p,d,m,w=.02,rot=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if w:
        f=o.modifiers.new("Worn edges","BEVEL");f.width=w;f.segments=1
        bpy.ops.object.modifier_apply(modifier=f.name)
    o.rotation_euler.z=rot;o.data.materials.append(m)
    return o

def stud(n,p,rad,height,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=rad,depth=height,location=p)
    o=bpy.context.object;o.name=n;o.data.materials.append(mat)
    return o

def export(name,node,items):
    bpy.ops.object.select_all(action="DESELECT")
    for o in items:o.select_set(True)
    bpy.context.view_layer.objects.active=items[0]
    bpy.ops.object.join()
    o=bpy.context.object;o.name=node
    bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/name),export_format="GLB",
        use_selection=True,export_animations=False,export_texcoords=False)

fixed=[]
for s in (-1,1):
    for transpose in (False,True):
        def v(x,y,z):return (y,x,z) if transpose else (x,y,z)
        fixed.extend([
            box("Machined landing flange",v(s*3.275,0,-.10),v(.43,6.12 if transpose else 6.98,.20),iron),
            box("Recessed long pit wall",v(s*3.26,0,-.82),v(.34,6.18 if transpose else 6.86,1.40),brick,.025),
            box("Captured guide strip",v(s*3.095,0,-.74),v(.07,5.96,1.03),dark,.006),
            box("Flange edge strip",v(s*3.393,0,-.012),v(.06,6.72 if transpose else 6.84,.024),paint,.006),
        ])
        for t in (-2.60,-1.30,0,1.30,2.60):
            fixed.append(stud("Flush fixing",v(s*3.270,t,-.017),.066,.033,edge))
        for t in (-2.21,-.75,.75,2.21):
            fixed.append(box("Recessed curb marker",v(s*3.176,t,-.014),v(.085,.24,.028),cyan,.008))
for s in (-1,1):
    fixed.extend([
        box("Shaft sleeve", (s*.88,0,-1.12), (.22,1.98,.90), dark,.034),
        box("Shaft sleeve", (0,s*.88,-1.12), (1.54,.22,.90), dark,.034),
    ])
export(FRAME,"C2_Lift_Fixed_Frame",fixed)
clear_scene()

moving=[box("Machined deck edge",(0,0,-.115),(6,6,.223),iron,.055),
        box("Recessed carriage deck",(0,0,-.41),(5.70,5.70,.40),dark,.073),
        box("Sliding carriage spine",(0,0,-2.769),(1.36,1.36,4.38),iron,.083)]
for x in (-2,-.0,2):
    for y in (-2,0,2):
        moving.append(box("Textured inset panel",(x*.938,y*.938,-.023),(1.853,1.853,.046),tread,.022))
for s in (-1,1):
    for y in (-.55,.55):
        moving.append(box("Vertical carriage groove",(s*.679,y,-2.642),(.047,.107,3.94),dark,.011))
    for x in (-2.4,-1.6,-.8,0,.8,1.6,2.4):
        moving.append(box("Amber inset tread",(x,s*2.89,-.014),(.345,.10,.028),paint,.014,s*math.pi/24))
    for x in (-2.17,2.17):
        moving.append(box("False guide shoe",(x,s*2.846,-.377),(.51,.236,.278),edge,.022))
    moving.append(box("Raised-state edge marker",(0,s*2.987,-.377),(2.34,.026,.058),cyan,.01))
export(DECK,"C2_Lift_Moving_Deck",moving)

if os.getenv("WSC_LIFT_RENDER")=="1":
    clear_scene()
    def instantiate(file,p):
        before=set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(OUT/file))
        ob,=[o for o in set(bpy.context.scene.objects)-before if o.type=="MESH"]
        ob.location=p
    for x,h in [(-4.43,0),(4.43,4)]:
        instantiate(FRAME,(x,0,0));instantiate(DECK,(x,0,h))
        # Studio cutaway plinth. Its floor masks the lowered carriage without adding to either GLB.
        for z,dist in [(-1.61,7.69)]:
            box("Studio cutaway base",(x,0,z),(dist,dist,.30),dark,.055)
    box("Studio ground",(0,0,-1.974),(200,200,.25),material("Studio background",0x3b4a55,.90,.05),0)
    s=bpy.context.scene;s.world.color=(.24,.28,.31)
    def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
    for p,power,size,c in [
        ((-8,-12,14),5900,10,(1,.84,.68)),((9,-5,12),4400,7,(.67,.83,1)),
        ((0,12,13),6200,8,(.81,.89,1))]:
        bpy.ops.object.light_add(type="AREA",location=p)
        o=bpy.context.object;o.data.energy=power;o.data.size=size;o.data.color=c;aim(o,(0,0,1))
    bpy.ops.object.camera_add(location=(10,-22,17))
    s.camera=bpy.context.object;aim(s.camera,(0,0,1))
    s.camera.data.type="ORTHO";s.camera.data.ortho_scale=22
    s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
    s.render.resolution_x=1440;s.render.resolution_y=1030;s.render.resolution_percentage=100
    s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=90
    s.render.filepath=str(OUT/"e11c-reveal-lift-reimport.jpg")
    bpy.ops.render.render(write_still=True)

"""Blender 4.3.2 source for the shared W1a town bot studies."""
import json
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

OUT=output_directory()
ROLES=(("001","stable-hand"),("002","weapons-keeper"))
SURVEYOR=os.getenv("WSC_TOWN_SURVEYOR")=="1"
ROOK=os.getenv("WSC_TOWN_ROOK")=="1"
if SURVEYOR and ROOK:
    raise ValueError("Select one role build at a time.")
# Blender Z up, front -Y; glTF Y up, front +Z. Right is negative X.
BONES=[
 ("hips",None,(0,0,.92)),("spine","hips",(0,0,1.04)),
 ("chest","spine",(0,0,1.22)),("neck","chest",(0,0,1.48)),
 ("head","neck",(0,0,1.57)),
]
for s,k in ((-1,"R"),(1,"L")):
    for n,p,x,y,z in [
        ("clavicle","chest",.115,0,1.39),("shoulder","clavicle",.258,0,1.37),
        ("twist","shoulder",.321,-.008,1.265),("elbow","twist",.391,-.016,1.15),
        ("hand","elbow",.458,-.047,.936),
    ]:
        BONES.append((n+k,p if p=="chest" else p+k,(s*x,y,z)))
for s,k in ((-1,"R"),(1,"L")):
    BONES.extend([("thigh"+k,"hips",(s*.125,0,.88)),
                  ("shin"+k,"thigh"+k,(s*.148,-.019,.54)),
                  ("foot"+k,"shin"+k,(s*.151,0,.174))])

COLORS={
    "rubber":0x272c2d,"iron":0x45535a,"alloy":0x8e9694,"edge":0xb1b9b2,
    "glass":0x181d1d,"eye":0xffbc41,"vest":0xcb772e,"clay":0x9a552b,
    "canvas":0xddd0ac,"thread":0x9a8869,"navy":0x3c506a,"lapel":0x62758a,
    "denim":0x2e4057,"copper":0xeb9852,"buckles":0x987854,"weld":0x59676e,
}
TILES={key:(i%4,i//4) for i,key in enumerate(COLORS)}


def palette():
    m=bpy.data.materials.new("W1a common body and costume atlas")
    m.use_nodes=True
    nodes=m.node_tree.nodes
    q=nodes.get("Principled BSDF")
    q.inputs["Roughness"].default_value=.68
    for kind, socket in (("albedo","Base Color"),("signal","Emission Color")):
        f=OUT/("w1a-"+kind+".png")
        # A deterministic RGBA atlas, no external bake, dependency or source image.
        import binascii,struct,zlib
        def chunk(t,d):return struct.pack(">I",len(d))+t+d+struct.pack(">I",binascii.crc32(t+d))
        rows=[]
        order=list(COLORS)
        for y in range(64):
            scan=bytearray([0])
            for x in range(64):
                key=order[((63-y)//16)*4+x//16]
                c=COLORS[key] if kind=="albedo" else (0xf38f1b if key=="eye" else 0)
                scan.extend((c>>16&255,c>>8&255,c&255,255))
            rows.append(scan)
        f.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",64,64,8,6,0,0,0))
                      +chunk(b"IDAT",zlib.compress(b"".join(rows)))+chunk(b"IEND",b""))
        im=bpy.data.images.load(str(f),check_existing=True);im.pack()
        t=nodes.new("ShaderNodeTexImage");t.name=kind;t.image=im;t.interpolation="Closest"
        m.node_tree.links.new(t.outputs["Color"],q.inputs[socket])
    q.inputs["Emission Strength"].default_value=.8
    return m


class Bot:
    def __init__(self):
        self.parts=[]
        self.mat=palette()
    def attach(self,ob,key,joint):
        ob.data.materials.clear();ob.data.materials.append(self.mat)
        uv=ob.data.uv_layers.active or ob.data.uv_layers.new()
        uv.name="Role_Atlas"
        x,y=TILES[key]
        # Sample the exact swatch center; there is no timing-dependent bake.
        for u in uv.data:u.uv=((x+.5)/4,(y+.5)/4)
        g=ob.vertex_groups.new(name=joint)
        g.add(list(range(len(ob.data.vertices))),1,"REPLACE")
        self.parts.append(ob)
        return ob
    def box(self,j,key,p,d,b=.018,rot=None):
        bpy.ops.mesh.primitive_cube_add(size=1,location=p)
        ob=bpy.context.object;ob.dimensions=d
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        if b:
            mod=ob.modifiers.new("Soft stamped edges","BEVEL");mod.width=b;mod.segments=1
            bpy.ops.object.modifier_apply(modifier=mod.name)
        if rot is not None:ob.rotation_euler=rot
        return self.attach(ob,key,j)
    def rod(self,j,key,a,b,r,s=10,r_top=None):
        a,b=Vector(a),Vector(b)
        bpy.ops.mesh.primitive_cone_add(vertices=s,radius1=r,radius2=r_top if r_top is not None else r,
                                      depth=(b-a).length,location=(a+b)/2)
        ob=bpy.context.object;ob.rotation_euler=(b-a).to_track_quat("Z","Y").to_euler()
        return self.attach(ob,key,j)
    def plate(self,j,key,front,depth=.025):
        # Clockwise outline as seen from the front; extruded toward the actor.
        v=front+[(x,y+depth,z) for x,y,z in front]
        n=len(front)
        faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
        faces.extend((i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n))
        mesh=bpy.data.meshes.new(key);mesh.from_pydata(v,[],faces)
        ob=bpy.data.objects.new(key,mesh);bpy.context.collection.objects.link(ob)
        return self.attach(ob,key,j)

    def finish(self,slug):
        bpy.ops.object.select_all(action="DESELECT")
        for ob in self.parts:ob.select_set(True)
        bpy.context.view_layer.objects.active=self.parts[0]
        bpy.ops.object.join()
        mesh=bpy.context.object;mesh.name="W1a_"+slug
        bpy.context.scene.cursor.location=(0,0,0)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        # Correct outward winding for every closed stamped part.
        bpy.ops.object.mode_set(mode="EDIT");bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode="OBJECT")
        arm=bpy.data.armatures.new("W1a dev-bot common rig")
        rig=bpy.data.objects.new("W1a_Rig",arm);bpy.context.collection.objects.link(rig)
        bpy.context.view_layer.objects.active=rig;rig.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        for name,parent,p in BONES:
            b=arm.edit_bones.new(name);b.head=p;b.tail=Vector(p)+Vector((0,0,.080))
            if parent:b.parent=arm.edit_bones[parent]
        bpy.ops.object.mode_set(mode="OBJECT")
        mesh.parent=rig
        mod=mesh.modifiers.new("Common rig","ARMATURE");mod.object=rig
        s=bpy.context.scene;s.render.fps=24;s.frame_end=73
        for name,amp in (("chest",.016),("head",.070),("elbowR",.062),("elbowL",.050)):
            b=rig.pose.bones[name];b.rotation_mode="XYZ"
            for f in (1,13,25,37,49,61,73):
                phase=(f-1)*math.tau/72
                b.rotation_euler=(amp*math.sin(phase),amp*.54*(math.cos(phase)-1),0)
                b.keyframe_insert(data_path="rotation_euler",frame=f,group=name)
        rig.animation_data.action.name="Idle_Studio"
        s.frame_set(1)
        bpy.ops.object.select_all(action="DESELECT");rig.select_set(True);mesh.select_set(True)
        return rig,mesh


def build(stable,slug,surveyor=False,rook=False):
    clear_scene()
    b=Bot()
    shell="vest" if stable or surveyor or rook else "navy"
    seam="clay" if stable or surveyor or rook else "denim"
    b.box("hips","iron",(0,0,.925),(.33,.252,.175),.041)
    b.box("spine","rubber",(0,0,1.083),(.30,.219,.21),.046)
    b.box("chest",shell,(0,0,1.285),(.465,.32,.34),.072)
    b.box("chest",seam,(0,.143,1.296),(.339,.045,.220),.022)
    b.box("chest","iron",(0,.177,1.32),(.181,.030,.120),.014)
    for i in range(3):b.box("chest","weld",(0,.194,1.29+.029*i),(.13,.009,.008),.002)
    for z in (1.474,1.502,1.530):
        b.rod("neck","rubber",(0,0,z),(0,0,z+.021),.084)
    b.box("head","iron",(0,-.002,1.660),(.370,.303,.276),.049)
    b.box("head","alloy",(0,-.129,1.672),(.342,.102,.229),.036)
    b.box("head","weld",(0,.053,1.788),(.233,.164,.035),.012)
    b.box("head","glass",(0,-.185,1.660),(.285,.022,.075),.015)
    b.box("head","eye",(0,-.200,1.665),(.239,.012,.026),.009)
    b.box("head","edge",(0,-.174,1.595),(.205,.025,.029),.009)
    b.box("hips","rubber",(0,-.008,.98),(.40,.288,.074),.021)
    for side,k in ((-1,"R"),(1,"L")):
        def n(j):return j+k
        x=lambda v:side*v
        b.rod("head","rubber",(x(.159),0,1.654),(x(.213),0,1.654),.082)
        b.rod("head","weld",(x(.205),0,1.654),(x(.225),0,1.654),.063)
        b.rod("head","alloy",(x(.222),0,1.654),(x(.232),0,1.654),.045)
        b.box(n("shoulder"),"rubber",(x(.26),0,1.359),(.135,.190,.163),.039)
        b.box(n("twist"),"alloy" if stable or surveyor or rook else shell,(x(.313),-.007,1.291),
              (.145,.169,.202),.031,(0,-side*.52,0))
        b.box(n("twist"),"weld",(x(.365),-.01,1.205),(.108,.119,.11),.025,(0,-side*.52,0))
        b.rod(n("elbow"),"rubber",(x(.392),.047,1.151),(x(.392),-.076,1.151),.049)
        b.rod(n("elbow"),"edge",(x(.392),-.074,1.151),(x(.392),-.087,1.151),.034)
        b.rod(n("elbow"),"alloy",(x(.409),-.024,1.106),(x(.453),-.043,.965),.065,8,.043)
        b.box(n("elbow"),"edge",(x(.427),-.075,1.045),(.072,.028,.104),.01,(0,-side*.25,0))
        b.rod(n("hand"),"rubber",(x(.456),-.046,.968),(x(.463),-.054,.918),.042)
        if not stable and not surveyor and not rook:b.rod(n("hand"),"copper",(x(.457),-.046,.967),(x(.460),-.05,.948),.050)
        b.box(n("hand"),"iron",(x(.472),-.063,.895),(.077,.084,.089),.018,(0,-side*.16,0))
        for idx in range(3):
            y=-.093+idx*.026
            b.rod(n("hand"),"weld",(x(.486),y,.870),(x(.489),y-.005,.819),.012,6,.009)
        b.rod(n("hand"),"alloy",(x(.447),-.103,.907),(x(.434),-.112,.865),.015,6,.012)
        b.box(n("thigh"),"weld",(x(.134),0,.696),(.165,.169,.273),.039)
        b.rod(n("shin"),"rubber",(x(.148),.080,.546),(x(.148),-.097,.546),.066)
        b.rod(n("shin"),"alloy",(x(.148),-.096,.546),(x(.148),-.106,.546),.046)
        b.rod(n("shin"),"iron",(x(.151),0,.209),(x(.148),-.011,.473),.068,8,.087)
        b.box(n("shin"),"alloy",(x(.15),-.072,.346),(.107,.043,.230),.015)
        b.box(n("foot"),"rubber",(x(.154),-.058,.025),(.218,.326,.050),.018)
        b.box(n("foot"),"iron",(x(.154),-.057,.088),(.199,.302,.118),.027)
        b.box(n("foot"),"alloy",(x(.154),-.142,.124),(.173,.115,.052),.017)
        b.box(n("foot"),"clay" if stable else ("weld" if surveyor or rook else "copper"),(x(.154),-.143,.154),(.052,.079,.014),.004)
        b.box(n("foot"),"weld",(x(.152),-.005,.167),(.161,.145,.075),.020)
        if stable:
            b.box("chest","canvas",(x(.132),-.162,1.353),(.041,.027,.183),.009,(0,side*.13,0))
            b.box("spine","clay",(x(.179),-.161,1.055),(.099,.057,.136),.014)
            b.box("spine","vest",(x(.179),-.194,1.085),(.102,.022,.048),.008)
            b.rod("spine","buckles",(x(.179),-.205,1.090),(x(.179),-.211,1.090),.010,8)
        elif surveyor:
            # Reflective tape wraps both sides of the vest; retained atlas swatches.
            b.box("chest","edge",(x(.151),-.173,1.340),(.039,.024,.207),.008,(0,side*.05,0))
            b.box("chest","edge",(x(.149),.174,1.337),(.039,.017,.196),.006,(0,-side*.06,0))
            b.box("chest","edge",(x(.126),-.171,1.224),(.169,.023,.025),.006)
            b.box("chest","edge",(x(.133),.182,1.226),(.174,.018,.025),.006)
            b.box("spine","vest",(x(.121),-.158,1.107),(.136,.053,.154),.019)
            b.box("spine","clay",(x(.121),-.192,1.139),(.141,.020,.035),.006)
            b.box("spine","buckles",(x(.122),-.204,1.135),(.027,.011,.015),.004)
            b.box(n("elbow"),"weld",(x(.435),-.10,1.013),(.112,.021,.097),.017,(0,-side*.23,0))
        elif rook:
            # W04 shop keeper and WSC-ACTOR-018 brown leather shop apron.
            b.box("chest","edge",(x(.122),-.171,1.367),(.034,.024,.182),.006,(0,-side*.065,0))
            b.box("chest","canvas",(x(.124),.179,1.343),(.036,.022,.222),.006,(0,side*.07,0))
            b.box("chest","clay",(x(.170),-.173,1.356),(.045,.028,.197),.008,(0,side*.10,0))
            b.box("chest","clay",(x(.167),.185,1.349),(.044,.024,.192),.006)
            shoulder=[(-.176,1.436),(-.11,1.457),(-.066,1.466),(.072,1.466),(.141,1.450),(.184,1.427)]
            for (a,z0),(c,z1) in zip(shoulder,shoulder[1:]):
                b.box("chest","clay",(x(.168),(a+c)/2,(z0+z1)/2),
                      (.046,math.hypot(c-a,z1-z0)+.014,.024),.004,
                      (math.atan2(z1-z0,c-a),0,0))
            b.box("spine","clay",(x(.210),-.123,1.004),(.068,.112,.155),.013)
            b.box("hips","clay",(x(.207),-.159,.824),(.086,.118,.231),.020)
            b.box("hips","thread",(x(.212),-.222,.893),(.081,.031,.057),.009)
            b.rod("hips","buckles",(x(.213),-.241,.889),(x(.213),-.247,.889),.014,8)
            b.rod("head","weld",(x(.231),0,1.654),(x(.251),0,1.654),.064,10)
            b.rod("head","alloy",(x(.249),0,1.654),(x(.256),0,1.654),.046,10)
        else:
            b.plate("chest","lapel",[(x(.038),-.177,1.288),(x(.177),-.156,1.39),
                (x(.113),-.135,1.465),(x(.079),-.164,1.411)])
            b.box(n("twist"),"lapel",(x(.358),-.01,1.245),(.144,.181,.057),.013,(0,-side*.52,0))
            b.plate(n("thigh"),"denim",[(x(.017),-.156,.970),(x(.027),-.166,.57),
                (x(.224),-.143,.585),(x(.180),-.137,.970)])
            b.plate(n("thigh"),"navy",[(x(.026),.149,.97),(x(.027),.142,.585),
                (x(.220),.129,.585),(x(.168),.143,.97)])
            b.box(n("thigh"),"navy",(x(.129),-.175,.757),(.143,.037,.139),.015)
            b.box(n("thigh"),"lapel",(x(.129),-.197,.796),(.144,.021,.045),.009)
            for px in (.085,.175):
                b.rod(n("thigh"),"buckles",(x(px),-.207,.796),(x(px),-.213,.796),.009,8)
    if stable:
        b.plate("spine","canvas",[(-.141,-.181,1.307),(-.207,-.181,.616),
                                  (.207,-.181,.616),(.141,-.181,1.307)])
        b.box("spine","thread",(0,-.198,.788),(.256,.022,.132),.014)
        b.box("spine","canvas",(0,-.213,.794),(.231,.013,.111),.012)
        # Stable badge: roof, small horse-head silhouette and fence rails.
        for a,c in [((-.078,1.190),(0,1.242)),((0,1.242),(.078,1.190)),
                    ((-.059,1.191),(-.059,1.105)),((.059,1.191),(.059,1.105)),
                    ((-.075,1.122),(.073,1.122))]:
            b.rod("spine","thread",(a[0],-.194,a[1]),(c[0],-.194,c[1]),.006,6)
        b.plate("spine","thread",[(-.029,-.204,1.139),(-.024,-.204,1.192),(.01,-.204,1.213),
            (.017,-.204,1.193),(.040,-.204,1.173),(.023,-.204,1.160),
            (.005,-.204,1.174),(-.005,-.204,1.141)],.003)
        for k in (-1,1):
            b.box("hips","canvas",(k*.060,.167,.956),(.115,.038,.042),.014,(0,k*.34,0))
            b.box("hips","canvas",(k*.044,.166,.883),(.035,.031,.140),.009,(0,-k*.33,0))
    elif surveyor:
        b.box("spine","vest",(0,.034,1.128),(.372,.23,.105),.025)
        b.box("chest","rubber",(0,-.169,1.319),(.023,.014,.186),.004)
        # Compact optics on the right temple plus a chest-worn slate; a distinct silhouette, not new tools.
        b.box("head","iron",(-.205,-.04,1.697),(.124,.165,.145),.022)
        b.box("head","alloy",(-.217,-.133,1.696),(.082,.023,.085),.01)
        b.rod("head","glass",(-.217,-.144,1.696),(-.217,-.158,1.696),.031,12)
        b.rod("head","lapel",(-.217,-.156,1.696),(-.217,-.163,1.696),.022,12)
        b.box("chest","iron",(.098,-.196,1.345),(.109,.034,.076),.012)
        b.box("chest","lapel",(.098,-.219,1.349),(.084,.011,.052),.005)
        for z0,x0 in [(1.331,.089),(1.346,.097),(1.362,.103)]:
            b.box("chest","edge",(x0,-.226,z0),(.052,.010,.005),.001)
        # Rear triangular survey datum on an atlas-colored id plate.
        for a,c in [((-.065,1.300),(0,1.386)),((0,1.386),(.065,1.300)),
                    ((-.065,1.300),(.065,1.300))]:
            b.rod("chest","navy",(a[0],.202,a[1]),(c[0],.202,c[1]),.006,6)
    elif rook:
        b.plate("spine","clay",[(-.173,-.182,1.239),(-.211,-.185,.975),
                                 (.211,-.185,.975),(.173,-.182,1.239)],.053)
        b.plate("hips","clay",[(-.201,-.185,.991),(-.209,-.197,.738),
                                (.209,-.197,.738),(.201,-.185,.991)],.046)
        b.box("spine","thread",(0,-.218,1.135),(.233,.035,.126),.013)
        b.box("spine","clay",(0,-.241,1.138),(.210,.020,.106),.011)
        b.box("hips","thread",(0,-.221,.870),(.248,.054,.158),.018)
        b.box("hips","clay",(0,-.253,.872),(.225,.023,.133),.012)
        b.box("hips","iron",(0,.010,1.002),(.431,.342,.054),.016)
        b.box("hips","thread",(0,.185,1.005),(.380,.029,.052),.009)
        for x in (-.146,.146):
            for z in (.902,1.187,1.218):
                y=-.273 if z==.902 else -.236
                b.rod("hips" if z<1 else "spine","buckles",(x,y,z),(x,y-.009,z),.011,8)
        # Single worn maker plate; restrained asymmetry against the visible gold slit.
        b.box("head","weld",(-.105,.153,1.685),(.108,.036,.079),.010)
        for i in range(3):
            b.box("head","buckles",(-.133+.026*i,.176,1.685),(.013,.012,.048),.003)
        b.box("head","iron",(0,-.180,1.657),(.304,.027,.094),.018)
        b.box("head","glass",(0,-.199,1.661),(.276,.021,.063),.012)
        b.box("head","eye",(0,-.213,1.661),(.232,.011,.029),.008)
    else:
        b.box("hips","alloy",(0,-.167,.977),(.104,.036,.065),.012)
        b.box("hips","rubber",(0,-.186,.977),(.067,.012,.037),.006)
        b.box("chest","denim",(-.126,-.169,1.234),(.094,.027,.102),.011)
        for k in range(3):b.box("chest","copper",(-.155+.028*k,-.188,1.264),(.022,.022,.029),.004)
        for z in (1.101,1.202):b.rod("chest","alloy",(0,-.165,z),(0,-.181,z),.016,8)
    b.finish(slug)


for code,slug in ((("017","surveyor"),) if SURVEYOR else ((("018","tinker-rook"),) if ROOK else ROLES)):
    build(code=="001",slug,surveyor=SURVEYOR,rook=ROOK)
    filename=f"wsc-actor-{code}-{slug}.glb" if SURVEYOR or ROOK else f"wsc-plan-{code}-{slug}.glb"
    bpy.ops.export_scene.gltf(filepath=str(OUT/filename),
        export_format="GLB",use_selection=True,export_animations=True,export_apply=False,
        export_animation_mode="ACTIVE_ACTIONS",export_force_sampling=True)

(OUT/"w1a-rest-landmarks.json").write_text(json.dumps({
    "space":"mesh-local metres, glTF Y up, front +Z",
    "joints":[dict(name=n,parent=p,rest=[x,z,-y]) for n,p,(x,y,z) in BONES],
    "approximate_ground_toe_RL":[[-.154,0,.154],[.154,0,.154]],
},indent=2)+"\n")

if not SURVEYOR and not ROOK and os.getenv("WSC_TOWN_BOT_RENDER")=="1":
    clear_scene()
    for offset,(code,slug) in zip((-.76,.76),ROLES):
        before=set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(OUT/f"wsc-plan-{code}-{slug}.glb"))
        for o in set(bpy.context.scene.objects)-before:
            if o.parent is None:o.location.x+=offset
    bpy.ops.mesh.primitive_plane_add(size=200)
    floor=bpy.data.materials.new("Studio clay")
    floor.diffuse_color=(.16,.21,.22,1)
    bpy.context.object.data.materials.append(floor)
    s=bpy.context.scene;s.frame_set(18);s.world.color=(.28,.28,.28)
    def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
    for p,power,size,color in [
        ((-3,-4,5),720,4,(1,.83,.65)),((4,-2,3),410,3,(.68,.84,1)),
        ((0,3,4),960,3,(1,.80,.56)),
    ]:
        bpy.ops.object.light_add(type="AREA",location=p);o=bpy.context.object
        o.data.energy=power;o.data.size=size;o.data.color=color;aim(o,(0,0,1))
    bpy.ops.object.camera_add(location=(2.35,-7.3,2.5))
    s.camera=bpy.context.object;aim(s.camera,(0,0,.94))
    s.camera.data.type="ORTHO";s.camera.data.ortho_scale=3.35
    s.render.engine="CYCLES";s.cycles.samples=48;s.cycles.use_denoising=False
    s.render.resolution_x=1440;s.render.resolution_y=1050;s.render.resolution_percentage=100
    s.render.image_settings.file_format="JPEG";s.render.image_settings.quality=90
    s.render.filepath=str(OUT/"w1a-town-bots-reimport.jpg")
    bpy.ops.render.render(write_still=True)

"""Blender 4.3.2 source for the shared W1a stable hand / weapons keeper studies."""
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


def build(stable,slug):
    clear_scene()
    b=Bot()
    shell="vest" if stable else "navy"
    seam="clay" if stable else "denim"
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
        b.box(n("twist"),"alloy" if stable else shell,(x(.313),-.007,1.291),
              (.145,.169,.202),.031,(0,-side*.52,0))
        b.box(n("twist"),"weld",(x(.365),-.01,1.205),(.108,.119,.11),.025,(0,-side*.52,0))
        b.rod(n("elbow"),"rubber",(x(.392),.047,1.151),(x(.392),-.076,1.151),.049)
        b.rod(n("elbow"),"edge",(x(.392),-.074,1.151),(x(.392),-.087,1.151),.034)
        b.rod(n("elbow"),"alloy",(x(.409),-.024,1.106),(x(.453),-.043,.965),.065,8,.043)
        b.box(n("elbow"),"edge",(x(.427),-.075,1.045),(.072,.028,.104),.01,(0,-side*.25,0))
        b.rod(n("hand"),"rubber",(x(.456),-.046,.968),(x(.463),-.054,.918),.042)
        if not stable:b.rod(n("hand"),"copper",(x(.457),-.046,.967),(x(.460),-.05,.948),.050)
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
        b.box(n("foot"),"clay" if stable else "copper",(x(.154),-.143,.154),(.052,.079,.014),.004)
        b.box(n("foot"),"weld",(x(.152),-.005,.167),(.161,.145,.075),.020)
        if stable:
            b.box("chest","canvas",(x(.132),-.162,1.353),(.041,.027,.183),.009,(0,side*.13,0))
            b.box("spine","clay",(x(.179),-.161,1.055),(.099,.057,.136),.014)
            b.box("spine","vest",(x(.179),-.194,1.085),(.102,.022,.048),.008)
            b.rod("spine","buckles",(x(.179),-.205,1.090),(x(.179),-.211,1.090),.010,8)
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
    else:
        b.box("hips","alloy",(0,-.167,.977),(.104,.036,.065),.012)
        b.box("hips","rubber",(0,-.186,.977),(.067,.012,.037),.006)
        b.box("chest","denim",(-.126,-.169,1.234),(.094,.027,.102),.011)
        for k in range(3):b.box("chest","copper",(-.155+.028*k,-.188,1.264),(.022,.022,.029),.004)
        for z in (1.101,1.202):b.rod("chest","alloy",(0,-.165,z),(0,-.181,z),.016,8)
    b.finish(slug)


for code,slug in ROLES:
    build(code=="001",slug)
    bpy.ops.export_scene.gltf(filepath=str(OUT/f"wsc-plan-{code}-{slug}.glb"),
        export_format="GLB",use_selection=True,export_animations=True,export_apply=False,
        export_animation_mode="ACTIVE_ACTIONS",export_force_sampling=True)

(OUT/"w1a-rest-landmarks.json").write_text(json.dumps({
    "space":"mesh-local metres, glTF Y up, front +Z",
    "joints":[dict(name=n,parent=p,rest=[x,z,-y]) for n,p,(x,y,z) in BONES],
    "approximate_ground_toe_RL":[[-.154,0,.154],[.154,0,.154]],
},indent=2)+"\n")

if os.getenv("WSC_TOWN_BOT_RENDER")=="1":
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

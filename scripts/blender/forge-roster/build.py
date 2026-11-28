"""Batch original Wildshard weapons: tailored silhouette, rigid joints, useful sockets."""
from pathlib import Path
import bpy, bmesh, json, math, sys
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"art/weapons/forge-roster"
SCRATCH=Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else OUT
OUT.mkdir(parents=True,exist_ok=True);SCRATCH.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene;S.render.fps=30
# Each row is a unique silhouette, not just a skin; values are art metres.
# id, label, motion family, handle length, head thickness, accent, head outline.
rows=[
 ("015","Dock Cleaver","chop",.37,.105,(.89,.27,.074),[(-.10,.13),(.21,.15),(.27,.33),(.25,.94),(.11,1.15),(-.21,1.07),(-.19,.5),(-.12,.36)]),
 ("016","Line Pike","thrust",1.15,.055,(.10,.73,.64),[(-.095,.62),(.085,.62),(.085,.87),(.22,.98),(.19,1.14),(.07,1.25),(0,1.96),(-.105,1.31),(-.17,1.13),(-.19,.98),(-.085,.90)]),
 ("017","Rivet Maul","chop",.70,.24,(.81,.48,.13),[(-.39,.82),(-.29,.68),(-.12,.68),(-.12,.58),(.12,.58),(.15,.70),(.31,.70),(.43,.79),(.43,1.03),(.30,1.17),(-.29,1.17),(-.41,1.04)]),
 ("018","Harbor Hook","sweep",.54,.08,(.22,.58,.87),[(-.09,.18),(.12,.16),(.18,.45),(.36,.54),(.49,.69),(.51,.91),(.36,1.09),(.10,1.11),(-.02,.99),(.19,.98),(.32,.86),(.29,.73),(.17,.65),(-.06,.61),(-.13,.43)]),
 ("019","Cinder Axe","chop",.56,.085,(.91,.19,.085),[(-.15,.29),(.06,.31),(.17,.73),(.48,.88),(.52,1.09),(.42,1.28),(.24,1.16),(.01,1.05),(-.16,1.13),(-.29,.98),(-.28,.82),(-.09,.78)]),
 ("020","Relay Baton","sweep",.26,.13,(.62,.57,.96),[(-.1,.12),(.10,.12),(.088,.36),(.16,.46),(.16,.84),(.108,.98),(-.11,.98),(-.16,.85),(-.16,.47),(-.088,.37)]),
 ("021","Beacon Lance","thrust",.88,.08,(.95,.37,.10),[(-.10,.48),(.10,.48),(.13,.78),(.28,.98),(.28,1.27),(.18,1.37),(.15,1.08),(.045,1.16),(0,1.71),(-.06,1.17),(-.16,1.09),(-.21,1.40),(-.30,1.30),(-.28,.99),(-.12,.80)]),
 ("022","Slipfin","sweep",.32,.053,(.11,.76,.61),[(-.08,.13),(.08,.14),(.15,.29),(.09,.49),(.14,.74),(.08,1.04),(-.038,1.28),(-.18,1.13),(-.235,.87),(-.16,.65),(-.235,.46),(-.12,.37)]),
 ("023","Counterweight Flail","chop",.52,.11,(.80,.23,.34),[(-.33,.83),(-.23,.68),(-.08,.73),(0,.64),(.08,.73),(.23,.68),(.33,.83),(.31,1.09),(.20,1.21),(-.21,1.21),(-.34,1.07)]),
 ("024","Glassbreaker Fan","sweep",.30,.096,(.27,.71,.95),[(-.09,.13),(.10,.13),(.10,.33),(.42,.54),(.49,.72),(.25,.91),(0,.99),(-.28,.91),(-.49,.71),(-.42,.56),(-.10,.33)]),
 ("025","Rail Needle","thrust",.48,.053,(.93,.73,.23),[(-.07,.16),(.07,.16),(.085,.4),(.165,.48),(.112,.58),(.055,.68),(.04,1.48),(0,1.79),(-.044,1.48),(-.067,.67),(-.15,.54),(-.16,.43),(-.09,.37)]),
]

def mat(name,c,metal=.72,r=.33,em=0):
    a=bpy.data.materials.new(name);a.diffuse_color=(*c,1);a.use_nodes=True
    n=a.node_tree.nodes["Principled BSDF"];n.inputs["Base Color"].default_value=(*c,1);n.inputs["Metallic"].default_value=metal;n.inputs["Roughness"].default_value=r
    if em:n.inputs["Emission Color"].default_value=(*c,1);n.inputs["Emission Strength"].default_value=em
    return a
body=mat("Charcoal blue steel",(.065,.100,.123)); edge=mat("Tool nickel",(.25,.36,.42),.92,.24)
bronze=mat("Reclaimed bronze",(.42,.23,.085)); wrap=mat("Grip composite",(.034,.028,.030),.08,.56)
floor=mat("Forge floor",(.021,.033,.043),.16,.47)
label_material=mat("Printed labels",(.68,.82,.80),0,.48,.8)
def bevel(o,s):
    m=o.modifiers.new("Forged edges","BEVEL");m.width=s;m.segments=1
    n=o.modifiers.new("Facet normals","WEIGHTED_NORMAL");n.keep_sharp=True
def link(o,c,m):
    for old in list(o.users_collection):old.objects.unlink(o)
    c.objects.link(o);o.data.materials.append(m);return o
def tube(c,name,x,y,z,r,l,m,axis=True,v=10):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=l,location=(x,y,z),rotation=(math.pi/2,0,0) if axis else (0,0,0))
    o=bpy.context.object;o.name=name;link(o,c,m);bevel(o,min(r*.2,.014));return o
def slab(c,name,pts,z,t,m,back=None):
    n=len(pts);v=[(x,y,z+h) for h in (0,t) for x,y in pts]
    f=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    g=bpy.data.meshes.new(name);g.from_pydata(v,[],f)
    b=bmesh.new();b.from_mesh(g);bmesh.ops.recalc_face_normals(b,faces=list(b.faces));b.to_mesh(g);b.free();g.update()
    o=bpy.data.objects.new(name,g);c.objects.link(o);g.materials.append(m)
    if back:
        g.materials.append(back)
        for p in g.polygons:
            if len(p.vertices)==4:p.material_index=1
    bevel(o,min(t*.28,.021));return o
def aim(o,point):o.rotation_euler=(Vector(point)-o.location).to_track_quat("-Z","Y").to_euler()
def attach(o,rig,bone):
    w=o.matrix_world.copy();o.parent=rig;o.parent_type="BONE";o.parent_bone=bone
    bpy.context.view_layer.update();o.matrix_world=w
def clip(rig,name,keys):
    for f,(grip_z,grip_y,head_z) in keys:
        for n,z,y in (("grip",grip_z,grip_y),("head",head_z,0)):
            p=rig.pose.bones[n];p.rotation_euler.z=math.radians(z);p.location.y=y
            p.keyframe_insert(data_path="rotation_euler",frame=f,group=n);p.keyframe_insert(data_path="location",frame=f,group=n)
    a=rig.animation_data.action;a.name=name;rig.animation_data.action=None
    t=rig.animation_data.nla_tracks.new();t.name=name;t.strips.new(name,1,a)
for i,(id,label,family,handle,t,accent,poly) in enumerate(rows):
    c=bpy.data.collections.new(label);S.collection.children.link(c)
    m=mat(label+" enamel",accent,.34,.35,.21); base=min(y for _,y in poly);tip=max(poly,key=lambda q:q[1]);p=(0,0,0)
    tube(c,"Leather grip",0,-handle*.32,0,.049,handle*.47,wrap)
    tube(c,"Steel shaft",0,(base-handle)*.5,0,.037,base+handle,body)
    for k in range(5):tube(c,"Grip wrap",0,-handle*.13-k*handle*.085,0,.051,.013,bronze if k in (0,4) else wrap)
    tube(c,"Pommel",0,-handle+.035,0,.058,.06,bronze,v=6)
    lead=slab(c,"Forged profile",poly,-t*.5,t,body,edge)
    cx=sum(x for x,_ in poly)/len(poly);cy=sum(y for _,y in poly)/len(poly)
    main=[(cx+(x-cx)*.61,cy+(y-cy)*.64) for x,y in poly]
    detail=[]
    for sign in (-1,1):
        detail.append(slab(c,"Color-backed wear plate",main,sign*t*.5-(.008 if sign<0 else 0),.008,m))
        for x,y in [(cx-.035,cy-.085),(cx+.035,cy-.085),(cx,cy+.11)]:
            detail.append(tube(c,"Countersunk rivet",x,y,sign*(t*.5+.012),.012,.012,bronze,False,8))
    gd=bpy.data.armatures.new(label+" rig");rig=bpy.data.objects.new(id+" "+label,gd);c.objects.link(rig)
    bpy.ops.object.select_all(action="DESELECT");rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode="EDIT")
    core=gd.edit_bones.new("grip");core.head=(0,0,0);core.tail=(0,.08,0)
    h=gd.edit_bones.new("head");h.head=(0,base,0);h.tail=(0,base+.08,0);h.parent=core
    bpy.ops.object.mode_set(mode="OBJECT")
    for q in rig.pose.bones:q.rotation_mode="XYZ"
    for name,position in (("grip_socket",p),("tip_socket",(*tip,0))):
        o=bpy.data.objects.new(name,None);o.location=position;c.objects.link(o);bpy.context.view_layer.update()
        attach(o,rig,"head" if name=="tip_socket" else "grip")
    for o in c.objects:
        if o.type=="MESH":attach(o,rig,"head" if o in [lead,*detail] else "grip")
    if family=="thrust": hit=(0,.45,0);wind=(-13,-.175,-5)
    elif family=="chop":hit=(-49,.06,-8);wind=(45,-.05,7)
    else:hit=(-61,.08,-10);wind=(32,-.04,8)
    clip(rig,"Ready",[(1,(0,0,0)),(10,wind),(25,(0,0,0))])
    clip(rig,"Attack_"+family,[(1,(0,0,0)),(9,wind),(14,hit),(19,(-12,0,-3)),(31,(0,0,0))])
    bpy.ops.object.select_all(action="DESELECT")
    for o in c.objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/(id+".glb")),export_format="GLB",use_selection=True,export_apply=True,export_animation_mode="NLA_TRACKS")
    for o in c.objects:
        if o.type=="EMPTY" and o.name.endswith("_socket"):o.name=label+" • "+o.name
    for track in rig.animation_data.nla_tracks:track.mute=True
    S.frame_set(1)
    rig.location=((i%4-1.5)*1.36,((2-i//4)-1)*3.01,0)
    curve=bpy.data.curves.new(label,"FONT");curve.body=label;curve.size=.125;curve.align_x="CENTER";curve.materials.append(label_material)
    caption=bpy.data.objects.new(label+" caption",curve);c.objects.link(caption);caption.location=(rig.location.x,rig.location.y-1.33,.001)

bpy.ops.mesh.primitive_plane_add(size=18,location=(0,0,-.18));bpy.context.object.data.materials.append(floor)
world=bpy.data.worlds.new("Forge ambient");S.world=world;world.use_nodes=True;world.node_tree.nodes["Background"].inputs["Strength"].default_value=.35
for n,p,E,m,h in (("Cool",(-3,2,6),1600,(.64,.82,1),6),("Warm",(4,-3,4),1250,(1,.54,.29),4)):
    light=bpy.data.lights.new(n,"AREA");light.energy=E;light.size=h;light.color=m
    o=bpy.data.objects.new(n,light);S.collection.objects.link(o);o.location=p;aim(o,(0,0,0))
c=bpy.data.cameras.new("Kit board");o=bpy.data.objects.new("Kit board",c);S.collection.objects.link(o);S.camera=o
o.location=(0,.44,14);o.rotation_euler=(0,0,0);c.type="ORTHO";c.ortho_scale=10.45
S.render.engine="CYCLES";S.cycles.use_denoising=False;S.cycles.samples=36
S.render.resolution_x=1020;S.render.resolution_y=1320;S.render.resolution_percentage=100;S.render.image_settings.file_format="PNG"
S.render.filepath=str(SCRATCH/"forge-roster.png")
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"forge-roster.blend"),compress=True)
bpy.ops.render.render(write_still=True)

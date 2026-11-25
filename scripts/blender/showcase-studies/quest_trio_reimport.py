"""Two studio studies and one W01-inspired West plaza eye-level reimport."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory
out=output_directory()
repo=Path(__file__).resolve().parents[3]
root=repo/"public/assets/wildshard-art"
scene=bpy.context.scene
pins={
 "wsc-actor-017-surveyor.glb":"81c43903ce90891c98909e7763a2e6cfe7d71e8c8acd00e2076bcb097fc7bd3b",
 "quest-board.glb":"84b82ec701da4529f5d9403e137d10a28ea370b87ada4ba28f837dc0ba1472aa",
 "town-gate-merchant-house.glb":"266fc52858b80847add0627c536c1421d1305e3092c846625937d1d6d80017fe",
 "wsc-arch-005-plaza-paving-kit.glb":"85b9ddb3f5c13a5168325fd4b6c34ccf0fde319a5c3511d67232ce6d762f97ea",
 "market-awning-stall.glb":"b240fd8056db68d9b1caeaefc61459de4171f1345782726b0da40d0a1c614f04",
}
for name,sha in pins.items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==sha,name
roles={"yard-boss":"Yard Boss · L1–6","shift-boss":"Shift Boss · L13–20","surveyor":"Surveyor · L7–12"}

def loaded(p):
    known=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.view_layer.update()
    return sorted(set(scene.objects)-known,key=lambda o:o.name)
def set_mat(obs,t):
    for o in obs:
        if o.parent not in obs:o.matrix_world=t@o.matrix_world
def anchor(p,yaw=0,scale=1):
    return Matrix.Translation(p)@Matrix.Rotation(math.radians(yaw),4,"Z")@Matrix.Scale(scale,4)
def actor(role,p,yaw):
    obs=loaded(out/f"{role}-decoded-for-blender.glb")
    rig,=[o for o in obs if o.type=="ARMATURE"]
    body,=[o for o in obs if o.type=="MESH" and o.vertex_groups]
    assert len(rig.data.bones)==21 and rig.animation_data
    assert body.parent==rig and len(body.data.materials)==1
    set_mat(obs,anchor(p,yaw))
    return rig
def prop(name,p,yaw,scale=1,remember=None):
    obs=loaded(root/name)
    v=[o.matrix_world@x.co for o in obs if o.type=="MESH" for x in o.data.vertices]
    lo,hi=([f(p[k] for p in v) for k in range(3)] for f in (min,max))
    pivot=((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2])
    set_mat(obs,anchor(p,yaw,scale)@Matrix.Translation(-Vector(pivot)))
    if remember is not None: remember.extend(obs)
    return [z-x for x,z in zip(lo,hi)]
def mat(name,c,e=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value=(*c,1);n.inputs["Roughness"].default_value=.71
    n.inputs["Emission Color"].default_value=(*c,1);n.inputs["Emission Strength"].default_value=e
    return m
def box(name,p,dim,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
    mod=o.modifiers.new("Chamfer","BEVEL");mod.width=.018;mod.segments=2
    return o
def logo(body,p,size,m,tilt=90):
    d=bpy.data.curves.new(body,'FONT');d.body=body;d.align_x='CENTER';d.align_y='CENTER';d.size=size
    d.materials.append(m);o=bpy.data.objects.new(body,d);scene.collection.objects.link(o)
    o.location=p;o.rotation_euler.x=math.radians(tilt)
    return o
def aim(o,p):
    o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def area(p,d,target,power,shade):
    n=bpy.data.lights.new("Soft box","AREA");n.energy=power;n.size=d;n.color=shade
    o=bpy.data.objects.new("Soft box",n);scene.collection.objects.link(o);o.location=p;aim(o,target)
def cam(p,target,focal,ortho=None):
    d=bpy.data.cameras.new("Review camera");o=bpy.data.objects.new("Review camera",d);scene.collection.objects.link(o)
    o.location=p;aim(o,target);d.lens=focal
    if ortho:d.type="ORTHO";d.ortho_scale=ortho
    scene.camera=o
    return o
def render(name,w,h):
    scene.render.fps=24;scene.frame_set(19)
    scene.render.engine="CYCLES";scene.cycles.samples=34;scene.cycles.use_denoising=False
    scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
    scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=90
    scene.render.filepath=str(out/f"nov23-quest-trio-{name}.jpg")
    bpy.ops.render.render(write_still=True)

def build_fascia():
    """Thin overlay in the untouched donor's asset coordinates, negative Y forward."""
    patina=mat("Blackened hammered bronze",(.061,.090,.082))
    rim=mat("Worn brass edges",(.33,.184,.063))
    glyph=mat("Warm brass inset",(.92,.66,.25),.15)
    for m in (patina,rim,glyph):
        m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value=.47
    center_z=1.7065
    # Keep the rear outside the old lettering plane at y=-0.252.
    body=box("Quest Board | fascia",(.0014,-.264,center_z),(1.160,.018,.194),patina)
    body.modifiers[0].width=.006
    for z in (center_z-.084,center_z+.084):
        edge=box("Fine brass rule",(.0014,-.274,z),(1.121,.003,.004),rim)
        edge.modifiers[0].width=.001
    for x in (-.553,.556):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1,location=(x,-.275,center_z))
        rivet=bpy.context.object
        rivet.name="Peened mounting head"
        rivet.scale=(.008,.004,.008)
        rivet.data.materials.append(rim)
    title=logo("QUEST BOARD",(0,-.274,0),.17,glyph)
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    title.select_set(True);bpy.context.view_layer.objects.active=title
    bpy.ops.object.convert(target="MESH")
    verts=[title.matrix_world@v.co for v in title.data.vertices]
    xmin,xmax=min(v.x for v in verts),max(v.x for v in verts)
    zmin,zmax=min(v.z for v in verts),max(v.z for v in verts)
    factor=min(1.012/(xmax-xmin),.122/(zmax-zmin))
    title.scale=(factor,factor,factor)
    title.location.x=.0014-factor*(xmin+xmax)/2
    title.location.z=center_z-factor*(zmin+zmax)/2
    bpy.context.view_layer.update()
    path=out/"w1b-quest-board-fascia.glb"
    bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",export_apply=True)
    return path

fascia_only=os.environ.get("WSC_QUEST_FASCIA_ONLY")=="1"
clear_scene()
fascia_path=build_fascia()
clear_scene()
marker_only=os.environ.get("WSC_QUEST_MARKERS_ONLY")=="1"
if not fascia_only and not marker_only:
    slate=mat("Charcoal studio",(.044,.071,.083));wood=mat("Copper studio insert",(.340,.186,.086))
    words=mat("Names on proof",(.85,.82,.67),.35)
    for (x,role,yaw) in [(-1.05,"yard-boss",-13),(1.05,"shift-boss",12)]:
        actor(role,(x,0,0),yaw)
        box("Studio stand",(x,0,-.051),(1.55,1.27,.10),slate)
        box("Fine accent",(x,-.639,-.045),(1.44,.020,.012),wood)
        logo(roles[role],(x,-.628,.038),.111,words,62)
    box("Cyclorama",(0,0,-.159),(200,200,.115),slate)
    scene.world=bpy.data.worlds.new("Studio fill");scene.world.color=(.17,.18,.19)
    for p,d,power,c in [((-3,-3.9,4.4),3.5,730,(1,.84,.64)),((3,-2.5,3.3),4,485,(.66,.82,1)),((1,3,4),3,680,(.82,1,.88))]:
        area(p,d,(0,0,.92),power,c)
    cam((.03,-7.2,2.65),(0,0,.89),46,3.72)
    render("studio",1400,1050)
    for o in scene.objects:
        if o.type=="ARMATURE":
            o.matrix_world=o.matrix_world@Matrix.Rotation(math.pi,4,"Z")
    render("reverse",1400,1050)
clear_scene()
screen=[
 ("shift-boss",(-2.40,.15,0),-12),("surveyor",(-1.05,.02,0),4),
 ("yard-boss",(2.25,.15,0),-9)]
for role,p,yaw in screen:actor(role,p,yaw)
board_obs=[]
board_anchor=anchor((.54,.33,0),0,.81)
board=prop("quest-board.glb",(.54,.33,0),0,.81,board_obs)
house=prop("town-gate-merchant-house.glb",(.47,6.05,0),0,.86)
prop("market-awning-stall.glb",(-3.65,1.64,0),-11,.66)
for x in (-4.80,0,4.80):
    for y in (-3.56,1.24,6.04):
        paving=prop("wsc-arch-005-plaza-paving-kit.glb",(x,y,-.154),0)
warm=mat("Plaza ochre stone",(.41,.29,.15))
box("Apron",(0,3,-.056),(28,30,.10),warm)
gold=mat("Level one quest pip",(.97,.37,.025),.50)
shadow=mat("Marker border",(.054,.081,.080))
ink=mat("Marker glyph",(.09,.075,.035),.35)
# Marker isn't part of either actor bundle. It stages the original W01 L1 state.
if not marker_only:
    for i,(sz,m,y) in enumerate([(.262,shadow,-.041),(.218,gold,-.078)]):
        o=box("L1 marker | Yard Boss",(2.25,y,2.245),(sz,.045,sz),m)
        o.rotation_euler.y=math.radians(45)
    logo("!",(2.25,-.108,2.236),.194,ink)
world=bpy.data.worlds.new("West Town daylight");world.use_nodes=True;n=world.node_tree.nodes
sky=n.new("ShaderNodeTexSky");sky.sky_type='NISHITA';sky.sun_elevation=.56;sky.sun_rotation=2.04
sky.sun_size=.036;sky.sun_intensity=.65
world.node_tree.links.new(sky.outputs[0],n["Background"].inputs[0]);n["Background"].inputs[1].default_value=.19
scene.world=world
area((-3.8,-4,5.6),3.4,(0,0,1.2),420,(1,.83,.63))
eye=cam((-.32,-5.97,1.7),(-.046,.08,1.62),33.5)
bpy.context.view_layer.update()
xs=[world_to_camera_view(scene,eye,Vector(p)).x for p in [screen[0][1],screen[1][1],(.54,.33,0),screen[2][1]]]
assert xs==sorted(xs) and min(xs)>.04 and max(xs)<.96,xs
(out/"w1a-quest-trio-layout.json").write_text(json.dumps({
  "scope":"rigged noncombat studies, one 3 s studio idle each; no native actor or quest",
  "role_ids":{"yard-boss":"WSC-ACTOR-015","shift-boss":"WSC-ACTOR-016","surveyor":"WSC-ACTOR-017"},
  "screen_order":["shift-boss","surveyor","quest-board","yard-boss"],"screen_x":xs,
  "viewer_eye_height_m":1.7,"level_one_markers":["yard-boss"],"staged_actor_positions":screen,"quest_board_uniform_scale":.81,
  "donor_mesh_sizes_m":{"board":board,"house":house,"paving":paving},"unchanged_pinned_donors":pins
},indent=2)+"\n")
# Preserve the published camera, actors, marker and layout; replace only the title.
overlay=loaded(fascia_path)
set_mat(overlay,board_anchor)
bpy.context.view_layer.update()
board_mesh,=[o for o in board_obs if o.type=="MESH"]
legacy=[p for p in board_mesh.data.polygons
        if board_mesh.data.materials[p.material_index].name=="ink"
        and (board_anchor.inverted()@board_mesh.matrix_world@p.center).z>1.5]
points=[board_mesh.matrix_world@p.center for p in legacy]
assert len(points)==123,len(points)
trees=[]
for o in overlay:
    if o.type!="MESH" or not o.name.startswith("Quest Board | fascia"): continue
    verts=[o.matrix_world@v.co for v in o.data.vertices]
    trees.append(BVHTree.FromPolygons(verts,[tuple(p.vertices) for p in o.data.polygons]))
assert len(trees)==1
# Each legacy face centre must be occluded on a ray from both review cameras.
detail_pos=Vector((.18,-1.82,1.74))
for origin in (eye.location,detail_pos):
    for p in points:
        direction=p-origin
        assert trees[0].ray_cast(origin,direction.normalized(),direction.length)[0] is not None,p
triangles=0
for o in overlay:
    if o.type=="MESH":
        o.data.calc_loop_triangles()
        triangles+=len(o.data.loop_triangles)
assert triangles<1600 and fascia_path.stat().st_size<90000
(out/"w1b-quest-board-fascia-proof.json").write_text(json.dumps({
  "title":"QUEST BOARD","unchanged_quest_board_donor_sha256":pins["quest-board.glb"],
  "masked_legacy_ink_triangle_centres_per_camera":len(points),
  "output_bytes":fascia_path.stat().st_size,"triangles":triangles,
  "round5_anchors_three_x_z":{"quest":[-36,-17],"contracts":[-26,17]},
  "native_game_modified":False,
},indent=2)+"\n")
if marker_only:
    from quest_marker_plate import capture
    capture(scene,out,root,eye,screen,cam)
    sys.exit(0)
render("plaza-quest-board",1500,1120)
cam(detail_pos,(.54,.13,1.40),39)
render("quest-board-detail",1360,1010)

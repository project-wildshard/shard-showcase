"""Build W4b release/score dress art and photograph exact pinned bench poses."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

root = Path(__file__).resolve().parents[2]
trace, out = map(Path, sys.argv[sys.argv.index('--') + 1:])
out.mkdir(parents=True, exist_ok=True)
data = json.loads(trace.read_text())
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
s = bpy.context.scene
a = Path(root, 'public/assets/wildshard-art')
basis = Matrix.Rotation(math.pi/2, 4, 'X')

def mat(name, rgb, metal=0, rough=.58, glow=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    for k, v in {'Base Color':(*rgb,1),'Metallic':metal,'Roughness':rough,
                 'Emission Color':(*rgb,1),'Emission Strength':glow}.items():
        bs.inputs[k].default_value = v
    return m

iron=mat('Yard blued iron',(.041,.064,.071),.55)
steel=mat('Struck satin steel',(.21,.27,.27),.65,.37)
gold=mat('Deep amber baked enamel',(.84,.26,.032),.32)
rubber=mat('Grip rubber',(.023,.027,.028))
teal=mat('Oxidized blue lane',(.078,.245,.235),.18,.77)
concrete=mat('Dark poured concrete',(.115,.153,.150),.09,.86)
warm=mat('Stencil warm bone',(.64,.59,.42),.06)
glass=mat('Timer sunk blue glass',(.011,.035,.050),.26,.32)
lamp=mat('Cyan status light',(.019,.54,.73),.25,.24,1.45)
signal=mat('Amber active light',(.91,.24,.021),.27,.31,1.2)

def objmat(o,n,m):
    o.name=n
    o.data.materials.append(m)
    return o

def box(n,p,d,m,r=.035):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p)
    o=bpy.context.object
    o.dimensions=d
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if r:
        v=o.modifiers.new('Machined chamfer','BEVEL')
        v.width=min(r,min(d)*.35)
        v.segments=1
        w=o.modifiers.new('Hard panels','WEIGHTED_NORMAL')
        w.keep_sharp=True
    return objmat(o,n,m)

def rod(n,p,q,r,m,segments=12):
    v=Vector(q)-Vector(p)
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=r,depth=v.length,location=Vector(p)+v/2)
    o=bpy.context.object
    o.rotation_euler=v.to_track_quat('Z','Y').to_euler()
    return objmat(o,n,m)

def text(n,p,size,m,flat=False):
    f=bpy.data.curves.new(n,'FONT')
    f.body=n
    f.align_x=f.align_y='CENTER'  # CENTER is the caption baseline in both axes.
    f.size=size
    f.materials.append(m)
    o=bpy.data.objects.new(n,f)
    s.collection.objects.link(o)
    o.location=p
    if not flat: o.rotation_euler.x=math.pi/2
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    # BFont tiny loops can produce degenerate triangles; the exported text
    # remains geometry, so no fonts or texture files are needed downstream.
    import bmesh
    bm=bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.delete(bm, geom=[x for x in bm.faces if x.calc_area()<1e-9], context='FACES_ONLY')
    bm.to_mesh(o.data); bm.free(); o.data.update()
    return o

def group(n, parts, origin=(0,0,0)):
    g=bpy.data.objects.new(n,None)
    s.collection.objects.link(g)
    g.location=origin
    bpy.context.view_layer.update()
    for o in parts:
        world=o.matrix_world.copy()
        o.parent=g
        o.matrix_world=world
    return g

def publish(n,groups):
    bpy.ops.object.select_all(action='DESELECT')
    for g in groups:
        g.select_set(True)
        for o in g.children_recursive: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/(n+'.glb')),export_format='GLB',
                              use_selection=True,export_animations=False)

fixed=[box('Concrete seat',(0,0,.10),(1.34,1.00,.20),concrete),
       box('Splined base',(0,0,.23),(1.05,.79,.13),iron),
       box('Lever column',(0,0,.67),(.39,.36,.89),gold),
       box('Upper machine housing',(0,0,1.04),(.61,.55,.34),iron),
       box('Angled instruction face',(0,-.254,.81),(.50,.026,.27),steel),
       box('Lamp inlay',(.169,-.283,1.085),(.085,.031,.044),signal),
       text('RELEASE',(0,-.27,.825),.104,rubber)]
for x in [-.40,.40]:
    for y in [-.273,.273]:
        fixed.append(rod('Recess hex bolt',(x,y,.276),(x,y,.321),.057,steel,6))
fixed += [rod('Transverse pivot',(-.354,0,1.103),(.354,0,1.103),.104,steel)]
pivot=(0,0,1.103)
moving=[rod('Pull arm',pivot,(0,-.15,1.70),.047,steel),
        rod('Knurled grip',(-.16,-.15,1.70),(.16,-.15,1.70),.067,rubber)]
for x in [-.186,.186]:
    moving.append(rod('Grip collar',(x-.026,-.15,1.70),(x+.026,-.15,1.70),.066,gold))
lever_base=group('Release_stand_floor',fixed)
lever_arm=group('Release_arm_localX_pivot',moving,pivot)
publish('w4b-release-stand',(lever_base,lever_arm))

panel=[]
for x in [-1.61,1.61]:
    panel += [box('Set-down foot',(x,0,.065),(.51,.54,.13),iron),
              box('Mounting post',(x,0,1.18),(.20,.20,2.36),steel),
              box('Enamel pole ID stripe',(x,-.111,.50),(.182,.022,.26),gold)]
panel += [box('Folded backplate',(0,0,2.21),(4.18,.28,1.31),iron),
          box('Angled cap flash',(0,0,2.891),(4.31,.34,.071),gold),
          box('Recessed readout',(0,-.145,2.179),(3.48,.095,.61),glass),
          box('Cyan left status bar',(-1.88,-.162,2.186),(.084,.055,.59),lamp),
          box('Amber right status bar',(1.88,-.162,2.186),(.084,.055,.59),signal),
          text('S K I T T L E S',(0,-.147,2.647),.216,warm),
          text('P H Y S I C S   Y A R D',(0,-.156,1.729),.125,warm)]
for x in [-1.93,1.93]:
    for z in [1.68,2.75]:
        panel.append(rod('Face screw',(x,-.13,z),(x,-.18,z),.036,steel,6))
board=group('Skittle_scoreboard_floor',panel)
publish('w4b-skittle-scoreboard',(board,))

def stage(parent,p):
    for g in parent: g.location += Vector(p)

# Preserve the wall-to-bay design; put the existing scoreboard facing the
# diagonal spectator camera for this labelled calibration render only.
stage([lever_base,lever_arm], (24.76,-2.75,6.00))
stage([board], (-17.0,2.40,.04))
score=text(f"{data['score']}  /  10",(-17,-.201+2.40,2.179+.04),.416,lamp)

def donor(name):
    path = a/name
    before = set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    new=set(s.objects)-before
    o,=[q for q in new if q.type=='MESH']
    mesh,m=o.data,o.matrix_world.copy()
    for q in new: bpy.data.objects.remove(q,do_unlink=True)
    return mesh,m,hashlib.sha256(path.read_bytes()).hexdigest()

ballmesh,ballpose,ballsha=donor('wsc-plan-004-rolling-ball.glb')
pinmesh,pinpose,pinsha=donor('wsc-plan-005-skittle-pin.glb')
bodies={}
for k in data['data']['bodies']:
    id=k['id']; isball=id.startswith('ball-')
    o=bpy.data.objects.new(id,ballmesh if isball else pinmesh)
    s.collection.objects.link(o)
    bodies[id]=o

def frame(f):
    for row in f['bodies']:
        x,y,z=(row['p'][k] for k in ('x','y','z'))
        r=row['q']
        rot=basis@Quaternion((r['w'],r['x'],r['y'],r['z'])).to_matrix().to_4x4()@basis.inverted()
        center=Matrix.Translation((x+42,196-z,y))
        isball=row['id'].startswith('ball-')
        bodies[row['id']].matrix_world=center@rot@Matrix.Translation((0,0,0 if isball else -.645))@(ballpose if isball else pinpose)

box('Broad yard slab',(0,0,-.21),(98,51,.50),concrete,.06)
for j in range(12):
    lo=j*2; hi=lo+2
    mesh=bpy.data.meshes.new('Continuous ribbon')
    mesh.from_pydata([(lo,-2,lo*.25),(hi,-2,hi*.25),(hi,2,hi*.25),(lo,2,lo*.25),
                       (lo,-2,.04),(hi,-2,.04),(hi,2,.04),(lo,2,.04)],
                      [],[(0,1,2,3),(0,4,5,1),(2,6,7,3)])
    for m in [teal,iron if j%2 else gold]: mesh.materials.append(m)
    mesh.polygons[1].material_index=mesh.polygons[2].material_index=1
    o=bpy.data.objects.new('Original 24 m ramp panel',mesh)
    s.collection.objects.link(o)
# Crest operator perch is a presentation-only structural context. It
# stays outside the disjoint bowling contact envelope |y| <= 2.
box('Operator perch shell',(24.84,-3.32,5.82),(3.45,2.58,.36),iron,.08)
for i in range(13):
    box('Perch anti-slip deck',(23.28+i*.26,-3.32,5.987),(.236,2.48,.026),steel,.008)
for x in [23.40,26.22]:
    box('Operator pier',(x,-3.84,2.82),(.26,.29,5.58),iron,.024)
    box('Pier shoe',(x,-3.84,.15),(.59,.57,.22),concrete)
    box('Rail post',(x,-4.52,6.54),(.073,.073,1.08),steel,.008)
rod('Amber top rail',(23.20,-4.52,7.05),(26.40,-4.52,7.05),.049,gold)
rod('Lower guard rail',(23.20,-4.52,6.54),(26.40,-4.52,6.54),.036,steel)
for y in [-1.92,1.92]:
    rod('Original visual toe rails',(0,y,.045),(24,y,6.045),.045,steel)
    box('Lane apron side line',(-7.98,y,.046),(15.95,.058,.012),warm,.002)
    for x in range(-15,0):
        box('Inset balance stripe',(x,y*.89,.047),(.45,.052,.009),teal,.002)
for x in [-1.4,-4.9,-8.4,-11.9]:
    box('Crosswise apron gauge',(x,0,.045),(.070,3.61,.008),warm,.002)
for row in data['data']['bodies'][4:]:
    p=row['at']
    bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=6,major_radius=.34,minor_radius=.012,
                                    location=(p['x']+42,196-p['z'],.044))
    objmat(bpy.context.object,'Painted pin seat outline',warm)

def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def light(n,p,t,e,c,w):
    l=bpy.data.lights.new(n,'AREA'); l.energy=e; l.color=c; l.shape='DISK'; l.size=w
    o=bpy.data.objects.new(n,l); s.collection.objects.link(o); o.location=p; aim(o,t)

s.world=bpy.data.worlds.new('Bright open slate sky')
s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.30,.40,.50,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.37
sun=bpy.data.lights.new('Low West sun','SUN'); sun.energy=3; sun.angle=.19; sun.color=(1,.83,.64)
u=bpy.data.objects.new(sun.name,sun); s.collection.objects.link(u); u.location=(16,-18,18); aim(u,(0,0,0))
light('Green-blue yard bounce',(-10,-8,8),(-10,0,0),2000,(.58,.81,1),7)
cam=bpy.data.cameras.new('Bench photographs')
s.camera=bpy.data.objects.new(cam.name,cam)
s.collection.objects.link(s.camera)
cam.type='ORTHO'
s.render.engine='CYCLES'; s.cycles.samples=44; s.cycles.adaptive_threshold=.075
s.cycles.use_denoising=False
s.view_settings.view_transform='AgX'; s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_x=1400; s.render.resolution_y=920; s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG'; s.render.image_settings.quality=94

def render(n,p,t,w):
    s.camera.location=p; aim(s.camera,t); cam.ortho_scale=w
    s.render.filepath=str(out/(n+'.jpg'))
    bpy.ops.render.render(write_still=True)

frame(data['frames'][0]); score.hide_render=True
render('skittles-release-ready',(31,-15,15),(21,-1.3,5.55),13.7)
frame(data['frames'][-1]); score.hide_render=False; lever_arm.rotation_euler.x=math.radians(42)
render('skittles-pins-after',(-9,-14,10),(-11.25,.58,1.0),16.1)
(out/'donors.json').write_text(json.dumps({'ball':ballsha,'pin':pinsha},indent=2)+'\n')

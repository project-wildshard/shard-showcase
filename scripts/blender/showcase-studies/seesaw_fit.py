"""Reimport the shipped West Yard see-saw and inspect its static pose envelope."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
DONOR = ROOT / 'public/assets/wildshard-art/wsc-plan-003-hinged-seesaw.glb'
SHA = '4810b216338fb4da46115884945a2a52c89776ce9d87c585508d6b95bd27df07'
assert hashlib.sha256(DONOR.read_bytes()).hexdigest() == SHA
assert len(sys.argv[sys.argv.index('--') + 1:]) == 1
out = Path(sys.argv[-1]).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=str(DONOR))
s = bpy.context.scene
stand, deck = (s.objects[k] for k in ('Fixed_Base', 'Hinged_Deck'))
bpy.context.view_layer.update()
assert abs(deck.location.z - 1.47) < 1e-6
zero = deck.matrix_world.copy()

def faces(o):
    o.data.calc_loop_triangles()
    return [tuple(t.vertices) for t in o.data.loop_triangles]

def points(o, matrix):
    return [matrix @ v.co for v in o.data.vertices]

sv, sf, df = points(stand, stand.matrix_world), faces(stand), faces(deck)
stand_bvh = BVHTree.FromPolygons(sv, sf, all_triangles=True)
angle_matrix = lambda angle: zero @ Matrix.Rotation(math.radians(angle), 4, 'Y')

# BVH overlap gives candidate pairs conservatively. Clipping each line segment to
# the opposite triangle plane gives the actual intersection points for nonparallel
# faces. Any coplanar BVH candidate counts as unclassified, not as clear.
def crossings(a, b):
    n = (b[1] - b[0]).cross(b[2] - b[0])
    n.normalize()
    result = []
    for u, v in zip(a, a[1:] + a[:1]):
        du, dv = n.dot(u - b[0]), n.dot(v - b[0])
        if du * dv > 0 or abs(du - dv) < 1e-8:
            continue
        p = u.lerp(v, du / (du - dv))
        if all(n.dot((r - q).cross(p - q)) >= -1e-7
               for q, r in zip(b, b[1:] + b[:1])):
            result.append(p)
    return result

def inspect(angle):
    dv = points(deck, angle_matrix(angle))
    pairs = BVHTree.FromPolygons(dv, df, all_triangles=True).overlap(stand_bvh)
    outside, materials, inside, unclassified = [], set(), 0, 0
    for di, si in pairs:
        a, b = tuple(dv[i] for i in df[di]), tuple(sv[i] for i in sf[si])
        na = (a[1] - a[0]).cross(a[2] - a[0]).normalized()
        nb = (b[1] - b[0]).cross(b[2] - b[0]).normalized()
        if abs(na.dot(nb)) > 0.999999 and max(abs(nb.dot(p - b[0])) for p in a) < 1e-6:
            unclassified += 1
            continue
        hits = crossings(a,b) + crossings(b,a)
        if not hits:
            continue
        # The fixed axle radius is 0.17 m, the outer side bosses 0.29 m.
        # Bound both by a cylinder along the axle with a small measurement margin.
        beyond = [p for p in hits if math.hypot(p.x, p.z - 1.47) > .300 or abs(p.y) > 1.49]
        if beyond:
            outside.extend(beyond)
            face = stand.data.polygons[stand.data.loop_triangles[si].polygon_index]
            materials.add(stand.data.materials[face.material_index].name)
        else:
            inside += 1
    return {'angle_deg': angle, 'ground_clearance_m': round(min(p.z for p in dv), 6),
            'joint_triangle_pairs': inside, 'coplanar_candidates': unclassified,
            'outside_joint_intersection_points': len(outside),
            'outside_stand_materials': sorted(materials),
            'outside_example_xyz_m': [round(x, 4) for x in outside[0]] if outside else None}

sweep = [inspect(q / 4) for q in range(-48, 49)]
samples = [inspect(q) for q in (-12, -10, 0, 10, math.degrees(.2), 12)]
for row in samples:
    print(row)
(start, finish) = (10, 12)
for _ in range(24):
    mid = (start + finish) / 2
    if inspect(mid)['ground_clearance_m'] > 0:
        start = mid
    else:
        finish = mid
report = {'id':'WSC-PLAN-003','donor_sha256':SHA,'joint_cylinder_radius_m':.30,
          'joint_cylinder_half_length_m':1.49,'ground_crossing_deg_approx':round((start+finish)/2,4),
          'samples':samples, 'sweep':sweep, 'native_physics':False}
assert all(r['outside_joint_intersection_points'] == r['coplanar_candidates'] == 0
           for r in sweep if abs(r['angle_deg']) <= 10)
assert abs(samples[1]['ground_clearance_m'] - .211) < .0001
assert all(r['outside_joint_intersection_points'] > 0 and
           set(r['outside_stand_materials']) == {'Safety orange enamel'}
           for r in sweep if abs(r['angle_deg']) in (11.75, 12))
(out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')

def finish(name, c, metal=0, rough=.72):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*c,1)
    m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value=(*c,1)
    n.inputs['Metallic'].default_value=metal
    n.inputs['Roughness'].default_value=rough
    return m

slate=finish('Blued concrete',(.042,.064,.075),.07)
strip=finish('Cold blue shop marking',(.067,.268,.287),.2)
hazard=finish('Amber clearance gauge',(.73,.29,.04),.2)
ink=finish('Plate lettering',(.59,.73,.71))

def box(n, p, d, m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object
    o.name=n
    o.dimensions=d
    o.data.materials.append(m)

def label(body, x, y, size=.3):
    cu=bpy.data.curves.new(body,'FONT')
    cu.body=body
    cu.size=size
    cu.materials.append(ink)
    o=bpy.data.objects.new(body,cu)
    s.collection.objects.link(o)
    o.location=(x,y,.018)

def pose(y, angle):
    move=Matrix.Translation((0,y,0))
    for src,world in ((stand,stand.matrix_world),(deck,angle_matrix(angle))):
        o=bpy.data.objects.new(f'{src.name} {angle:+g} degrees',src.data)
        s.collection.objects.link(o)
        o.matrix_world=move @ world

def aim(o, target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def area(n,p,q,e,col,sz):
    d=bpy.data.lights.new(n,'AREA')
    d.energy=e
    d.color=col
    d.shape='DISK'
    d.size=sz
    o=bpy.data.objects.new(n,d)
    s.collection.objects.link(o)
    o.location=p
    aim(o,q)

s.world=bpy.data.worlds.new('Blue shop bounce')
s.world.color=(.24,.27,.31)
area('Wide amber key',(-5,-8,11),(0,0,0),4300,(1,.76,.55),9)
area('Blue skylight',(6,6,8),(0,0,0),3400,(.53,.77,1),8)
area('Neutral rim',(-6,8,5),(0,0,0),2200,(.77,.90,1),7)
box('Continuous level ground',(0,0,-.27),(200,200,.54),slate)
for i in range(-26,27):
    box('Shop grid X',(i*.5,0,.001),(.012,24,.002),strip)
for j in range(-17,18):
    box('Shop grid Y',(0,j*.5,.001),(26,.012,.002),strip)
for y,angle in ((2.7,-10),(-2.7,10)):
    pose(y,angle)
    label(f'{angle:+d} DEG  /  211 MM FLOOR CLEARANCE',-6.8,y-1.7,.27)
    for x in (-7.18,7.18):
        box('Clearance lane end',(x,y,.006),(.08,2.8,.010),hazard)
stand.hide_render=deck.hide_render=True
cam=bpy.data.cameras.new('Art fit proof')
s.camera=bpy.data.objects.new(cam.name,cam)
s.collection.objects.link(s.camera)
cam.type='ORTHO'
s.render.engine='CYCLES'
s.cycles.samples=56
s.cycles.use_denoising=False
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG'
s.render.image_settings.quality=92

def render(name,p,q,scale,res):
    s.camera.location=p
    aim(s.camera,q)
    cam.ortho_scale=scale
    s.render.resolution_x,s.render.resolution_y=res
    s.render.filepath=str(out/(name+'.jpg'))
    bpy.ops.render.render(write_still=True)

render('nov23-seesaw-fit',(9,-18,17),(0,0,.45),19.0,(1600,1050))
render('nov23-seesaw-joint',(2.1,-9,3.7),(0,-2.7,1.03),5.0,(1150,820))

"""W6c rope terminal art: two fitted reusable overlays, original spans unchanged."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[3]
spec = json.loads((root/'scripts/blender/west-climb-rock/expected.json').read_text())
yard, out = map(Path, sys.argv[sys.argv.index('--')+1:][:2])
out.mkdir(parents=True, exist_ok=True)
assert bpy.data.filepath and Path(bpy.data.filepath).resolve() == (yard/'climb-rock-editable.blend').resolve()
parity = json.loads((yard/'parity.json').read_text())
assert parity['matched_signature'] in (spec['semantic_signature'], spec['normalized_semantic_signature'])
assert json.loads((yard/'integration.json').read_text())['bridges'] == spec['bridges']
scene = bpy.context.scene

def finish(n, c, metal, rough):
    m = bpy.data.materials.new(n)
    m.diffuse_color = (*c, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*c, 1)
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Roughness'].default_value = rough
    return m

iron = finish('Oil-blued forged iron', (.057,.093,.101), .64, .37)
bronze = finish('Warm bronze hardware', (.45,.25,.10), .57, .31)
zinc = finish('Weathered fastener caps', (.20,.30,.30), .64, .32)

class Mesh:
    def __init__(self):
        self.v, self.f, self.m = [], [], []

    def poly(self, verts, faces, material):
        i = len(self.v)
        self.v.extend(verts)
        self.f.extend(tuple(i+x for x in f) for f in faces)
        self.m.extend([material]*len(faces))

    def tube(self, axis, outer, inner, lo, hi, material, sides=12, center=(0,0,0), phase=0):
        """True open bore, not a cap; radial dimensions are to vertices."""
        k = Vector(axis).normalized()
        u = k.cross(Vector((1,0,0) if abs(k.x)<.9 else (0,0,1))).normalized()
        v = k.cross(u).normalized()
        c = Vector(center)
        dirs = [u*math.cos(phase+i*math.tau/sides)+v*math.sin(phase+i*math.tau/sides) for i in range(sides)]
        vertices = [c+k*t+d*r for r in (outer,inner) for t in (lo,hi) for d in dirs]
        faces = []
        for i in range(sides):
            j=(i+1)%sides; n=sides
            faces.extend(((i,j,j+n,i+n),(i+2*n,i+3*n,j+3*n,j+2*n),
                          (i,i+2*n,j+2*n,j),(i+n,j+n,j+3*n,i+3*n)))
        self.poly(vertices, faces, material)

    def box(self, p, d, material):
        self.poly([tuple(p[k]+q[k]*d[k]/2 for k in range(3))
                   for q in [(i,j,z) for z in (-1,1) for j in (-1,1) for i in (-1,1)]],
                  [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],material)

    def make(self,n):
        data=bpy.data.meshes.new(n)
        data.from_pydata(self.v,[],self.f)
        data.update()
        mats=list(dict.fromkeys(self.m))
        for m in mats:data.materials.append(m)
        for p,m in zip(data.polygons,self.m):p.material_index=mats.index(m)
        o=bpy.data.objects.new(n,data)
        scene.collection.objects.link(o)
        return o

post = Mesh()
# Two rims with an open bore. A central stop sleeve bridges them.
for lo, hi in ((-.116,-.076),(.076,.116)):
    post.tube((0,0,1),.109,.079,lo,hi,bronze)
post.tube((0,0,1),.101,.079,-.076,.076,iron)
for s in (-1,1):
    post.box((s*.114,0,0),(.075,.113,.164),iron)
    for z in (-.044,.044):
        post.tube((1,0,0),.022,.010,min(s*.147,s*.161),max(s*.147,s*.161),zinc,6,center=(0,0,z))
ferrule = Mesh()
ferrule.tube((1,0,0),.047,.033,-.081,.081,iron)
for lo, hi in ((-.084,-.056),(.056,.084)):
    ferrule.tube((1,0,0),.057,.033,lo,hi,bronze)
post_obj = post.make('Post sleeve')
ferrule_obj = ferrule.make('Rope ferrule')
names = ['w6c-bridge-post-sleeve','w6c-bridge-rope-ferrule']

def export_and_import(o,n):
    f=out/(n+'.glb')
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',use_selection=True,
                             export_yup=True,export_apply=True,export_lights=False,export_cameras=False)
    bpy.data.objects.remove(o,do_unlink=True)
    b=f.read_bytes()
    j=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
    assert len(j['nodes'])==1 and not any(k in j['nodes'][0] for k in ('rotation','translation','scale','matrix'))
    assert 'images' not in j and len(j['meshes'])==1
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(f))
    imported,=set(scene.objects)-before
    imported.data.calc_loop_triangles()
    return imported,{'bytes':len(b),'triangles':len(imported.data.loop_triangles),
                     'primitives':len(j['meshes'][0]['primitives']),'sha256':hashlib.sha256(b).hexdigest()}

originals, meta = zip(*(export_and_import(o,n) for o,n in zip((post_obj,ferrule_obj),names)))
finished = bpy.data.collections.new('W6c | optional terminal hardware')
scene.collection.children.link(finished)
placements=[]

def instance(base,name,matrix):
    o=bpy.data.objects.new(name,base.data)
    finished.objects.link(o)
    o.matrix_world=matrix
    return o

def reach(o,axis,anchor):
    return max(axis.dot(o.matrix_world@v.co-anchor) for v in o.data.vertices)

def numbers(v):
    return [round(float(x),6) for x in v]

for b in spec['bridges']:
    A,B=map(Vector,b['anchors_blender'])
    D=B-A
    L=math.hypot(D.x,D.y)
    U=Vector((D.x/L,D.y/L,0))
    V=Vector((-U.y,U.x,0))
    W=b['width_m']
    N=round(L/.43)
    Z=Vector((0,0,1))
    donor=scene.objects['CLIMB | bridge '+b['name']]
    verts=[donor.matrix_world@v.co for v in donor.data.vertices]
    target=BVHTree.FromPolygons(verts,[tuple(p.vertices) for p in donor.data.polygons])

    def point(t):
        p=A+D*t-Z*(4*b['illustrative_sag_m']*t*(1-t))
        if b['name']=='C Rock' and t>.67:
            if t<=.82:
                q=(t-.67)/.15
                f=q*q*(3-2*q)
                p.z=p.z*(1-f)+16.065*f
            else:p.z=16+.065*(1-t)/.18
        return p

    for e,E,t,ti in [(0,A,0,1/N),(1,B,1,1-1/N)]:
        anchor=point(t)
        assert (E-anchor).length < 1e-4
        chord=(point(ti)-anchor).normalized()
        for s in (-1,1):
            side=V*s
            a=anchor+side*(W*.58)+Z*1.05
            rope=anchor+side*(W*.55)+Z*1.05
            fp=rope+chord*.101
            # Vertical timber and rope radius rechecked against actual modeled triangles.
            post_hit=target.ray_cast(a+side*.22,-side,.26)
            rope_hit=target.ray_cast(fp-chord.cross(Z).normalized()*.16,chord.cross(Z).normalized(),.19)
            assert post_hit[0] is not None and .124<post_hit[3]<.155, (b['name'],post_hit)
            assert rope_hit[0] is not None and .118<rope_hit[3]<.149, (b['name'],rope_hit)
            pm=Matrix.Translation(a)@Matrix.Rotation(math.atan2(U.y,U.x),4,'Z')
            fm=Matrix.Translation(fp)@chord.to_track_quat('X','Z').to_matrix().to_4x4()
            sleeve=instance(originals[0],f'{b["name"]} {e} {s:+d} sleeve',pm)
            ferr=instance(originals[1],f'{b["name"]} {e} {s:+d} ferrule',fm)
            bpy.context.view_layer.update()
            # Vertical plane of the original tread envelope; no projection over that lane.
            reach_inside=max(reach(o,-side,anchor) for o in (sleeve,ferr))
            side_margin=-W/2-reach_inside
            assert side_margin>.002, (b['name'],e,s,side_margin)
            placements.append({'bridge':b['name'],'endpoint':e,'side':s,
                'sleeve_xyz_blender':numbers(a),'sleeve_yaw_rad':round(math.atan2(U.y,U.x),6),
                'ferrule_xyz_blender':numbers(fp),'ferrule_axis_blender':numbers(chord),
                'tread_envelope_margin_m':round(side_margin,5),
                'post_sample_radius_m':round(.22-post_hit[3],5),'rope_sample_radius_m':round(.16-rope_hit[3],5)})

for o in originals:
    bpy.data.objects.remove(o,do_unlink=True)
assert len(placements)==12
report={'status':'static_visual_overlay','donor_matched_signature':parity['matched_signature'],
        'models':dict(zip(names,meta)), 'terminal_count':len(placements),'placements':placements}
(out/'fit.json').write_text(json.dumps(report,indent=2)+'\n')
print('TERMINAL FIT PASS:', min(p['tread_envelope_margin_m'] for p in placements),meta)

if '--models-only' in sys.argv:
    raise SystemExit(0)
scene.render.engine='CYCLES'
scene.cycles.samples=38
scene.cycles.adaptive_threshold=.045
scene.cycles.use_denoising=False
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='WEBP'
scene.render.image_settings.quality=90
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
world=bpy.data.worlds.new('Late afternoon blue fill')
scene.world=world
world.use_nodes=True
bg=world.node_tree.nodes['Background']
bg.inputs[0].default_value=(.45,.63,.78,1)
bg.inputs[1].default_value=.62
for o in scene.objects:
    if o.type=='LIGHT':o.hide_render=True
bpy.ops.object.light_add(type='SUN')
sun=bpy.context.object
sun.rotation_euler=Vector((-.59,.35,-.65)).to_track_quat('-Z','Y').to_euler()
sun.data.color=(1,.83,.60)
sun.data.energy=3.3
sun.data.angle=.095
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam

def shot(name,eye,look,lens,res):
    cam.location=eye
    cam.rotation_euler=(Vector(look)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=res
    scene.render.filepath=str(out/(name+'.webp'))
    bpy.ops.render.render(write_still=True)

if '--detail-only' not in sys.argv:
    shot('nov26-w6c-bridge-terminal-wide',(-156,-35.2,12.9),(-153.4,-43.9,10.5),28,(1440,900))
shot('nov26-w6c-bridge-terminal-detail',(-149.95,-41.52,11.46),(-149.57,-42.57,11.02),43,(1160,920))

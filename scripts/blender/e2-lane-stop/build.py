"""Optional game-art end stop for the existing E2 lane, not a placed level."""
from pathlib import Path
import hashlib,json,math,struct,sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
assets=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art'
pins={
 'e2-charge-lane-warning.glb':'a66841c0328e58988dec7574f4a69adebb091955490cb1f1f55503f82fe43351',
 'haul-crate.glb':'d7a5f8fcb2b835d0c0c77c3051ebd950ed449dc2c563e10779fdc5f01cc6bb44',
}
for p,h in pins.items():assert hashlib.sha256((assets/p).read_bytes()).hexdigest()==h
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
def mat(name,c,metal=.2,rough=.5):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value=(*c,1)
    n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough
    return m
def select(obs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs:o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
def box(name,p,d,m,b=.012):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=name;o.dimensions=d;o.data.materials.append(m)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if b:
        z=o.modifiers.new('Edge bevel','BEVEL');z.width=b;z.segments=1
        bpy.ops.object.modifier_apply(modifier=z.name)
    return o
def join(label,obs):
    select(obs);bpy.ops.object.join();o=bpy.context.object;o.name=label
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    return o
def bolt(x,y,z,rad,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=rad,depth=.022,location=(x,y,z),rotation=(math.pi/2,0,0))
    o=bpy.context.object;o.name='Service fastener';o.data.materials.append(m);return o
def plate(name,verts,m):
    d=bpy.data.meshes.new(name);d.from_pydata(verts,[],[tuple(range(len(verts)))]);d.materials.append(m)
    o=bpy.data.objects.new(name,d);s.collection.objects.link(o);return o
steel=mat('Blued zinc plating',(.096,.159,.17),.53)
edge=mat('Burnished cast edge',(.33,.39,.39),.66)
dark=mat('Deep petrol frame',(.045,.07,.073),.47)
amber=mat('Scuffed industrial amber',(.69,.26,.044),.34)
pale=mat('Bone enamel',(.82,.74,.48),.13)
rubber=mat('Reinforced black impact rubber',(.031,.038,.035),.04,.76)
frame=[box('Ground crossmember',(0,.475,.148),(2.43,.91,.296),dark,.041),
       box('Back plate',(0,.54,.714),(2.38,.22,1.16),steel,.057),
       box('Upper cap',(0,.45,1.32),(2.46,.61,.132),edge,.031)]
head=[box('Damped strike face',(0,.154,.725),(2.17,.278,1.025),rubber,.053)]
for x in [-.84,-.60,-.36,-.12,.12,.36,.60,.84]:
    head.append(box('Moulded damper rib',(x,.031,.719),(.14,.062,.856),rubber,.016))
for i in [-1,1]:
    frame.append(box('End return',(i*1.125,.408,.684),(.225,.675,1.21),amber,.031))
    boot=box('Low tripod brace',(i*1.07,.687,.433),(.19,.523,.73),steel,.035)
    boot.rotation_euler.x=-.21;frame.append(boot)
    frame.append(box('Side foot',(i*1.02,.49,.055),(.41,.95,.11),steel,.023))
    for y in (.24,.79):
        frame.append(box('Anchor washer',(i*1.02,y,.122),(.115,.101,.043),edge,.015))
    for z in (.414,.634,.854,1.076):
        frame.append(bolt(i*1.121,.071,z,.036,edge))
for i in range(5):
    x=(i-2)*.17
    z=1.323; y=.143
    frame.append(plate('Diagonal caution slat',[(x-.046,y,z-.035),(x+.026,y,z-.035),(x+.087,y,z+.039),(x+.015,y,z+.039)],pale))
frame=join('ChargeStopFrame',frame)
head=join('ChargeStopReplaceableFace',head)
f=out/'e2-charge-stop.glb'
select([frame,head])
bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',use_selection=True,export_animations=False)
b=f.read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n])
tri=sum(g['accessors'][q['indices']]['count']//3 for m in g['meshes'] for q in m['primitives'])
assert not g.get('textures') and tri<2200 and len(b)<165000
for o in tuple(s.objects):bpy.data.objects.remove(o,do_unlink=True)
def load(path,offset):
    old=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    obs=sorted(set(s.objects)-old,key=lambda o:o.name)
    for o in obs:
        if o.parent is None:o.location+=Vector(offset)
    bpy.context.view_layer.update()
    return [o for o in obs if o.type=='MESH']
stop=load(f,(0,8.4,0))
lane=load(assets/'e2-charge-lane-warning.glb',(0,0,0))
crates=[]
for side in (-1,1):
    for d in (3.85,6.25):
        crates+=load(assets/'haul-crate.glb',(side*3.2,d,0))

def pts(o):
    return [o.matrix_world@v.co for v in o.data.vertices]
def dump(o):
    v=pts(o);o.data.calc_loop_triangles()
    return dict(name=o.name,vertices=[round(a,7) for x,y,z in v for a in (x,z,-y)],
                indices=[i for t in o.data.loop_triangles for i in t.vertices])
def bounds(obs):
    p=[v for o in obs for v in pts(o)]
    return [[round(fun(v[i] for v in p),6) for i in range(3)] for fun in (min,max)]
assert len(stop)>=2 and len(crates)==4
lmin,lmax=bounds(lane)
assert abs(lmax[1]-8.4)<1e-3 and abs(lmax[0]-lmin[0]-1.7)<1e-3
bmin,bmax=bounds(stop)
assert bmin[1]>=8.3999 and bmin[2]>=-.0001 and bmax[1]<9.5,(bmin,bmax)
assert min(abs(v.x) for o in crates for v in pts(o))>2.4
def tree(obs):
    v,tr=[],[]
    for o in obs:
        o.data.calc_loop_triangles();i=len(v);v.extend(pts(o))
        tr.extend(tuple(i+k for k in t.vertices) for t in o.data.loop_triangles)
    return BVHTree.FromPolygons(v,tr,all_triangles=True)
t=tree(stop)
hit=lambda x,h:t.ray_cast((x,7,h),(0,1,0),3)[0] is not None
width_samples=[-.85+i*.05 for i in range(35)]
heights=[.32+i*.095 for i in range(9)]
assert all(hit(x,h) for x in width_samples for h in heights)
assert not any(hit(x,h) for x in (-1.85,1.85) for h in heights)
receipt=dict(scope='Optional E2 lane-end fixture in local review staging; no actor, stun, strike or level install.',
    hashes=pins,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),triangles=tri,texture_count=0,
    local_origin_direction='glTF front edge center; footprint extends -Z',staged_world_xyz=[0,0,-8.4],
    stop_bounds_blender=[bmin,bmax],lane_width_m=1.7,lane_length_m=8.4,
    blocked_face_rays=len(width_samples)*len(heights),clear_flank_rays=len(heights)*2,
    test_flank_x_m=[-1.85,1.85],crates_x=[-3.2,3.2],crates_z=[-3.85,-6.25])
(out/'art.json').write_text(json.dumps(receipt,indent=2)+'\n')
(out/'geometry.json').write_text(json.dumps(dict(stop=[dump(o) for o in stop],crates=[dump(o) for o in crates]),separators=(',',':'))+'\n')
print(receipt,flush=True)
if '--proof-only' in sys.argv:sys.exit(0)
floor=mat('Coarse rain-stained lane concrete',(.112,.143,.148),.03,.69)
m=floor.node_tree.nodes.get('Principled BSDF')
n=floor.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=33
p=floor.node_tree.nodes.new('ShaderNodeBump');p.inputs['Strength'].default_value=.17;p.inputs['Distance'].default_value=.02
floor.node_tree.links.new(n.outputs['Fac'],p.inputs['Height']);floor.node_tree.links.new(p.outputs['Normal'],m.inputs['Normal'])
box('Review floor',(0,7,-.12),(63,71,.24),floor,0)
sky=bpy.data.worlds.new('Warm steel yard dusk');s.world=sky;sky.use_nodes=True
bg=sky.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.41,.55,.70,1);bg.inputs['Strength'].default_value=.51
d=bpy.data.lights.new('Late sun','SUN');d.energy=3.05;d.angle=.095;d.color=(1,.81,.58)
o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o)
o.rotation_euler=Vector((-.39,.57,-1)).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=36;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.065
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
for label,at,target,lens,dims in [
 ('charge-stop-detail',(2.62,5.15,2.15),(0,8.58,.70),43,(1260,850)),
 ('charge-stop-lane',(.30,-2.35,1.76),(0,5.5,.65),31,(980,1280))]:
    bpy.ops.object.camera_add(location=at);c=bpy.context.object
    c.data.lens=lens;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c
    s.render.resolution_x,s.render.resolution_y=dims;s.render.resolution_percentage=100
    s.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)

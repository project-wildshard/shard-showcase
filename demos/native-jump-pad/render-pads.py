"""Build W6b graphically consistent pad and destination overlays."""
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[2]
trace,out=map(Path,sys.argv[sys.argv.index('--')+1:])
out.mkdir(parents=True,exist_ok=True)
t=json.loads(trace.read_text())
source=root/'public/assets/wildshard-art/wsc-plan-007-mover-jump-pad-casing.glb'
sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert sha=='4ae1b0e5df65cc5d56471b0bf2abd3b72b6a04d759f0418594a85482189d02d5'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete()
s=bpy.context.scene

def mat(n,c,metal=.35,rough=.53,e=0):
    m=bpy.data.materials.new(n)
    m.use_nodes=True;m.diffuse_color=(*c,1)
    q=m.node_tree.nodes.get('Principled BSDF')
    for k,v in {'Base Color':(*c,1),'Metallic':metal,'Roughness':rough,
                'Emission Color':(*c,1),'Emission Strength':e}.items():q.inputs[k].default_value=v
    return m

iron=mat('Tempered dark alloy',(.055,.086,.096),.68,.43)
ochre=mat('Ledge safety amber',(.71,.269,.038),.38,.57)
cyan=mat('Cyan vector enamel',(.021,.59,.70),.28,.36,.8)
zinc=mat('Rain brushed trim',(.21,.29,.28),.66,.44)
cement=mat('Weathered vertical concrete',(.218,.249,.244),.10,.86)
floor=mat('Rough blue slate',(.107,.143,.145),.09,.88)
timber=mat('Weathered birch trim',(.336,.21,.095),.05,.78)
sand=mat('West transit shoulder',(.227,.196,.108),.06,.83)
white=mat('Soft cyan trace guide',(.026,.71,.84),.07,.5,1.7)

def objmesh(n,vs,faces,m):
    d=bpy.data.meshes.new(n);d.from_pydata(vs,[],faces);d.update()
    d.materials.append(m)
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);return o
def box(n,p,d,m,b=.014):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d;o.data.materials.append(m)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if b:
        v=o.modifiers.new('Rounded milled edge','BEVEL');v.width=min(b,min(d)*.3);v.segments=1
    return o
def fin(n,x,y,z,length,width,m,ang=0):
    w=width*.5
    # Local west-facing chevron. Its two strips share an edge.
    vs=[(-length,0),(.0,w),(.11,w),(-length+.15,0),(.11,-w),(0,-w)]
    rot=Matrix.Rotation(ang,3,'Z')
    pts=[Vector((x,y,z))+rot@Vector((u,v,0)) for u,v in vs]
    return objmesh(n,pts,[(0,3,2,1),(0,5,4,3)],m)
def ringseg(n,a0,a1,r0,r1,z,nsteps,m):
    angles=[math.radians(a0+(a1-a0)*j/nsteps) for j in range(nsteps+1)]
    vs=[(r*math.cos(a),r*math.sin(a),z) for a in angles for r in [r0,r1]]
    return objmesh(n,vs,[(2*j,2*j+1,2*j+3,2*j+2) for j in range(nsteps)],m)
def export(n,parts):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    f=out/(n+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',use_selection=True,
                              export_apply=True,export_animations=False,export_texcoords=False)
    b=f.read_bytes();doc=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
    assert b[:4]==b'glTF' and len(b)<85000
    tris=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])
    for o in parts:bpy.data.objects.remove(o,do_unlink=True)
    return dict(bytes=len(b),triangles=tris,sha256=hashlib.sha256(b).hexdigest())
def proto(p):
    old=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.view_layer.update()
    ns=set(s.objects)-old
    result=[(o.name,o.data,o.matrix_world.copy()) for o in sorted(ns,key=lambda o:o.name) if o.type=='MESH']
    for o in ns:bpy.data.objects.remove(o,do_unlink=True)
    return result
def install(protos,p):
    T=Matrix.Translation(p);result=[]
    for n,d,m in protos:
        o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.matrix_world=T@m
        result.append(o)
    return result

donor=proto(source)
# Separate flat direction decal on the original lid, not a new pad collider.
parts=[fin('West flight chevron',x,0,.2535,.277,.59-i*.085,cyan) for i,x in enumerate([-.27,.020,.31])]
for a in [26,116,206,296]:
    parts.append(ringseg('Segmented vector rim',a,a+38,.795,.868,.2535,9,cyan))
assets={'w6b-jump-pad-vector':export('w6b-jump-pad-vector',parts)}
parts=[]
for y in [-2.34,2.34]:
    parts.append(box('Flush touchdown strip',(0,y,.005),(2.90,.175,.010),ochre,.002))
    for x in [-1.27,-.71,-.15,.41,.97]:
        parts.append(box('Treadded landing index',(x,y+(1 if y>0 else -1)*.235,.004),
                         (.13,.21,.008),cyan,.002))
for y in [-1.1,1.1]:
    parts.append(fin('Go on to the sliders',.37,y,.011,.72,.87,ochre))
assets['w6b-landing-index']=export('w6b-landing-index',parts)

def tree(pr):
    vs=[];faces=[]
    for _,data,M in pr:
        start=len(vs);vs.extend(M@v.co for v in data.vertices)
        data.calc_loop_triangles()
        faces.extend(tuple(start+i for i in p.vertices) for p in data.loop_triangles)
    return BVHTree.FromPolygons(vs,faces,all_triangles=True)
arrow=proto(out/'w6b-jump-pad-vector.glb')
landing=proto(out/'w6b-landing-index.glb')
donor_bvh=tree(donor)
offsets=[]
for _,data,M in arrow:
    data.calc_loop_triangles()
    for tri in data.loop_triangles:
        a,b,c=(M@data.vertices[i].co for i in tri.vertices)
        for i in range(6):
            for j in range(6-i):
                v=a+(b-a)*(i/5)+(c-a)*(j/5)
                p0=donor_bvh.ray_cast(Vector((v.x,v.y,.37)),Vector((0,0,-1)),.23)[0]
                assert p0 is not None
                offsets.append(v.z-p0.z)
assert min(offsets)>.001 and max(offsets)<.004,(min(offsets),max(offsets))
deck_half=[t['target']['halfWidth'],t['target']['halfDepth']]
lim=[max(abs((M@p.co)[i]) for _,d,M in landing for p in d.vertices) for i in range(2)]
assert all(a<b for a,b in zip(lim,deck_half))
report={k:v for k,v in t.items() if k!='results'}
report.update(slice='W6b',catalogue_id='WSC-PLAN-007',casing_sha256=sha,assets=assets,
    results=[{k:v for k,v in r.items() if k!='frames'} for r in t['results']],
    decorative_samples=len(offsets),pad_minimum_surface_offset_m=round(min(offsets),6),
    pad_maximum_surface_offset_m=round(max(offsets),6),landing_extents_m=lim,
    format_launch_row=False)
(out/'fit.json').write_text(json.dumps(report,indent=2)+'\n')

# Staged scene relative to the ledge centre (-121,6,-103).
for r in t['results']:
    dx=r['padX']+121
    install(donor,(dx,0,.12));install(arrow,(dx,0,.12))
install(landing,(0,0,6))
box('Receiver deck matching current scene', (0,0,5.75),(4,8,.5),cement,.059)
for x in [-1.5,1.5]:
    for y in [-3.2,3.2]:
        box('Staged footing',(x,y,.18),(.83,.83,.36),cement)
        box('Staged support',(x,y,2.85),(.49,.49,5.55),iron,.035)
for y in [-3.2,3.2]:
    box('Cross tie',(0,y,3.40),(3.52,.26,.34),iron)
    box('Receiver rim beam',(0,y,5.52),(3.85,.24,.35),zinc)
box('Long slab of pad seat',(11,0,.05),(20,8,.10),floor)
box('Cutaway ground',(8,0,-.205),(79,58,.41),sand)
for y in [-3.52,3.52]:
    for x in range(4,21,2):
        box('Hazard edge paint',(x,y,.103),(1.03,.14,.008),ochre,.002)
for y in [-3.01,3.01]:
    box('Deck end border',(0,y,6.004),(3.4,.076,.008),zinc,.002)
for x,y in [(-5,-5),(-6,5),(-9,-9),(22,9),(16,13),(32,12)]:
    box('Staging backdrop only',(x,y,.36),(2.0,1.5,.72),timber)

points=[]
for i,row in enumerate(t['results']):
    # A dotted trace of the actual player's feet; no guessed swoosh.
    for frame in row['frames']:
        k=frame['tick']
        if k%3!=0 or k>row['first']['tick'] or k==0:continue
        x,y,z=frame['feet']
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.065,location=(x+121,103*-1-z,y))
        o=bpy.context.object;o.name=f'Calibration path {i+1} step {k}';o.data.materials.append(white)
        points.append(o)
s.world=bpy.data.worlds.new('Blue ambient sky');s.world.use_nodes=True
w=s.world.node_tree.nodes.get('Background');w.inputs[0].default_value=(.18,.31,.48,1);w.inputs[1].default_value=.43
sun=bpy.data.lights.new('Grazing dry sundown','SUN');sun.energy=2.85;sun.color=(1,.82,.62);sun.angle=.17
o=bpy.data.objects.new(sun.name,sun);s.collection.objects.link(o);o.rotation_euler=(.38,-.54,-.27)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(n,p,q,e,c,w):
    l=bpy.data.lights.new(n,'AREA');l.energy=e;l.color=c;l.shape='DISK';l.size=w
    o=bpy.data.objects.new(n,l);s.collection.objects.link(o);o.location=p;aim(o,q)
area('Blue sky fill',(13,-11,11),(6,0,2),3700,(.58,.82,1),10)
cam=bpy.data.cameras.new('Pad and ledge views')
s.camera=bpy.data.objects.new(cam.name,cam);s.collection.objects.link(s.camera)
cam.type='ORTHO'
s.render.engine='CYCLES';s.cycles.samples=42;s.cycles.adaptive_threshold=.071;s.cycles.use_denoising=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_x=1400;s.render.resolution_y=890;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94
def shoot(n,p,q,size):
    s.camera.location=p;aim(s.camera,q);cam.ortho_scale=size
    s.render.filepath=str(out/(n+'.jpg'));bpy.ops.render.render(write_still=True)
for o in points:o.hide_render=True
shoot('w6b-pad-direction',(16,-9,8),(11,0,.44),15)
for o in points:o.hide_render=False
shoot('w6b-ledge-path',(7,-25,18),(8,0,3.55),25.4)

"""E8b Big Pallet's ring, using the original Round 5 pit outline."""
from math import cos, sin, pi
from pathlib import Path
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import sys, hashlib, json, struct

args=sys.argv[sys.argv.index("--")+1:]
assert len(args) in (1,2)
out=Path(args[0]);out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
def clear():
    for o in list(scene.objects):bpy.data.objects.remove(o,do_unlink=True)
clear()

def mat(name,col,metal=0,rough=.55):
    m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    return m
basalt=mat('Cast smoke-brown concrete',(.161,.117,.089),.03,.85)
oxide=mat('Burnt-sienna impact panels',(.43,.124,.039),.33,.54)
ochre=mat('Saffron abrasion paint',(.73,.352,.035),.28,.47)
black=mat('Graphite capped plate',(.047,.057,.051),.50,.50)
steel=mat('Rain brushed hardware',(.246,.263,.241),.72,.36)
earth=[mat('Dry earth '+str(i),(.190+i*.011,.098+i*.006,.048+i*.004),.02,.91) for i in range(5)]
def mesh(name,vs,fs,ms,mi=None):
    m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs)
    for material in ms:m.materials.append(material)
    if mi is not None:
        for q,k in zip(m.polygons,mi):q.material_index=k
    o=bpy.data.objects.new(name,m);scene.collection.objects.link(o);return o

def shell(name,a,b,radii,zs,ms,slots,n=64):
    w=len(radii)
    vs=[(r*cos(a+(b-a)*k/n),r*sin(a+(b-a)*k/n),z)
        for k in range(n+1) for r,z in zip(radii,zs)]
    fs=[];tags=[]
    for k in range(n):
        for j in range(w):
            j1=(j+1)%w
            fs.append((k*w+j,(k+1)*w+j,(k+1)*w+j1,k*w+j1))
            tags.append(slots(j,k))
    fs.extend((tuple(range(w)),tuple(reversed(range(w*n,w*(n+1))))))
    tags.extend([0,0])
    return mesh(name,vs,[tuple(reversed(f)) for f in fs],ms,tags)

def block(n,p,d,m,bevel=.025,yaw=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=d;o.rotation_euler.z=yaw
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if bevel:
        q=o.modifiers.new("Formed edge","BEVEL");q.width=bevel;q.segments=1
        o.modifiers.new("Weighted faces","WEIGHTED_NORMAL")
    return o

# Local X east, Y north in Blender. The exits are centered due north/south.
spans=[(-pi/2+.25,pi/2-.25),(pi/2+.25,3*pi/2-.25)]
walls=[]
for i,(a,b) in enumerate(spans):
    walls.append(shell(f'Basalt split-ring wall {i+1}',a,b,[12,12,12.14,13.86,14,14],
          [.0,1.12,1.40,1.40,1.19,.0],[basalt,oxide,ochre,black],
          lambda j,k: (1 if j==1 else 2 if j==2 and (k//2)%2==0 else 3 if j in (2,3) else 0)))
    walls.append(shell(f'Continuous recessed bumper {i+1}',a,b,[11.964,11.964,12.08,12.08],
          [.23,.375,.375,.23],[black],lambda j,k:0))
    walls.append(shell(f'Upper recessed rail {i+1}',a,b,[11.946,11.946,12.065,12.065],
          [.877,1.001,1.001,.877],[steel],lambda j,k:0))
    for k in range(18):
        phi=a+(b-a)*(k+.50)/18
        for z in (.43,.92):
            r=11.927
            walls.append(block('Countersunk field joint',(r*cos(phi),r*sin(phi),z),
                               (.030,.12,.095),steel,.009,phi))
    for phi in (a+.034,b-.034):
        r=12.40
        walls.append(block('Gate-end vertical armor',(r*cos(phi),r*sin(phi),.65),
                           (.65,.15,1.18),black,.036,phi))

# Archival disc at z=.05. No buried tread/room floor assumptions: outside it
# the study has no export. Small surface color differences are textureless.
steps,segments=12,96
vs=[(0,0,.05)]
for k in range(1,steps+1):
    for j in range(segments):
        t=2*pi*j/segments;r=12*k/steps
        vs.append((r*cos(t),r*sin(t),.05))
fs=[(0,1+j,1+(j+1)%segments) for j in range(segments)]
for k in range(steps-1):
    p=1+k*segments
    for j in range(segments):
        t=(j+1)%segments
        fs.append((p+j,p+j+segments,p+t+segments,p+t))
def soil_tone(f):
    x=sum(vs[i][0] for i in f)/len(f)
    y=sum(vs[i][1] for i in f)/len(f)
    grooves=min(abs(y+.070*(x*x)-v) for v in (-3.8,-1.9))
    if x*x+y*y>100:return 1
    if abs(x)<10 and grooves<.21:return 0
    return 2+round(1.45*sin(1.9*x+.55*y)*cos(2.2*y))
tonal=[soil_tone(f) for f in fs]
floor=mesh("Arced yard floor | 12 m radius",vs,fs,earth,tonal)
# Provisional twin obstacles; there was no pillar placement in the R5 lab.
pillars=[]
for x,y in ((-6.8,.6),(6.8,-.6)):
    pillars += [
      block("Square pad and toe plate",(x,y,.17),(1.62,1.62,.24),basalt,.08),
      block("Pillar body",(x,y,1.44),(1.18,1.18,2.50),oxide,.065),
      block("Counterweight dark foot",(x,y,.38),(1.31,1.31,.34),black,.035),
      block("Forged top cap",(x,y,2.79),(1.38,1.38,.22),black,.047),
      block("Ochre wear band",(x,y,1.04),(1.26,1.26,.20),ochre,.027)]
    for side in (-1,1):
        for dx in (-.395,.395):
            pillars.append(block("Pressed vertical impact recess",(x+dx,y+side*.59,1.86),
                                 (.225,.074,1.13),black,.025))
            pillars.append(block("Recess return band",(x+dx,y+side*.635,1.86),
                                 (.12,.031,.99),oxide,.012))
    for dx in (-.39,.39):
        pillars.append(block("Inset steel fastener",(x+dx,y-.598,1.21),(.115,.065,.105),steel,.018))

# Collapse each named assembly independently into material primitives.
# Retain mesh/control origin at floor-centre in the exported scene.
def merge(name,objects,materials):
    bvh=bpy.context.evaluated_depsgraph_get()
    coords,faces,slots,normals=[],[],[],[]
    index={m.name:i for i,m in enumerate(materials)}
    for o in objects:
        e=o.evaluated_get(bvh);m=e.to_mesh()
        try:
            n=len(coords);T=e.matrix_world;N=T.to_3x3().inverted_safe().transposed()
            coords.extend(tuple(T@v.co) for v in m.vertices)
            for f in m.polygons:
                faces.append(tuple(n+i for i in f.vertices));slots.append(index[m.materials[f.material_index].name])
                normals.extend(tuple((N@m.corner_normals[i].vector).normalized()) for i in f.loop_indices)
        finally:e.to_mesh_clear()
    for o in objects:bpy.data.objects.remove(o,do_unlink=True)
    result=mesh(name,coords,faces,materials,slots)
    for f in result.data.polygons:f.use_smooth=True
    result.data.normals_split_custom_set(normals)
    return result
bpy.context.view_layer.update()
parts=[floor,merge("Split wall assembly",walls,[basalt,oxide,ochre,black,steel]),
       merge("Pair of provisional pillared obstacles",pillars,[basalt,oxide,ochre,black,steel])]
bpy.ops.object.select_all(action="DESELECT")
for o in parts:o.select_set(True)
path=out/"e8b-big-pallet-pit.glb"
bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",use_selection=True,export_apply=True,
                         export_animations=False,export_texcoords=False)
raw=path.read_bytes()
document=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
prims=[p for m in document['meshes'] for p in m['primitives']]
ntri=sum(document['accessors'][p['indices']]['count']//3 for p in prims)
assert len(raw)<420000 and ntri<14000 and not document.get("images"),(len(raw),ntri)
clear()
bpy.ops.import_scene.gltf(filepath=str(path))
bpy.context.view_layer.update()
vs,fs=[],[]
for o in sorted(scene.objects,key=lambda o:o.name):
    if o.type!="MESH":continue
    n=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
    fs.extend(tuple(n+i for i in f.vertices) for f in o.data.polygons)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
bounds=[tuple(f(v[j] for v in vs) for j in range(3)) for f in (min,max)]
assert abs(bounds[0][0]+14)<.005 and abs(bounds[1][0]-14)<.005
def cast(origin,direction,distance):
    return bvh.ray_cast(Vector(origin),Vector(direction),distance)[0]
samples=[i*.10 for i in range(-28,29)]
assert all(cast((x,sign*16,z),(0,-sign,0),32) is None for x in samples for z in (.25,.75,1.30) for sign in (-1,1))
assert all(cast((sign*16,y,.70),(-sign,0,0),5) is not None for y in (-3,0,3) for sign in (-1,1))
assert all(abs(cast((x,y,5),(0,0,-1),6).z-.05)<1e-5 for x in (-3,0,3) for y in range(-10,11))
assert all(abs(cast((x,y,5),(0,0,-1),6).z-2.90)<1e-5 for x,y in [(-6.8,.6),(6.8,-.6)])
(out/"pit-blender.json").write_text(json.dumps(dict(
    sourceCenterThree=[96,0,-206],archivedFloorRadiusM=12,
    outerWallRadiusM=14,gapAngleRads=.5,nominalInnerGapM=24*sin(.25),
    clearLaneWidthTestedM=5.6,clearLaneRays=342,crossWallControls=6,flatFloorProbes=63,
    pillarHeightM=2.90,pillarXs=[-6.8,6.8],pillarThreeZOffsets=[-.6,.6],
    bytes=len(raw),triangles=ntri,drawPrimitives=len(prims),boundsBlender=bounds,
    sha256=hashlib.sha256(raw).hexdigest()),indent=2)+"\n")
if len(args)==1:raise SystemExit(0)

# Context staging for photos only: clear both mouths, and keep the kit
# self-contained without duplicating the existing pallet export.
repo=Path(__file__).resolve().parents[3]
parts_before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(repo/"public/assets/wildshard-art/wsc-prop-009-stacked-pallets.glb"))
roots=sorted([o for o in set(scene.objects)-parts_before if o.parent is None],key=lambda o:o.name)
palette=[o for o in set(scene.objects)-parts_before if o.type=="MESH"]
assert roots and len(roots)==len(palette)
for k,(x,y,a) in enumerate([(9.2,-6.1,.6),(-9,5.6,-.5),(-9.1,-6.4,.53),(9.45,4.8,-.62)]):
    T=Matrix.Translation((x,y,.05))@Matrix.Rotation(a,4,"Z")
    for o in palette:
        p=o if k==3 else o.copy()
        if k!=3:scene.collection.objects.link(p)
        p.matrix_world=T@o.matrix_world
ground=mat("Surrounding warm loam",(.15,.096,.057),.01,.88)
block("Studio surround only",(0,0,-.105),(180,180,.20),ground,0)
scene.render.engine="CYCLES";scene.cycles.samples=36
scene.cycles.use_denoising=False;scene.cycles.adaptive_threshold=.045
scene.render.resolution_percentage=100;scene.render.image_settings.file_format="JPEG";scene.render.image_settings.quality=94
scene.view_settings.view_transform="AgX"
scene.world=bpy.data.worlds.new("Blue above the pit");scene.world.use_nodes=True
p=scene.world.node_tree.nodes["Background"];p.inputs[0].default_value=(.37,.47,.57,1);p.inputs[1].default_value=.58
bpy.ops.object.light_add(type="SUN",location=(-9,-7,12))
s=bpy.context.object;s.rotation_euler=Vector((.54,.39,-.73)).to_track_quat('-Z','Y').to_euler()
s.data.energy=2.75;s.data.angle=.14;s.data.color=(1,.86,.75)
bpy.ops.object.camera_add()
camera=bpy.context.object;scene.camera=camera
def shot(name,eye,aim,lens,w,h):
    camera.location=eye;camera.rotation_euler=(Vector(aim)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.lens=lens;scene.render.resolution_x=w;scene.render.resolution_y=h
    scene.render.filepath=str(out/(name+".jpg"));bpy.ops.render.render(write_still=True)
shot("nov25-e8b-pit-arrival",(-2.25,-12.8,1.75),(0,4,1.12),27,1300,820)
shot("nov25-e8b-pit-overhead",(19,-24,21),(0,0,.65),35,1340,900)

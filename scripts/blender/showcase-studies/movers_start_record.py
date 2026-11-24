"""Static W6d Movers start and world record board, fitted to the pinned yard."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

HERE=Path(__file__).resolve().parent
base,out=(Path(p).resolve() for p in sys.argv[sys.argv.index('--')+1:])
out.mkdir(parents=True,exist_ok=True)
finger=json.loads((base/'parity.json').read_text())['movers']['matched_signature']
assert finger==json.loads((HERE.parent/'west-movers-roof/expected.json').read_text())['movers']['semantic_signature']
bpy.ops.wm.open_mainfile(filepath=str(base/'movers/west-r02-plus-movers-editable.blend'))
sc=bpy.context.scene
sc.render.use_compositing=False


def tree(obs):
    v,f=[],[]
    dg=bpy.context.evaluated_depsgraph_get()
    for original in obs:
        o=original.evaluated_get(dg)
        m=o.to_mesh();n=len(v)
        v.extend(o.matrix_world@p.co for p in m.vertices)
        f.extend(tuple(n+i for i in p.vertices) for p in m.polygons)
        o.to_mesh_clear()
    assert f
    return BVHTree.FromPolygons(v,f)


def measure(t,x,y,z0=3,span=6):
    p=t.ray_cast(Vector((x,y,z0)),Vector((0,0,-1)),span)[0]
    assert p is not None,(x,y,z0,span)
    return p.z


start=Vector((-74,90,0))
board_anchor=Vector((-66,96,0))
direction=(Vector((-84,103,0))-start).normalized()
front=(start-board_anchor).normalized()
stage_objs=[o for o in sc.objects if o.type=='MESH']
t=tree(stage_objs)
base_samples=[measure(t,start.x+dx,start.y+dy) for dx,dy in
              [(0,0),(-2.90,0),(2.90,0),(0,-2.90),(0,2.90)]]
assert max(base_samples)-min(base_samples)<.001
start.z=base_samples[0]
board_anchor.z=measure(t,board_anchor.x,board_anchor.y)
assert -.10 < board_anchor.z < .20


def mat(n,c,metal=.15,em=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    s=m.node_tree.nodes['Principled BSDF']
    s.inputs['Base Color'].default_value=(*c,1)
    s.inputs['Metallic'].default_value=metal
    s.inputs['Roughness'].default_value=.47
    s.inputs['Emission Color'].default_value=(*c,1)
    s.inputs['Emission Strength'].default_value=em
    return m


charcoal=mat('Movers dark steel',(.049,.086,.091),.48)
ochre=mat('Movers warning orange',(.59,.173,.037),.32)
steel=mat('Movers worn rail',(.30,.36,.32),.57)
glass=mat('Matte smoked board',(.021,.050,.063),.12)
pale=mat('Ready display white',(.84,.88,.79),.07,.45)
copper=mat('Inactive amber type',(.88,.39,.083),.15,.65)
teal=mat('Start cyan enamel',(.035,.39,.39),.24,.10)
mint=mat('Start cyan inlay',(.14,.75,.63),.07,.45)


def mesh(name,v,f,m):
    d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.materials.append(m)
    o=bpy.data.objects.new(name,d);sc.collection.objects.link(o)
    return o


def box(n,p,d,m):
    x,y,z=p;a,b,c=[x*.5 for x in d]
    return mesh(n,[(x+i*a,y+j*b,z+k*c) for k in (-1,1) for j in (-1,1) for i in (-1,1)],
         [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m)


def disc(name,r0,r1,lo,hi,m,N=56):
    verts=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z)
           for r,z in [(r0,lo),(r1,lo),(r1,hi),(r0,hi)] for i in range(N)]
    faces=[]
    for a in range(4):
        b=(a+1)%4
        for i in range(N):
            j=(i+1)%N
            faces.append((a*N+i,a*N+j,b*N+j,b*N+i))
    return mesh(name,verts,faces,m)


def text(name,s,x,z,size,m,y=-.196):
    c=bpy.data.curves.new(name,'FONT');c.body=s;c.align_x='CENTER';c.size=size;c.materials.append(m)
    o=bpy.data.objects.new(name,c);sc.collection.objects.link(o)
    o.location=(x,y,z);o.rotation_euler=(math.pi/2,0,0)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    return o


pad=[
    disc('Start pad · outer edging',2.78,3.0,-.012,.032,charcoal),
    disc('Start pad · edge inlay',2.68,2.83,.020,.049,mint),
    disc('Start pad · inner surround',2.58,2.69,.010,.043,ochre)]
v=[(2.60*math.cos(i*math.tau/56),2.60*math.sin(i*math.tau/56),.041) for i in range(56)]
pad.append(mesh('Start pad · quiet center',v,[tuple(range(len(v)))],teal))
for y in (-.8,-.06,.68):
    pad.append(mesh('Direction chevron',[(-.60,y,.052),(0,y+.39,.052),(.60,y,.052),
          (.60,y+.18,.052),(0,y+.60,.052),(-.60,y+.18,.052)],[tuple(range(6))],mint))
# The world-readable display has no test times presented as measured records.
board=[
    box('Record board · housing',(0,0,1.90),(2.92,.31,1.72),ochre),
    box('Record board · dark solar visor',(0,-.06,2.79),(3.02,.59,.09),charcoal),
    box('Record board · face',(0,-.159,1.90),(2.72,.06,1.48),glass)]
for x in (-1.05,1.05):
    board += [box('Board standard',(x,0,.58),(.19,.26,1.16),steel),
              box('Board plinth flange',(x,0,.065),(.52,.52,.13),charcoal),
              box('Housing leg collar',(x,0,1.04),(.29,.36,.27),charcoal)]
for z in (1.44,1.90,2.19):
    board.append(box('Record row separator',(0,-.191,z),(2.49,.018,.021),steel))
board += [text('World display title','MOVERS TIME',0,2.41,.22,pale),
          text('Best field legend','BEST',-.96,1.98,.15,pale),
          text('Last field legend','LAST',-.96,1.57,.15,pale),
          text('Best blank field','--:--.--',.54,1.97,.21,copper),
          text('Last blank field','--:--.--',.54,1.56,.21,copper),
          text('Board state','READY  /  6 STATIONS',0,1.21,.113,mint)]
for x in (-1.29,1.29):
    for z in (1.37,2.52):
        board.append(box('Face latch',(x,-.206,z),(.115,.055,.095),steel))

asset_info={}
placed=[]
for key,objs,T in [
    ('start-pad',pad,Matrix.Translation(start)@Matrix.Rotation(math.atan2(-direction.x,direction.y),4,'Z')),
    ('record-board',board,Matrix.Translation(board_anchor)@Matrix.Rotation(math.atan2(front.x,-front.y),4,'Z'))]:
    path=out/('w6d-movers-'+key+'.glb')
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False)
    raw=path.read_bytes()
    assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
    g=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
    assert not any(k in g for k in ('images','animations','skins','cameras'))
    asset_info[key]={'bytes':len(raw),'triangles':sum(g['accessors'][p['indices']]['count']//3
        for mesh0 in g['meshes'] for p in mesh0['primitives']),'sha256':hashlib.sha256(raw).hexdigest()}
    for o in objs:bpy.data.objects.remove(o,do_unlink=True)
    before=set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    incoming=sorted(set(sc.objects)-before,key=lambda o:o.name)
    for o in incoming:
        if o.parent not in incoming:o.matrix_world=T@o.matrix_world
    placed.append([o for o in incoming if o.type=='MESH'])
bpy.context.view_layer.update()
assert abs(measure(tree(placed[0]), start.x,start.y)-start.z-.041)<5e-5
footing=[]
for q in (-1.05,1.05):
    side=Vector((-front.y,front.x,0));p=board_anchor+side*q
    z=measure(t,p.x,p.y)
    footing.append(round(z,5))
    assert abs(z-board_anchor.z)<.025
mark=board_anchor+front*.198+Vector((0,0,2.5))
view=start+Vector((0,0,1.7))
vec=mark-view
assert t.ray_cast(view,vec.normalized(),vec.length-.08)[0] is None

for o in list(sc.objects):
    if o.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(o,do_unlink=True)
world=bpy.data.worlds.new('Movers west afternoon');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.33,.46,.60,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.34
sc.world=world


def lamp(n,kind,p,target,power,size,c):
    d=bpy.data.lights.new(n,kind);d.energy,d.color=power,c
    if kind=='SUN':d.angle=size
    else:d.size=size
    o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.location=p
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()


lamp('Sun on the hardware','SUN',(-92,78,18),(-70,92,0),2.25,.11,(1,.78,.56))
lamp('Cool sign fill','AREA',(-74,89,7),(-66,96,2),580,6,(.66,.81,1))
cam=bpy.data.objects.new('Movers review camera',bpy.data.cameras.new('Movers review camera'))
sc.collection.objects.link(cam);sc.camera=cam
sc.render.use_compositing=False;sc.render.engine='CYCLES'
sc.cycles.samples=52;sc.cycles.use_denoising=False
sc.cycles.use_adaptive_sampling=True;sc.cycles.adaptive_threshold=.056
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG'
sc.render.image_settings.quality=91;sc.view_settings.view_transform='AgX'


def shot(n,p,target,lens,wh):
    cam.location=p;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens;sc.render.resolution_x,sc.render.resolution_y=wh
    sc.render.filepath=str(out/(n+'.jpg'));bpy.ops.render.render(write_still=True)


shot('movers-overview',(-82.7,80.8,6.8),(-71.0,92.5,.8),37,(1340,880))
shot('movers-board',view,board_anchor+Vector((0,0,1.86)),74,(1180,860))
for dx in (-1.35,1.35):
    p=world_to_camera_view(sc,cam,mark+Vector((-front.y,front.x,0))*dx)
    assert 0<p.x<1 and 0<p.y<1
proof={'scope':'Static W6d entry art: no timing, stats, trigger zone, clocks or movement.',
       'archive':'ce1cf050b3 Round 5 MOVERS and lab buildMovers','base_semantic_signature':finger,
       'start_map_xz':[-74,-90],'board_map_xz':[-66,-96],'start_radius_m':3,
       'separation_m':round((board_anchor-start).xy.length,5),
       'terrain_start_z_m':[round(z,5) for z in base_samples],
       'board_footing_z_m':footing,'board_faces_start':True,
       'start_view_title_ray_clear':True,'record_fields':['BEST --:--.--','LAST --:--.--'],
       'course_station_count':6,'assets':asset_info}
(out/'w6d-movers-start.json').write_text(json.dumps(proof,indent=2)+'\n')

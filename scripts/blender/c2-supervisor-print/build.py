"""Optional Supervisor print on the existing C2 cloth, with no lift changes."""
import hashlib
import json
from pathlib import Path
import struct
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
root = here.parents[2]
dep = root / 'public/assets/wildshard-art'
pit = dep / 'wsc-scene-007-c2-pit.glb'
pin = '90cff3a5ab2706987585417d898fe8fe0b42823f9be01c9dd34196cb9f8dfbd5'
assert hashlib.sha256(pit.read_bytes()).hexdigest() == pin
layout = json.loads((root/'project/layouts/wsc-scene-007-c2-pit.json').read_text())
lift = json.loads((root/'project/layouts/e11c-reveal-lift-native-proof.json').read_text())
assert lift['worldOrigin']==[55,0,229] and lift['firstTopTick']==150
assert lift['layout']==layout['donors_sha256']
out = Path(sys.argv[sys.argv.index('--')+1])
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
bpy.ops.import_scene.gltf(filepath=str(pit))
cloth=[bpy.data.objects[n] for n in ('13 Cloth banner','13 Cloth banner.001')]
ink=bpy.data.objects['13 Cloth banner.002']
assert ink.active_material.name=='Pale stamped chevrons'
deck=bpy.data.objects['C2_Lift_Moving_Deck']
bpy.context.view_layer.update()

def geo(objects):
    vertices, faces = [], []
    for o in objects:
        if o.type!='MESH':continue
        i=len(vertices)
        vertices.extend(o.matrix_world@v.co for v in o.data.vertices)
        faces.extend(tuple(i+k for k in p.vertices) for p in o.data.polygons)
    return vertices,faces

def tree(objects):
    return BVHTree.FromPolygons(*geo(objects))

cloth_tree=tree(cloth)
# The exact donor cloth is sourced by ray, not approximated with the old
# flat-chevrons plane. Work in C2-local Blender coordinates.
def sample(x,z):
    q,*_=cloth_tree.ray_cast(Vector((x,-19,z)),Vector((0,-1,0)),3.5)
    assert q is not None, (x,z)
    return q.y
def mat(name,col,rough,em=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*col,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Emission Color'].default_value=(*col,1)
    p.inputs['Emission Strength'].default_value=em
    return m
cream=mat('Warm signal ivory',(.92,.85,.65),.68,.15)
navy=mat('Blue-black enamel ink',(.021,.055,.065),.78)
bronze=mat('Old signal brass ink',(.58,.263,.079),.67)
groups={m: ([],[]) for m in (cream,navy,bronze)}
def tri(a,b,c,m,off):
    if max((a-b).length,(a-c).length,(c-b).length)>.20:
        ab=(a+b)*.5;bc=(b+c)*.5;ca=(c+a)*.5
        for u,v,w in [(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)]:
            tri(u,v,w,m,off)
        return
    arr,faces=groups[m]
    idx=len(arr)
    arr.extend((v.x,sample(v.x,v.y)+off,v.y) for v in (a,b,c))
    faces.append((idx,idx+1,idx+2))
def contour(points,m,off):
    from mathutils.geometry import tessellate_polygon
    poly=[Vector((x,z)) for x,z in points]
    for p in tessellate_polygon([poly]):
        tri(*(poly[i] for i in p),m,off)
def type_line(body,y,width,height,m):
    font=bpy.data.curves.new(body,'FONT')
    font.body=body
    font.align_x='CENTER'
    font.align_y='CENTER'
    font.space_character=1.08
    font.resolution_u=2
    ob=bpy.data.objects.new(body,font)
    s.collection.objects.link(ob)
    bpy.context.view_layer.update()
    data=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob,do_unlink=True)
    data.calc_loop_triangles()
    pts=[v.co for v in data.vertices]
    minx,maxx=min(v.x for v in pts),max(v.x for v in pts)
    miny,maxy=min(v.y for v in pts),max(v.y for v in pts)
    pts=[Vector((((maxx+minx)*.5-v.x)*width/(maxx-minx),y+(v.y-(maxy+miny)*.5)*height/(maxy-miny))) for v in pts]
    for t in data.loop_triangles:
        a,b,c=[pts[i] for i in t.vertices]
        tri(a,b,c,m,.068)
    bpy.data.meshes.remove(data)

# Large icon reads before text; estate/actor badges are deliberately absent.
# X/Z polygon winding yields north-facing front faces.
def shield(cx,y,r,m,off):
    contour([(cx+x*r,y+z*r) for x,z in [(-.8,.67),(.8,.67),(.8,-.15),(.55,-.5),(0,-.83),(-.55,-.5),(-.8,-.15)]][::-1],m,off)
shield(0,11.77,1.22,bronze,.050)
shield(0,11.77,1.07,navy,.060)
contour([(-.09,12.31),(-.52,11.65),(-.045,11.65),(-.20,11.13),(.40,11.87),(-.06,11.87),(.12,12.31)],cream,.073)
type_line('SHIFT',10.32,2.42,.55,cream)
type_line('SUPERVISOR',9.51,5.12,.64,cream)
for side in (-1,1):
    x=side*2.26
    for j in range(3):
        pos=x+(j-1)*.27
        contour([(pos-.085,10.09),(pos+.058,10.09),(pos+.163,10.53),(pos+.02,10.53)],cream,.068)

obs=[]
for m,(v,f) in groups.items():
    # Weld coincident vertices. Remove isolated numerical zero-area faces.
    idx={}
    vv,ff=[],[]
    for face in f:
        ids=[]
        for i in face:
            k=tuple(round(a,6) for a in v[i])
            if k not in idx:idx[k]=len(vv);vv.append(k)
            ids.append(idx[k])
        if len(set(ids))==3:
            a,b,c=(Vector(vv[i]) for i in ids)
            normal=(b-a).cross(c-a)
            if abs(normal.y)>1e-9:
                ff.append(ids if normal.y<0 else ids[::-1])
    g=bpy.data.meshes.new(m.name)
    g.from_pydata(vv,[],ff)
    g.update()
    for poly in g.polygons:poly.use_smooth=True
    o=bpy.data.objects.new('C2 Supervisor print | '+m.name,g)
    s.collection.objects.link(o)
    g.materials.append(m)
    obs.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in obs:o.select_set(True)
filename=out/'wsc-scene-007-c2-supervisor-print.glb'
bpy.ops.export_scene.gltf(filepath=str(filename),export_format='GLB',use_selection=True,export_animations=False)
for o in obs:bpy.data.objects.remove(o,do_unlink=True)
prior=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(filename))
obs=sorted(set(s.objects)-prior,key=lambda o:o.name)
raw=filename.read_bytes()
gltf=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert not any(k in gltf for k in ('images','textures','animations','skins'))
tri_count=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives'])
assert tri_count<4500 and len(raw)<140_000,(tri_count,len(raw))
bpy.context.view_layer.update()
v,ff=geo(obs)
standoff=[]
for f in ff:
    q=sum((v[i] for i in f),Vector())/len(f)
    standoff.append(q.y-sample(q.x,q.z))
assert .016<min(standoff)<max(standoff)<.11,(min(standoff),max(standoff))
lowest=min(q.z for q in v)
maxdeck=4
minDeckClear=lowest-maxdeck
assert minDeckClear>5

# Three eye-height approaches. Count visible ink triangle barycenters,
# including court meshes as blockers; omit the replaced pale-only node.
reference=tree([o for o in s.objects if o not in obs and o!=ink])
cameras=[(-8.2,-2.5,1.70),(0,-2.1,1.70),(8.2,-2.5,1.70)]
visible=[]
for eye in map(Vector,cameras):
    seen=0
    for f in ff:
        p=sum((v[i] for i in f),Vector())/len(f)
        d=p-eye
        hit,*_=reference.ray_cast(eye,d.normalized(),d.length-.006)
        seen+=hit is None
    visible.append(seen)
assert min(visible)==len(ff),(visible,len(ff))
proof=dict(scope='Optional print on unchanged C2 cloth and room GLB; original chevron node hidden only to show alternate print.',
    donorSha256=pin,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),triangles=tri_count,
    materials=len(gltf['materials']),textures=0,hideNode=ink.name,
    heightMinM=round(lowest,5),riseM=maxdeck,minVerticalDeckSeparationM=round(minDeckClear,5),
    clearanceFromClothM=[round(min(standoff),6),round(max(standoff),6)],
    cameraLocalBlender=cameras,visibleGeometrySamples=visible,samplesPerCamera=len(ff))
(out/'e11c-c2-supervisor-print.json').write_text(json.dumps(proof,indent=2)+'\n')
print(proof,flush=True)
if '--proof-only' in sys.argv:sys.exit(0)

def aim(o,t):
    o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,kind,at,target,energy,color,size):
    d=bpy.data.lights.new(name,kind)
    d.energy,d.color=energy,color
    if kind=='SUN':d.angle=size
    else:d.shape,d.size='DISK',size
    o=bpy.data.objects.new(name,d)
    s.collection.objects.link(o)
    o.location=at
    aim(o,target)
s.world=bpy.data.worlds.new('Blue overcast')
s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.21,.35,.50,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.56
light('Apricot court sky','SUN',(-22,13,21),(0,-17,0),2.2,(1,.76,.49),.11)
light('Cold shaft fill','AREA',(5,-12,7),(0,-17,0),2400,(.52,.72,1),7)
light('Banner wash','AREA',(-2,-14.8,9.8),(0,-20,10.8),1000,(1,.86,.69),4)
bpy.ops.object.camera_add()
cam=bpy.context.object
s.camera=cam
s.render.engine='CYCLES'
s.cycles.samples=28
s.cycles.use_denoising=False
s.cycles.adaptive_threshold=.073
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG'
s.render.image_settings.quality=92
ink.hide_render=True
for name,at,target,ll,dims in [
    ('approach',cameras[0],(0,-17,6.1),25,(860,1180)),
    ('lift-raised',(-8.1,-9.2,5.7),(0,-17.5,7.2),28,(1280,900)),
]:
    cam.location=at
    aim(cam,target)
    cam.data.lens=ll
    s.render.resolution_x,s.render.resolution_y=dims
    bpy.context.view_layer.update()
    assert all(0<q.x<1 and 0<q.y<1 for q in [world_to_camera_view(s,cam,p) for p in v])
    title=[world_to_camera_view(s,cam,p) for p in v if p.z<9.84]
    assert (max(q.y for q in title)-min(q.y for q in title))*dims[1] > 19
    # The first glyph in the donor font raster order now maps to left in
    # the north-facing review; confirm the chosen camera frame does not flip.
    assert world_to_camera_view(s,cam,Vector((2,-20.35,9.5))).x < world_to_camera_view(s,cam,Vector((-2,-20.35,9.5))).x
    s.render.filepath=str(out/f'c2-supervisor-{name}.jpg')
    bpy.ops.render.render(write_still=True)

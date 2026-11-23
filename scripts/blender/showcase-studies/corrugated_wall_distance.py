"""WSC-MODULE-020 distance bay. Build from the exact donor fold section, not the graphite fence."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

OUT=output_directory()
SOURCE=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art/wsc-module-020-corrugated-yard-wall.glb'
clear_scene()
S=bpy.context.scene

def load(path):
    have=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    fresh=set(S.objects)-have
    ob,=[o for o in fresh if o.type=='MESH']
    return ob,fresh

def info(path,obj):
    raw=path.read_bytes()
    n=struct.unpack_from('<I',raw,12)[0]
    doc=json.loads(raw[20:20+n])
    coords=[obj.matrix_world@v.co for v in obj.data.vertices]
    bounds=[[round(fn(v[i] for v in coords),6) for i in range(3)] for fn in (min,max)]
    p=doc['meshes'][0]['primitives']
    return dict(file=path.name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                triangles=sum(doc['accessors'][q['indices']]['count']//3 for q in p),
                material_primitives=len(p),blender_bounds_m=bounds,
                embedded_images=len(doc.get('images',[])),node_count=len(doc['nodes']))

orig,original_nodes=load(SOURCE)
near=info(SOURCE,orig)
assert near['triangles']==9436 and near['bytes']==821832
assert (orig.matrix_world.translation-Vector((0,0,0))).length<1e-7
# Restrict to the stamped sheet's lower cross-section, excluding orange top caps.
profile={}
for p in orig.data.polygons:
    if p.material_index!=0:
        continue
    for i in p.vertices:
        x,y,z=orig.matrix_world@orig.data.vertices[i].co
        if abs(z-.47)<1e-6 and abs(x)<.961:
            profile.setdefault(round(x,6),set()).add(round(y,6))
profile=sorted((x, min(ys), max(ys)) for x,ys in profile.items() if len(ys)==2)
assert len(profile)==61
assert sum(y0<-.05 and (i==0 or profile[i-1][1]>=-.05) for i,(_,y0,_) in enumerate(profile))==12
# The donor has extra coplanar joins between corrugations. Drop only
# points measured within 20 microns of both interpolated faces.
raw_profile=profile
profile=[raw_profile[0]]
for i,b in enumerate(raw_profile[1:-1],1):
    a=profile[-1]
    c=raw_profile[i+1]
    u=(b[0]-a[0])/(c[0]-a[0])
    if max(abs(b[j]-(a[j]+u*(c[j]-a[j]))) for j in (1,2))>.000020:
        profile.append(b)
profile.append(raw_profile[-1])
error=0
for x,y0,y1 in raw_profile:
    a,b=next((a,b) for a,b in zip(profile,profile[1:]) if a[0]<=x<=b[0])
    f=(x-a[0])/(b[0]-a[0])
    error=max(error,abs(y0-(a[1]+f*(b[1]-a[1]))),abs(y1-(a[2]+f*(b[2]-a[2]))))
assert error<=.000020

def srgb(v):
    return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4

orange=tuple(map(srgb,(.719,.289,.086)))
frame=tuple(map(srgb,(.236,.274,.303)))
dark=(.047,.058,.069)
edge=(.275,.333,.367)
V=[];F=[];C=[]
def append(verts,faces,colors):
    a=len(V)
    V.extend(verts)
    for face,c in zip(faces,colors):
        F.append(tuple(a+j for j in face))
        C.append(c)
def tint(c,f):
    return tuple(min(1,v*f) for v in c)
# Keep both faces and physical edges; use the extracted front/back fold stations.
n=len(profile)
for j in (1,2):
    for z in (.47,2.52):
        V.extend((x,ys[j-1],z) for x,*ys in profile)
for i in range(n-1):
    hue=1.+.09*math.sin(i*1.113)+.031*math.sin(i*.49)
    for face,shade in [
        ((i,i+1,i+1+n,i+n),1.0),
        ((i+3*n,i+1+3*n,i+1+2*n,i+2*n),.93),
        ((i+2*n,i+1+2*n,i+1,i),.8),
        ((i+n,i+1+n,i+1+3*n,i+3*n),1.08),
    ]:
        F.append(face);C.append(tint(orange,hue*shade))
F.extend([(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)])
C.extend([orange,orange])

def block(center,size,color,angle=0):
    # Single, deliberate edge bevel; no high-order perimeter segments or texture.
    W,H,D=[x*.5 for x in size]
    r=min(.012,W*.28,H*.28)
    xy=[(-W+r,-H),(W-r,-H),(W,-H+r),(W,H-r),(W-r,H),(-W+r,H),(-W,H-r),(-W,-H+r)]
    trans=Matrix.Translation(center) @ Matrix.Rotation(angle,4,'Y')
    v=[tuple(trans@Vector((x,y,z))) for y in (-D,D) for x,z in xy]
    faces=[tuple(range(8)),tuple(reversed(range(8,16)))]
    faces.extend((i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8))
    append(v,faces,[tint(color,1.02),tint(color,.90)]+[tint(color,1.14 if i in (2,3,4) else .94) for i in range(8)])

def bounds_box(lo,hi,c):
    block([(a+b)*.5 for a,b in zip(lo,hi)],(hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]),c)

for side in (-1,1):
    x=side*1.05
    block((x,.044,1.339),(.173,2.59,.230),frame)
    block((x,.049,2.635),(.148,.073,.146),tint(frame,1.17))
    block((x,.040,.055),(.275,.110,.395),dark)
    block((side*.991,-.133,2.515),(.251,.171,.026),tint(orange,1.13),side*.29)
# Front/rear plates, cap, three cross members, a lip and two rear chevron diagonals.
bounds_box((-1.105,-.0915,2.5065),(1.105,.1555,2.6415),tint(frame,1.29))
bounds_box((-.92,-.113,2.5005),(.92,-.079,2.5595),orange)
bounds_box((-.97,-.107,.0535),(.97,-.013,.5065),frame)
bounds_box((-.97,.031,.0535),(.97,.121,.5065),frame)
bounds_box((-.972,-.135,.089),(.972,-.091,.161),dark)
for z in (.596,1.355,2.385):
    block((0,.103,z),(1.90,.104,.093),frame)
# The donor apex is on its +X side (seen on the left when viewed from the rear).
apex_x=.90
rear_steel=[orig.matrix_world@orig.data.vertices[i].co for p in orig.data.polygons
            if p.material_index==1 for i in p.vertices]
rear_end_levels=[[v.z for v in rear_steel if sign*v.x>.79 and v.y>.195] for sign in (-1,1)]
assert all(1.30<z<1.41 for z in rear_end_levels[1])
assert min(rear_end_levels[0])<.66 and max(rear_end_levels[0])>2.30
for a,b in [((apex_x,.150,1.355),(-apex_x,.150,.620)),
            ((apex_x,.150,1.355),(-apex_x,.150,2.357))]:
    delta=Vector(b)-Vector(a)
    block((Vector(a)+Vector(b))/2,(delta.length,.083,.104),tint(frame,1.10),-math.atan2(delta.z,delta.x))

def bolt(x,y,z,r):
    n=6
    ny=y+.014 if y<0 else y-.014
    v=[(x+r*math.cos(math.tau*j/n),dy,z+r*math.sin(math.tau*j/n))
       for dy in (y,ny) for j in range(n)]
    f=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
    f.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    append(v,f,[tint(edge,.72)]*len(f))
for side in (-1,1):
    for x,z in ((.933,2.567),(1.052,2.511)):
        bolt(side*x,-.167,z,.026)
    for z in (.194,1.22,1.989):
        bolt(side*1.05,-.084,z,.019)
    bolt(side*.90,.199,1.355,.020)

mesh=bpy.data.meshes.new('Shared distance bay')
mesh.from_pydata(V,[],F)
mesh.update()
o=bpy.data.objects.new('WSC-MODULE-020 | Distance',mesh)
S.collection.objects.link(o)
mat=bpy.data.materials.new('Enamel and rolled frame | distance color')
mat.use_nodes=True
mat.use_backface_culling=False
q=mat.node_tree.nodes.get('Principled BSDF')
q.inputs['Roughness'].default_value=.57
q.inputs['Metallic'].default_value=.26
color=mesh.color_attributes.new(name='Finish',type='BYTE_COLOR',domain='CORNER')
mesh.color_attributes.active_color=color
vc=mat.node_tree.nodes.new('ShaderNodeVertexColor')
vc.layer_name='Finish'
mat.node_tree.links.new(vc.outputs['Color'],q.inputs['Base Color'])
mesh.materials.append(mat)
for p,c in zip(mesh.polygons,C):
    for i in p.loop_indices:
        # Lower-lip weathering keeps the large-scale texture cue without a texture lookup.
        z=V[mesh.loops[i].vertex_index][2]
        tm=.91 if z<.51 else 1.
        color.data[i].color=(*tint(c,tm),1)
bpy.ops.object.select_all(action='DESELECT')
o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
f=OUT/'wsc-module-020-corrugated-wall-distance.glb'
export([o],f)
bpy.data.objects.remove(o,do_unlink=True)
far_node,far_nodes=load(f)
far=info(f,far_node)
assert far['material_primitives']==1 and far['embedded_images']==0
assert far['bytes']<90000 and far['triangles']<1200,far
for a,b in zip(near['blender_bounds_m'],far['blender_bounds_m']):
    assert math.dist(a,b)<.00001,(a,b)
assert (far_node.matrix_world.translation-Vector((0,0,0))).length<1e-7
far_points={tuple(round(t,6) for t in (far_node.matrix_world@v.co)) for v in far_node.data.vertices}
assert all((x,y,z) in far_points for x,y0,y1 in profile for y in (y0,y1) for z in (.47,2.52))
# Both point sets have physical shoe geometry at the outer bounding planes.
pitch=2.375
for ob in (orig,far_node):
    pts=[ob.matrix_world@v.co for v in ob.data.vertices]
    for side in (-1,1):
        assert any(abs(side*p.x-pitch/2)<.00001 and 0<=p.z<=.1101 for p in pts)
    assert max(abs(p.x) for p in pts if 1.2<p.z<2.4)<=1.13651
manifest={'id':'WSC-MODULE-020','scope':'Static art distance variant, not native LOD, collision, placement or performance.',
          'original':near,'distance':far,'max_fold_station_spacing_m':round(max(b[0]-a[0] for a,b in zip(profile,profile[1:])),6),
          'max_horizontal_profile_depth_error_m':round(error,9),
          'folds':12,'fold_cross_section_blender_x_y_front_back':profile,
          'rear_chevron_apex_blender_x_m':apex_x,
          'studio_bays':5,'studio_pitch_m':pitch,'shoe_x_envelope_gap_m':0.0,
          'upright_x_envelope_gap_m':round(pitch-2*1.1365,4),
          'seam_note':'Shoes meet without overlap. Upright seam is an intentional ~102 mm gap; no solid wall or collision inferred.',
          'ground_and_origin':'Original, zero at steel shoes, Blender front -Y / glTF front +Z.'}
(OUT/'wsc-module-020-wall-distance-report.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('WALL_RESULT',near,far)
if os.environ.get('WSC_METADATA_ONLY')=='1':
    sys.exit(0)

# Reimported five-bay comparisons. Only mesh visibility changes between each pair.
groups=[]
for proto in (orig,far_node):
    group=[]
    for i in range(-2,3):
        k=bpy.data.objects.new(f'{proto.name} | studio bay {i+3}',proto.data)
        S.collection.objects.link(k)
        k.matrix_world=Matrix.Translation((pitch*i,0,0))@proto.matrix_world
        group.append(k)
    groups.append(group)
for obj in original_nodes|far_nodes:
    bpy.data.objects.remove(obj,do_unlink=True)
floor=bpy.data.materials.new('Concrete proof floor')
floor.use_nodes=True
q=floor.node_tree.nodes.get('Principled BSDF')
q.inputs['Base Color'].default_value=(.066,.085,.094,1)
q.inputs['Roughness'].default_value=.76
bpy.ops.mesh.primitive_plane_add(size=240,location=(0,0,-.005))
bpy.context.object.data.materials.append(floor)
S.world=bpy.data.worlds.new('Neutral industrial daylight')
S.world.use_nodes=True
bg=S.world.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.33,.46,.60,1)
bg.inputs[1].default_value=.52
def aim(o,target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for pos,power,width,col in [((-6,-4,6),1950,7,(1,.84,.66)),((6,5,5.7),1580,6,(.72,.86,1)),((6,-3,3),650,5,(.86,.93,1))]:
    bpy.ops.object.light_add(type='AREA',location=pos)
    k=bpy.context.object;k.data.energy=power;k.data.size=width;k.data.color=col
    aim(k,(0,0,1.35))
S.render.engine='CYCLES'
S.cycles.samples=34
S.cycles.use_denoising=False
S.cycles.use_adaptive_sampling=True
S.cycles.adaptive_threshold=.071
S.render.resolution_x=1460;S.render.resolution_y=980;S.render.resolution_percentage=100
S.render.image_settings.file_format='JPEG'
S.render.image_settings.quality=90
bpy.ops.object.camera_add()
cam=bpy.context.object
S.camera=cam
cam.data.lens=38
for side,xyz,target in [('front',(-8.05,-10.8,3.15),(-.53,0,1.27)),('rear',(8.05,10.8,3.15),(.53,0,1.27))]:
    cam.location=xyz
    aim(cam,target)
    for k,name in enumerate(('original','distance')):
        for j,group in enumerate(groups):
            for ob in group: ob.hide_render=k!=j
        only=os.environ.get('WSC_WALL_VIEW')
        if only and only!=f'{side}-{name}':
            continue
        S.render.filepath=str(OUT/f'nov23-orange-wall-{side}-{name}.jpg')
        bpy.ops.render.render(write_still=True)

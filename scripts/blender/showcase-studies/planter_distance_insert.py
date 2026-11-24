"""WSC-PROP-014 replaceable far foliage; retain the exact masonry and loam."""
import hashlib,json,math,struct,sys
from pathlib import Path

import bpy
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE))
from common import clear_scene,export,output_directory
clear_scene();out=output_directory();s=bpy.context.scene
donor=ROOT/'public/assets/wildshard-art/wsc-prop-014-planter-bed.glb'
pin='ac39cc51273c0d25c3b5c4cb957b4c71e4d427992b9d219152f89195332da7d7'
assert hashlib.sha256(donor.read_bytes()).hexdigest()==pin
bpy.ops.import_scene.gltf(filepath=str(donor))
bpy.context.view_layer.update()
orig=[x for x in s.objects if x.type=='MESH']
ratios={'resilient stems':.48,'serrated-look':.74,'tickseed blossoms':1.0,'flower discs':.38}
foliage=[o for o in orig if any(k in o.name for k in ratios)]
base=[o for o in orig if o not in foliage]
assert len(foliage)==4 and len(base)==2


def triangles(items):
    total=0
    for o in items:
        o.data.calc_loop_triangles()
        total+=len(o.data.loop_triangles)
    return total


near_triangles=triangles(foliage)
reduced=[]
for o in foliage:
    data=o.data.copy()
    new=bpy.data.objects.new('Far insert | '+o.name.split(' • ')[-1],data)
    s.collection.objects.link(new);new.matrix_world=o.matrix_world.copy()
    bpy.ops.object.select_all(action='DESELECT')
    new.select_set(True);bpy.context.view_layer.objects.active=new
    # Collapse within the donor geometry; retain colors from the original export.
    mod=new.modifiers.new('Far surface reduction','DECIMATE')
    mod.ratio=next(v for k,v in ratios.items() if k in o.name)
    mod.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    reduced.append(new)
far_triangles=triangles(reduced)
assert near_triangles==2932 and 1000<far_triangles<near_triangles*.70
path=out/'wsc-prop-014-far-planting.glb'
export(reduced,path)
raw=path.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert not any(k in d for k in ('images','animations','skins'))
for o in reduced:bpy.data.objects.remove(o,do_unlink=True)
prior=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(path))
reduced=[o for o in set(s.objects)-prior if o.type=='MESH']
assert len(reduced)==4 and triangles(reduced)==far_triangles
assert len(raw)<210000,len(raw)


def bounds(items):
    vs=[o.matrix_world@v.co for o in items for v in o.data.vertices]
    return [[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]


near_bounds,far_bounds=map(bounds,(foliage,reduced))
max_axis_change=max(abs(a-b) for p,q in zip(near_bounds,far_bounds) for a,b in zip(p,q))
assert max_axis_change<.16,max_axis_change
# Camera and geometry checks compare the exact original planting with
# the final reimport over the same, unchanged rectangular masonry donor.
world=bpy.data.worlds.new('Plaza neutral daylight')
world.use_nodes=True;q=world.node_tree.nodes['Background']
q.inputs['Color'].default_value=(.38,.48,.62,1);q.inputs['Strength'].default_value=.36
s.world=world
bpy.ops.mesh.primitive_plane_add(size=140,location=(0,0,-.095))
m=bpy.data.materials.new('Muted plaza ground')
m.diffuse_color=(.28,.24,.176,1);bpy.context.object.data.materials.append(m)
for n,kind,p,target,energy,size,col in [
 ('Warm key','SUN',(-4,-7,9),(0,0,.5),2.25,.12,(1,.84,.69)),
 ('Cool sky patch','AREA',(4,-3,5),(0,0,.7),650,7,(.65,.81,1))]:
    d=bpy.data.lights.new(n,kind);d.energy,d.color=energy,col
    if kind=='SUN':d.angle=size
    else:d.size=size
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);o.location=p
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Fixed original and reduced comparison',bpy.data.cameras.new('Fixed original and reduced comparison'))
s.collection.objects.link(cam);s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=50;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.055
s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG'
s.render.image_settings.quality=91;s.render.use_compositing=False;s.view_settings.view_transform='AgX'


def camera(p,target,deg,dims):
    cam.location=p;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=36
    cam.data.lens=36/(2*math.tan(math.radians(deg)/2))
    s.render.resolution_x,s.render.resolution_y=dims
    bpy.context.view_layer.update()


def save(n,far):
    for o in foliage:o.hide_render=far
    for o in reduced:o.hide_render=not far
    s.render.filepath=str(out/(n+'.jpg'));bpy.ops.render.render(write_still=True)


def silhouette(items,width=402,height=874):
    # Rasterize the projected triangle union only, not screen/background
    # color. The same player-eye camera is active for both variants.
    mask=set()
    for o in items:
        o.data.calc_loop_triangles()
        pts=[world_to_camera_view(s,cam,o.matrix_world@v.co) for v in o.data.vertices]
        pts=[(v.x*width,v.y*height) for v in pts]
        for tri in o.data.loop_triangles:
            (x0,y0),(x1,y1),(x2,y2)=[pts[k] for k in tri.vertices]
            def side(a,b,x,y):return (b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0])
            A,B,C=(x0,y0),(x1,y1),(x2,y2)
            for x in range(max(0,math.floor(min(x0,x1,x2))),min(width,math.ceil(max(x0,x1,x2)))):
                for y in range(max(0,math.floor(min(y0,y1,y2))),min(height,math.ceil(max(y0,y1,y2)))):
                    vals=(side(A,B,x+.5,y+.5),side(B,C,x+.5,y+.5),side(C,A,x+.5,y+.5))
                    if all(v>=0 for v in vals) or all(v<=0 for v in vals):mask.add((x,y))
    return mask


camera((0,-24,1.7),(0,0,.75),55,(804,1748))
a,b=map(silhouette,(foliage,reduced))
overlap=len(a&b)/len(a|b)
assert overlap>.82,(len(a),len(b),overlap)
save('planter-original-24m',False)
save('planter-reduced-24m',True)
camera((2.9,-5.3,3.25),(0,0,.51),42,(1150,875))
save('planter-insert-detail',True)
report={'scope':'Distance foliage-only art variant. No engine LOD, placement, draw-call or frame rate claim.',
        'donor_sha256':pin,'donor_id':'WSC-PROP-014','masonry_and_loam_unchanged':True,
        'asset':{'bytes':len(raw),'triangles':far_triangles,'sha256':hashlib.sha256(raw).hexdigest()},
        'original_planting_triangles':near_triangles,'max_bounds_component_difference_m':round(max_axis_change,6),
        'distance_m':24,'eye_m':1.7,'vertical_fov_deg':55,'reference_pixels':[402,874],
        'union_overlap':round(overlap,5),'original_covered_pixels':len(a),'reduced_covered_pixels':len(b),
        'reimport_nodes':len(reduced)}
(out/'planter-distance.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))

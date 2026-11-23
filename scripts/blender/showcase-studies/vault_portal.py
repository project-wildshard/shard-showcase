"""Rebuild the WSC-ARCH-007 open Training Vault frame and optional reimport view."""
import math, os, sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import clear_scene, output_directory

OUT = output_directory()
ROOT = HERE.parents[2] / 'public/assets/wildshard-art'
NAME = 'wsc-arch-007-training-vault-portal'
clear_scene()

def finish(name, srgb, rough=.65, metal=0, emission=0):
    def l(s):
        return s / 12.92 if s <= .04045 else ((s + .055) / 1.055) ** 2.4
    color=tuple(l((srgb>>n&255)/255) for n in (16,8,0))+(1,)
    m=bpy.data.materials.new(name); m.diffuse_color=color; m.use_nodes=True
    q=m.node_tree.nodes.get('Principled BSDF')
    for k,v in [('Base Color',color),('Roughness',rough),('Metallic',metal),('Emission Color',color),('Emission Strength',emission)]:
        q.inputs[k].default_value=v
    return m

brick=[finish('Fired terracotta '+str(i), c,.88) for i,c in enumerate((0xa9512c,0xb35d32,0xbf6c38,0x914526))]
mortar=finish('Deep clay joints',0x67392a,.92)
iron=finish('Oxide charcoal frame',0x303d45,.49,.69)
steel=finish('Brushed gunmetal flange',0x81919a,.43,.46)
zinc=finish('Polished bolt seats',0x9bafa9,.32,.78)
brass=finish('Brass wake markers',0xe4a64a,.39,.67)
cyan=finish('Passive turquoise lens',0x48a9a7,.41,.30,.12)

def mesh(n, vs, fs, mat):
    d=bpy.data.meshes.new(n); d.from_pydata(vs,[],fs); d.update()
    o=bpy.data.objects.new(n,d); bpy.context.collection.objects.link(o); d.materials.append(mat)
    assert all(f.area>1e-6 for f in d.polygons)
    return o

def box(n, p, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object; o.name=n; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=o.modifiers.new('Machined edges','BEVEL'); b.width=bevel; b.segments=1
        bpy.ops.object.modifier_apply(modifier=b.name)
    o.data.materials.append(mat)
    return o

def cylinder(n,x,y,z,rad,depth,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=rad,depth=depth,location=(x,y,z),rotation=(math.pi/2,0,0))
    o=bpy.context.object; o.name=n; o.data.materials.append(mat); return o

CZ = 1.77
START = math.radians(-44)
ARC = math.pi-2*START
def polar(a,r): return r*math.cos(a), CZ+r*math.sin(a)

def band(n,r0,r1,y0,y1,start,stop,nseg,mat):
    # An open lower sector becomes vertical jambs, so the art opening reaches the floor.
    vs=[]
    for i in range(nseg+1):
        a=start+(stop-start)*i/nseg
        for rad,y in ((r0,y0),(r1,y0),(r1,y1),(r0,y1)):
            x,z=polar(a,rad); vs.append((x,y,z))
    fs=[]
    for i in range(nseg):
        for j in range(4):
            k=(j+1)%4
            fs.append((4*i+j,4*i+k,4*(i+1)+k,4*(i+1)+j))
    fs.extend([(3,2,1,0),tuple(range(4*nseg,4*nseg+4))])
    o=mesh(n,vs,fs,mat)
    # Normal sign does not depend on arc direction or flat cap winding.
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    return o

def join(n,arr):
    bpy.ops.object.select_all(action='DESELECT')
    for o in arr:o.select_set(True)
    bpy.context.view_layer.objects.active=arr[0]; bpy.ops.object.join()
    o=bpy.context.object; o.name=n; bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    return o

mas=[band('Mortar core',1.91,2.35,-.32,.32,START,START+ARC,30,mortar)]
for i in range(14):
    a=START+ARC*i/14
    mas.append(band('Crown voussoir',2.03,2.36,-.37,.37,a+.008,a+ARC/14-.008,3,brick[i%4]))
for side in (-1,1):
    for i in range(7):
        mas.append(box('Laid pier course',(side*1.89,0,.235+i*.353),(.81-(i%2)*.05,.69,.331),brick[i%4],.025))
    mas.append(box('Spring block',(side*1.89,0,2.73),(.89,.79,.18),brick[2],.021))

frame=[band('Continuous throat',1.66,2.13,-.43,.43,START,START+ARC,30,iron)]
for side in (-1,1):
    for d in (-1,1):
        y=d*.477
        for j in range(10):
            a=START+ARC*j/10
            frame.append(band('Flanged armor quadrant',1.775,2.15,y-.052,y+.052,a+.009,a+ARC/10-.009,3,steel))
        frame.append(box('Rail cheek',(side*1.45,y,.35),(.52,.14,.70),steel,.045))
        frame.append(box('Corner clamp',(side*2.26,y,2.52),(.30,.19,.35),iron,.024))
    frame.append(box('Anchor boot',(side*1.85,0,.117),(1.08,1.10,.234),iron,.048))
    frame.append(box('Jamb throat',(side*1.40,0,.325),(.42,.88,.65),iron,.034))
    frame.append(box('Jamb wear strip',(side*1.188,0,.335),(.048,.82,.61),zinc,.012))
# Wide opening without a high sill or a blocked effect face.
frame.append(box('Flush floor rebate',(0,0,.026),(2.37,1.13,.052),iron,.012))
frame.append(box('Upper retention rail',(0,0,3.75),(4.11,.79,.18),iron,.025))
acc=[]
for side in (-1,1):
    y=side*.546
    acc.append(band('Inactive turquoise channel',1.698,1.73,y-.018,y+.018,START+.012,START+ARC-.012,30,cyan))
    acc.append(box('Keycard escutcheon',(0,y,3.835),(.59,.16,.59),iron,.057))
    acc.append(cylinder('Keyhole circle',0,y+side*.086,3.913,.105,.025,cyan))
    acc.append(box('Keyhole stem',(0,y+side*.086,3.76),(.089,.023,.209),cyan,.012))
    for j in range(10):
        a=START+ARC*(j+.5)/10
        x,z=polar(a,1.96)
        acc.append(cylinder('Brass marker',x,y+side*.027,z,.076,.036,brass))
for o in [join('Masonry_Shell',mas),join('Open_Portal_Frame',frame),join('Lens_And_Keycard_Detail',acc)]:
    assert o.location.length<1e-6
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(OUT/(NAME+'.glb')),export_format='GLB',use_selection=True,export_texcoords=False,export_animations=False)

if os.getenv('WSC_VAULT_RENDER')=='1':
    clear_scene()
    def insert(filepath, x, y, z, width, axis=0):
        before=set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(filepath))
        bpy.context.view_layer.update()
        children=set(bpy.context.scene.objects)-before
        verts=[o.matrix_world @ Vector(v) for o in children if o.type=='MESH' for v in o.bound_box]
        lo=[min(p[i] for p in verts) for i in range(3)]
        hi=[max(p[i] for p in verts) for i in range(3)]
        scale=width/(hi[axis]-lo[axis]) if width else 1
        center=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]))
        for o in children:
            if o.parent is None:
                o.location=(o.location-center)*scale+Vector((x,y,z));o.scale*=scale
        return (hi[2]-lo[2])*scale
    h=insert(ROOT/'wsc-prop-060-east-stair-kit.glb',-.8,-.72,0,2.31)*.72
    insert(OUT/(NAME+'.glb'),-.8,1.1,h,0)
    insert(ROOT/'wsc-module-021-open-circular-vault-door.glb',4.72,2.12,0,3.05)
    insert(ROOT/'wsc-prop-062-vault-information-sign.glb',-4.10,-.55,0,1.55)
    insert(ROOT/'wsc-prop-061-keyhole-banner.glb',2.58,1.68,.87,.69)
    ground=finish('Studio slate',0x3d4b54,.84)
    box('Studio floor',(0,0,-.125),(200,200,.25),ground)
    box('Entry landing',(-.8,1.25,h/2),(5.0,1.87,h),steel,.045)
    box('Banner stand',(2.58,1.86,.96),(.055,.055,1.92),iron,.012)
    s=bpy.context.scene; s.world.color=(.31,.31,.31)
    def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
    for n,p,power,size,c in [('Daylight',(-5,-7,12),2500,7,(1,.87,.73)),('Cool fill',(8,-3,8),1250,6,(.71,.84,1)),('Rim',(0,7,10),2050,5,(1,.78,.59))]:
        bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object
        o.name=n;o.data.energy=power;o.data.size=size;o.data.color=c;aim(o,(0,1,1.6))
    bpy.ops.object.camera_add(location=(4.2,-14.7,5.6))
    s.camera=bpy.context.object;aim(s.camera,(.2,1.0,2.14));s.camera.data.type='ORTHO';s.camera.data.ortho_scale=13.6
    s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=False
    s.render.resolution_x=1380;s.render.resolution_y=900;s.render.resolution_percentage=100
    s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=90
    s.render.filepath=str(OUT/'east-vault-portal-reimport.jpg')
    bpy.ops.render.render(write_still=True)

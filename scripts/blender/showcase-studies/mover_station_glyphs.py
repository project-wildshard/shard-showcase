"""W09 wayfinding study: five relief meshes for the unchanged station sign."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

assets=Path(__file__).resolve().parents[3]/'public/assets/wildshard-art'
donor=assets/'wsc-prop-038-mover-station-number-sign.glb'
assert hashlib.sha256(donor.read_bytes()).hexdigest()=='9b09b4db9e5d2c5903abb552d02635b22f99e68859de407f634c4000d0681dc8'
out=output_directory()
pack=out/'wsc-prop-038-mover-station-glyphs.glb'
s=bpy.context.scene
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(donor))
bpy.context.view_layer.update()
base=[o for o in s.objects if o.type=='MESH' and o.name!='numeral']
exact=s.objects['numeral']
assert len(base)==6
names=('Conveyors','Jump Pads','Sliding Platforms','Spinner','Lift','Top Deck')

def flash(text):
    cv=bpy.data.curves.new('Raised '+text,'FONT')
    cv.body=text
    cv.size=1
    cv.resolution_u=5
    cv.fill_mode='BOTH'
    cv.extrude=.024
    cv.bevel_depth=.008
    cv.bevel_resolution=0
    o=bpy.data.objects.new('Glyph '+text,cv)
    s.collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    pts=[v.co.copy() for v in o.data.vertices]
    a,b=([fn(p[i] for p in pts) for i in range(3)] for fn in (min,max))
    scale=.293/(b[1]-a[1])
    center=(a[0]+b[0])*.5
    for v,p in zip(o.data.vertices,pts):
        v.co=((p.x-center)*scale, -.048-.010*(p.z-a[2])/(b[2]-a[2]), .502+scale*(p.y-a[1]))
    o.data.materials.clear()
    o.data.materials.append(exact.data.materials[0])
    o.data.update()
    assert not o.data.validate(clean_customdata=False)
    return o

# W09 has a flagged, footed one. The bare Bfont "1" is too close to
# a letter I at distance. Use a small custom footprint, 144 mm wide.
def flagged_one():
    xy=[(-.072,0),(.072,0),(.072,.041),(.026,.041),(.026,.293),
        (-.015,.293),(-.069,.252),(-.069,.207),(-.020,.236),(-.020,.041),(-.072,.041)]
    count=len(xy)
    verts=[(x,depth,.502+h) for depth in (-.058,-.048) for x,h in xy]
    faces=[tuple(range(count)),tuple(reversed(range(count,2*count)))]
    faces.extend((j,i,i+count,j+count) for i in range(count) for j in [(i+1)%count])
    m=bpy.data.meshes.new('Flagged one relief')
    m.from_pydata(verts,[],faces)
    m.materials.append(exact.data.materials[0])
    m.update()
    assert not m.validate()
    o=bpy.data.objects.new('Glyph 1',m)
    s.collection.objects.link(o)
    return o

replacements=[flagged_one()]+[flash(str(n)) for n in (3,4,5,6)]
export(replacements,pack)
for o in replacements:
    bpy.data.objects.remove(o,do_unlink=True)
before=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(pack))
bpy.context.view_layer.update()
glyphs={int(o.name[-1]):o for o in set(s.objects)-before if o.type=='MESH'}
assert set(glyphs)=={1,3,4,5,6}
glyphs[2]=exact
stats={}
for n,o in sorted(glyphs.items()):
    vv=[o.matrix_world@v.co for v in o.data.vertices]
    radius=max(math.hypot(v.x,v.z-.647) for v in vv)
    zs=[-v.y for v in vv]
    height=max(v.z for v in vv)-min(v.z for v in vv)
    assert radius < .206 and abs(height-.293)<.0001
    assert abs(min(zs)-.048)<1e-5 and abs(max(zs)-.058)<1e-5
    stats[n]={'name':names[n-1], 'rim_clearance_mm':round((.245-radius)*1000,2)}
raw=pack.read_bytes()
d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
assert len(d['nodes'])==len(d['meshes'])==5 and not any(d.get(k) for k in ('images','skins','animations'))
tris=sum(d['accessors'][p['indices']]['count']//3 for m in d['meshes'] for p in m['primitives'])
assert len(raw) < 100_000 and tris<2800
(out/'validation.json').write_text(json.dumps({'bytes':len(raw),'triangles':tris,'variants':stats,'native_placement':False},indent=2)+'\n')

for o in [*base,*glyphs.values()]:
    o.hide_render=True

def assemble(n,x,y,yaw=0):
    t=Matrix.Translation((x,y,0)) @ Matrix.Rotation(math.radians(yaw),4,'Z')
    created=[]
    for src in [*base,glyphs[n]]:
        o=bpy.data.objects.new(f'{n} {src.name}',src.data)
        s.collection.objects.link(o)
        o.matrix_world=t@src.matrix_world
        created.append(o)
    return created

def matte(n,c):
    m=bpy.data.materials.new(n)
    m.use_nodes=True
    sh=m.node_tree.nodes.get('Principled BSDF')
    sh.inputs['Base Color'].default_value=(*c,1)
    sh.inputs['Roughness'].default_value=.78
    return m

slate=matte('W09 green-gray stage',(.057,.087,.086))
ink=matte('Pale route legends',(.69,.75,.64))
aqua=matte('Faded painted course stripe',(.053,.22,.22))
amber=matte('Amber lane dash',(.61,.24,.05))
def slab(name,p,d,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object
    o.name=name
    o.dimensions=d
    o.data.materials.append(m)
    return o

def legend(name,x,caption):
    cv=bpy.data.curves.new(name,'FONT')
    cv.body=caption
    cv.size=.061
    cv.align_x='CENTER'
    cv.materials.append(ink)
    o=bpy.data.objects.new(name,cv)
    s.collection.objects.link(o)
    o.location=(x,-.295,.003)
    return o

def aim(o,q):
    o.rotation_euler=(Vector(q)-o.location).to_track_quat('-Z','Y').to_euler()

def lamp(n,p,q,power,c,sz):
    l=bpy.data.lights.new(n,'AREA')
    l.energy=power
    l.color=c
    l.shape='DISK'
    l.size=sz
    o=bpy.data.objects.new(n,l)
    s.collection.objects.link(o)
    o.location=p
    aim(o,q)

slab('continuous studio floor',(0,0,-.08),(100,100,.16),slate)
s.world=bpy.data.worlds.new('Cool daylight')
s.world.color=(.23,.26,.28)
lamp('Sunkissed key',(-2.6,-4.6,5),(0,0,.4),950,(1,.81,.61),6)
lamp('Cool fill',(1.6,-.8,4),(0,0,.4),680,(.57,.77,1),5)
lamp('Bronze rim',(-1,4,5),(0,0,.4),970,(1,.88,.64),4.2)
c=bpy.data.cameras.new('Course art camera')
s.camera=bpy.data.objects.new(c.name,c)
s.collection.objects.link(s.camera)
s.render.engine='CYCLES'
s.cycles.samples=48
s.cycles.use_denoising=False
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG'
s.render.image_settings.quality=91

def render(key,p,q,wh,ortho=None):
    s.camera.location=p
    aim(s.camera,q)
    c.type='ORTHO' if ortho else 'PERSP'
    c.clip_end=100
    if ortho: c.ortho_scale=ortho
    else: c.lens=38
    s.render.resolution_x,s.render.resolution_y=wh
    s.render.filepath=str(out/(key+'.jpg'))
    bpy.ops.render.render(write_still=True)

line=[]
for n in range(1,7):
    x=(n-3.5)*.89
    line+=assemble(n,x,0,0)
    line+=[legend(names[n-1],x,names[n-1].upper())]
line+=[slab('painted baseline',(0,-.43,.003),(5.16,.014,.004),aqua)]
render('nov23-mover-glyph-plate',(0,-7,2.55),(0,0,.37),(1640,650),5.47)
for o in line:
    bpy.data.objects.remove(o,do_unlink=True)
for n,x,y,yaw in ((1,-1.95,.05,5),(2,-.96,.22,3),(3,.10,.48,0),(4,1.17,.63,-3),(5,2.23,.92,-6),(6,3.26,1.12,-10)):
    assemble(n,x,y,yaw)
for x in (-2.45,2.58):
    slab('cyan paint margin',(x,1.39,.003),(.042,5,.004),aqua)
for j in range(9):
    slab('dashed approach mark',(-.72+j*.44,-.62+j*.30,.004),(.26,.032,.006),amber)
render('nov23-mover-glyph-approach',(-1.95,-6.32,2.61),(.65,.35,.44),(1400,790))

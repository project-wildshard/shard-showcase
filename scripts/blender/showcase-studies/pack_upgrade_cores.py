"""Three original W2a PACK component models and nine-way 48 px legibility proof."""
import itertools
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

root = Path(__file__).resolve().parents[3]
out = output_directory()
clear_scene()
s = bpy.context.scene

def srgb(rgb):
    channels = [(rgb >> n & 255) / 255 for n in (16, 8, 0)]
    return tuple(x / 12.92 if x < .04045 else ((x + .055) / 1.055) ** 2.4 for x in channels)

def material(name, rgb, rough=.4, metal=.5, em=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    color = (*srgb(rgb), 1)
    m.diffuse_color = color
    p = m.node_tree.nodes['Principled BSDF']
    for k, v in [('Base Color', color), ('Roughness', rough), ('Metallic', metal),
                 ('Emission Color', color), ('Emission Strength', em)]:
        p.inputs[k].default_value = v
    return m

iron = material('Blackened cast iron', 0x303543, .53)
steel = material('Machined steel', 0xaebdbe, .28, .76)
gold = material('Industrial bronze', 0xcc9559, .33, .63)
red = material('Big Pallet claret enamel', 0xaa362c, .39, .24)
blue = material('Vault Warden cold enamel', 0x397a98, .38, .29)
cream = material('Foreman kiln ceramic', 0xe3d0a1, .36, .10)
amber = material('Live amber glass', 0xff982a, .25, .13, .8)
cyan = material('Cool diagnostic glass', 0x41b8d0, .26, .20, .8)
rubber = material('Woven dark insulation', 0x25252c, .62, 0)

def link(name, data):
    ob = bpy.data.objects.new(name, data)
    s.collection.objects.link(ob)
    return ob

def finish(ob, ma, width):
    ob.data.materials.append(ma)
    if width:
        bpy.context.view_layer.objects.active = ob
        mod = ob.modifiers.new('Machined edge', 'BEVEL')
        mod.width, mod.segments = width, 1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob

def box(n, ma, p, d, width=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p)
    o = bpy.context.object
    o.name, o.scale = n, d
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, ma, width)

def cyl(n, ma, x, y, z, r, depth, sides=12, width=.002):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=r, depth=depth, location=(x,y,z))
    o = bpy.context.object
    o.name = n
    return finish(o, ma, width)

def profile(n, ma, xy, z, h, opening=None, width=.004):
    # CCW outer and inner loops; matching rings close both surfaces.
    k = len(xy)
    v = [(x,y,zz) for ring, zz in [(xy,z),(xy,z+h)] for x,y in ring]
    f = [(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
    if opening:
        v += [(x,y,zz) for zz in (z,z+h) for x,y in opening]
        for i in range(k):
            j = (i+1)%k
            f += [(k+i,k+j,3*k+j,3*k+i), (j,i,2*k+i,2*k+j),
                  (2*k+j,2*k+i,3*k+i,3*k+j)]
    else:
        f += [tuple(reversed(range(k))), tuple(range(k,2*k))]
    m = bpy.data.meshes.new(n)
    m.from_pydata(v, [], f)
    m.update()
    return finish(link(n,m),ma,width)

def join(n, items):
    bpy.ops.object.select_all(action='DESELECT')
    for o in items:
        o.select_set(True)
    bpy.context.view_layer.objects.active = items[0]
    bpy.ops.object.join()
    o = items[0]
    o.name = o.data.name = n
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ v.co for v in o.data.vertices]
    lo,hi = bounds(pts)
    offset = Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    o.data.transform(Matrix.Translation(-offset) @ o.matrix_world)
    o.matrix_world = Matrix.Identity(4)
    return o

def bounds(pts):
    return tuple(Vector(fn(p[i] for p in pts) for i in range(3)) for fn in (min,max))

def chamfer(n, ma, x,y,hx,hy,c,z,h,opening=None,width=.004):
    xy = [(-hx+c,-hy),(hx-c,-hy),(hx,-hy+c),(hx,hy-c),(hx-c,hy),(-hx+c,hy),(-hx,hy-c),(-hx,-hy+c)]
    return profile(n,ma,[(x+a,y+b) for a,b in xy],z,h,opening,width)

def trace(n, ma, coords, radius):
    cu = bpy.data.curves.new(n,'CURVE')
    cu.dimensions='3D'
    cu.resolution_u=1
    cu.bevel_resolution=0
    cu.bevel_depth=radius
    cu.use_fill_caps=True
    sp=cu.splines.new('POLY')
    sp.points.add(len(coords)-1)
    for p,v in zip(sp.points,coords):
        p.co=(*v,1)
    cu.materials.append(ma)
    ob = link(n,cu)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH')
    return bpy.context.object

# A forked pressure manifold, with real recess between the two pistons.
outline=[(-.078,-.173),(-.009,-.188),(.064,-.173),(.131,-.093),(.152,.020),
         (.135,.151),(.096,.182),(.057,.178),(.041,.146),(.027,.032),
         (-.027,.032),(-.041,.146),(-.057,.178),(-.096,.182),(-.135,.151),(-.152,.020),(-.131,-.093)]
heart=[profile('Forked iron sump',iron,outline,0,.054,width=.012),
       profile('Cast red manifold',red,[(x*.96,y*.94) for x,y in outline],.038,.033,width=.009),
       cyl('Pressure gauge bezel',gold,0,-.077,.074,.049,.02,20),
       cyl('Recessed pressure dial',amber,0,-.077,.086,.037,.012,20),
       box('Pressure needle',iron,(.009,-.066,.094),(.008,.052,.004),.001)]
heart[-1].rotation_euler.z=.68
for sign in (-1,1):
    x=.087*sign
    heart.extend([box('Exposed hydraulic slide',steel,(x,.108,.076),(.030,.131,.026),.006),
                  box('Hard stop',gold,(x,.150,.088),(.064,.043,.022),.006),
                  box('Compressed rubber bellow',rubber,(x,.050,.084),(.046,.045,.021),.004),
                  trace('Return line',gold,[(sign*a,b,c) for a,b,c in
                       [(.095,.03,.081),(.111,.002,.083),(.105,-.042,.087),(.073,-.104,.086),(.035,-.118,.080)]],.007),
                  cyl('Sump octagonal plug',steel,x,-.102,.066,.014,.014,8)])

# Low beveled armored cassette: a real cutout through the entire core.
hole=[(-.056,-.073),(.056,-.073),(.070,-.059),(.070,.059),(.056,.073),(-.056,.073),(-.070,.059),(-.070,-.059)]
plate=[chamfer('Keyed armor cassette',iron,0,0,.182,.119,.041,0,.034,hole),
       chamfer('Hardened chamfer',steel,0,0,.175,.112,.040,.029,.022,hole),
       chamfer('Blue anodized face',blue,0,0,.163,.100,.034,.048,.012,hole,.002)]
for sign in (-1,1):
    x=sign*.120
    plate.extend([box('Ceramic wing pad',iron,(x,0,.056),(.054,.114,.019),.009),
                  box('Check-index light',cyan,(x,-.023,.067),(.034,.008,.009),.002)])
    for y in (-.067,.067):
        plate.append(cyl('Flush shoulder screw',gold,x,y,.059,.015,.014,8))
    for y in (0,.023):
        plate.append(box('Stamped wing rib',steel,(x,y,.066),(.030,.006,.007),.001))

# Three-sided fork crown and T-shaped foot are readable without colors.
cap=[chamfer('Three-gang terminal foot',iron,0,-.154,.118,.045,.014,0,.064),
     box('Rectangular ceramic spine',cream,(0,-.019,.034),(.089,.236,.066),.011)]
for sign in (-1,1):
    x=sign*.064
    cap.extend([chamfer('Kiln insulator canister',cream,x,.019,.048,.143,.014,.007,.066),
                box('Terminal armor cover',steel,(x,.140,.054),(.083,.049,.064),.007),
                box('Raised busbar blade',gold,(x,.167,.047),(.033,.062,.043),.004),
                box('Busbar polarity strip',iron,(x,.091,.076),(.038,.016,.010),.003)])
    for y in (-.086,-.052,-.018,.016,.050):
        cap.append(box('Ceramic cooling band',gold,(x,y,.058),(.098,.013,.044),.003))
    cap.append(cyl('Arc terminal',steel,x,-.157,.070,.020,.016,8))
cap.extend([box('Amber warning well',iron,(0,-.088,.073),(.057,.101,.016),.004),
            box('Amber test strip',amber,(0,-.088,.084),(.022,.070,.008),.002)])

cores=[('Hydraulic Heart','Big Pallet','Dodge Servo',heart),
       ('Plate Core','Vault Warden chest','Parry Gyro',plate),
       ("Foreman's Capacitor",'Foreman Unit 7','Arc Insulation',cap)]
names=[x[0] for x in cores]
dims={}
objects={}
for i,(n,_,_,obs) in enumerate(cores):
    o=join(n,obs)
    lo,hi=bounds([v.co for v in o.data.vertices])
    dims[n]=[round(x,6) for x in hi-lo]
    assert abs(lo.z)<1e-6 and max(hi-lo)<.5
    o.location.x=(i-1)*.54
    objects[n]=o
target=out/'w2a-pack-upgrade-cores.glb'
export(list(objects.values()),target)
raw=target.read_bytes()
doc=json.loads(raw[20:20+int.from_bytes(raw[12:16],'little')])
tri=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])
assert len(doc['nodes'])==len(doc['meshes'])==3 and tri<6600 and len(raw)<390000,(tri,len(raw))
assert not any(doc.get(k) for k in ('images','skins','animations','extensionsRequired'))
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(target))
bpy.context.view_layer.update()
for n in names:
    ob=bpy.data.objects[n]
    lo,hi=bounds([ob.matrix_world@v.co for v in ob.data.vertices])
    assert abs(lo.z)<.00002 and max(abs(a-b) for a,b in zip(hi-lo,dims[n]))<.00002
bpy.ops.import_scene.gltf(filepath=str(root/'public/assets/wildshard-art/w2a-salvage-parts.glb'))
angles={'Servo':(40,9,-25),'Tine':(15,31,-42),'Rotor':(9,8,-8),'Nozzle':(63,-18,28),
        'Rivet plate':(17,-15,-24),'Arc coil':(14,0,-29),
        names[0]:(14,-6,46),names[1]:(15,12,-10),names[2]:(17,-12,21)}
sizes=dict(zip(angles,(.95,1.35,1.08,.95,1.06,1.08,1.14,1.10,1.23)))
obs={n:bpy.data.objects[n] for n in angles}

def aim(ob,p,q):
    ob.location=p
    ob.rotation_euler=(Vector(q)-ob.location).to_track_quat('-Z','Y').to_euler()

def pose(n,x,y,z,k=1):
    ob=obs[n]
    ax,ay,az=map(math.radians,angles[n])
    rot=Matrix.Rotation(az,4,'Z')@Matrix.Rotation(ay,4,'Y')@Matrix.Rotation(ax,4,'X')
    lo,hi=bounds([rot@v.co for v in ob.data.vertices])
    center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    ob.matrix_world=Matrix.Translation((x,y,z))@Matrix.Scale(k*sizes[n]/max(hi.x-lo.x,hi.y-lo.y),4)@Matrix.Translation(-center)@rot

camera=link('PACK lens',bpy.data.cameras.new('PACK lens'))
s.camera=camera
camera.data.type='ORTHO'
camera.data.ortho_scale=1.65
aim(camera,(0,-.25,4.8),(0,0,0))
s.render.engine='CYCLES'
s.cycles.samples=14
s.cycles.use_denoising=False
s.render.film_transparent=True
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
s.world=bpy.data.worlds.new('Workshop ambient')
s.world.color=(.20,.23,.29)
s.render.resolution_percentage=100
s.render.resolution_x=s.render.resolution_y=48
s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGBA'
masks={}
for n,ob in obs.items():
    for o in obs.values():
        o.hide_render=o!=ob
    pose(n,0,0,0)
    p=out/('mask-'+n.lower().replace("'",'').replace(' ','-')+'.png')
    s.render.filepath=str(p)
    bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(p),check_existing=False)
    masks[n]={i for i,a in enumerate(im.pixels[:][3::4]) if a>=.5}
    bpy.data.images.remove(im)
    assert 140<len(masks[n])<1450,(n,len(masks[n]))
pairs={f'{a} / {b}':round(len(masks[a]&masks[b])/len(masks[a]|masks[b]),4)
       for a,b in itertools.combinations(masks,2) if a in names or b in names}
assert max(pairs.values())<.64,pairs

def flat(name,rgb):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    nd=m.node_tree.nodes
    nd.clear()
    e=nd.new('ShaderNodeEmission')
    e.inputs[0].default_value=(*srgb(rgb),1)
    m.node_tree.links.new(e.outputs[0],nd.new('ShaderNodeOutputMaterial').inputs[0])
    return m

def title(t,x,y,sz,m,align='CENTER'):
    f=bpy.data.curves.new(t,'FONT')
    f.body,f.size,f.align_x,f.align_y=t,sz,align,'CENTER'
    f.materials.append(m)
    link(t,f).location=(x,y,.018)

def light(n,p,q,e,color,size):
    d=bpy.data.lights.new(n,'AREA')
    d.energy,d.color,d.shape,d.size=e,color,'DISK',size
    aim(link(n,d),p,q)

paper=flat('Warm caption',0xf8e7c9)
faint=flat('Brushed caption',0x90bac5)
dark=flat('PACK locked silhouette',0x161d24)
parch=flat('Light mask field',0xe4cda5)
board=material('Charcoal backcloth',0x16232a,.85,0)
slate=material('Graphite display pads',0x30414b,.70,.12)
base=box('Backdrop',board,(0,0,-.12),(30,30,.10))
light('Amber softbox',(-3,-4,5),(0,0,0),430,(1,.79,.57),5.2)
light('Cobalt edge',(3,2,4),(0,0,0),420,(.55,.78,1),4)
light('White rim',(0,3,5),(0,0,0),250,(1,.93,.83),3)
for n,o in obs.items():
    o.hide_render=n not in names
review=set(s.objects)
for i,(n,reward,use,_) in enumerate(cores):
    x=(i-1)*2.39
    pose(n,x,.21,.055,1.63)
    box('Specimen pad',slate,(x,.20,-.013),(2.27,2.20,.05),.13)
    box('Index bar',gold,(x,-1.018,.007),(.30,.027,.010),.003)
    title(n.upper(),x,-1.22,.167,paper)
    title(reward+'  /  '+use,x,-1.47,.121,faint)
title('WILDSHARD  /  THE UPGRADE CORES',-3.47,1.82,.250,paper,'LEFT')
title('W2a     PACK REWARDS     /     THREE MINI-BOSS COMPONENTS',-3.47,1.55,.115,faint,'LEFT')
s.render.film_transparent=False
s.cycles.samples=32
s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.07
s.render.image_settings.file_format='JPEG'
s.render.image_settings.color_mode='RGB'
s.render.image_settings.quality=94
s.render.resolution_x,s.render.resolution_y=1600,840
camera.data.ortho_scale=7.62
aim(camera,(0,-1.18,11),(0,.19,0))
s.render.filepath=str(out/'nov25-pack-cores-earned.jpg')
bpy.ops.render.render(write_still=True)

for o in set(s.objects)-review:
    bpy.data.objects.remove(o,do_unlink=True)
base.data.materials[0]=flat('Dark panel backdrop',0x1c2932)
for i,(n,ob) in enumerate(obs.items()):
    x=(i%3-1)*2.03
    y=1.47-i//3*1.50
    ob.hide_render=False
    pose(n,x,y+.105,.024,.90)
    ob.data.materials.clear()
    ob.data.materials.append(dark)
    box('Silhouette tile',parch,(x,y,-.018),(1.94,1.40,.04),.07)
    title(n.upper(),x,y-.51,.127,dark)
title('WILDSHARD  /  UNFOUND PACK',-2.97,2.74,.238,paper,'LEFT')
title('SIX SALVAGE PARTS + THREE CORES   /   48 PX MASKS TESTED SEPARATELY',-2.97,2.49,.100,faint,'LEFT')
s.cycles.samples=10
s.render.resolution_x,s.render.resolution_y=1400,1210
camera.data.ortho_scale=6.48
aim(camera,(0,.22,11),(0,.32,0))
s.render.filepath=str(out/'nov25-pack-cores-locked.jpg')
bpy.ops.render.render(write_still=True)
(out/'validation.json').write_text(json.dumps({
    'GLB':{'bytes':len(raw),'triangles':tri,'sizesBlenderMeters':dims,'meshes':names},
    'mask':{'thumbnailPixels':[48,48],'minimumAlpha':.5,'thresholdIou':.64,
            'maxIouNewVsAny':max(pairs.values()),'newComparisons':pairs,
            'occupancy':{n:len(m) for n,m in masks.items()}},
    'planRewards':{n:{'source':reward,'upgrade':use} for n,reward,use,_ in cores},
    'gameplayBindings':False
},indent=2)+'\n')

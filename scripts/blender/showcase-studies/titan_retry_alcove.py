"""E12g visual fit, at the original Round 5 retry fixture positions."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, export, output_directory

out=output_directory()
root=Path(__file__).resolve().parents[3]
bound=root/'public/assets/wildshard-art/wsc-scene-008-titan-bowl.glb'
pin='cd4b20016133bab16940d85f0b3319aecd19708626a5fe9cdb35f68f83a92021'
assert hashlib.sha256(bound.read_bytes()).hexdigest()==pin
clear_scene()
s=bpy.context.scene

def material(n,rgb,metal=0,rough=.55,glow=0):
    m=bpy.data.materials.new(n)
    m.use_nodes=True
    color=(*rgb,1)
    m.diffuse_color=color
    p=m.node_tree.nodes['Principled BSDF']
    for k,v in [('Base Color',color),('Metallic',metal),('Roughness',rough),
                ('Emission Color',color),('Emission Strength',glow)]:
        p.inputs[k].default_value=v
    return m

frame=material('Blue-black roller steel',(.062,.088,.111),.72,.50)
sheet=material('Brushed slate panel',(.112,.148,.167),.45,.48)
edge=material('Machined silver lip',(.38,.47,.49),.75,.34)
oxide=material('Warm oxide bronze',(.31,.119,.035),.69,.41)
base=material('Blue slate concrete',(.255,.293,.317),.09,.80)
floor=material('Stippled paving',(.181,.215,.226),.17,.74)
black=material('Electronics recess',(.021,.035,.048),.39,.63)
yellow=material('Safety enamel',(.67,.275,.037),.32,.52)
amber=material('Retry lamp amber',(.94,.43,.085),.2,.39,3.2)
blue=material('Exit ion neon',(.058,.298,.98),.19,.26,4.1)
white=material('Warm lettering',(.89,.86,.71),.16,.48,.30)
groups={}

def add(n,ma,pts,faces):
    d=bpy.data.meshes.new(n)
    d.from_pydata(pts,[],faces)
    d.update()
    if ma:d.materials.append(ma)
    o=bpy.data.objects.new(n,d)
    s.collection.objects.link(o)
    return o

def keep(g,o):
    groups.setdefault(g,[]).append(o)
    return o

def box(g,n,m,p,d,w=0,rz=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object
    o.name,o.scale=n,d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.rotation_euler.z=rz
    o.data.materials.append(m)
    if w:
        mod=o.modifiers.new('Machined corners','BEVEL')
        mod.width=w;mod.segments=1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return keep(g,o)

def bolt(g,n,m,p,r,d,nvert=8,vertical=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=nvert,radius=r,depth=d,location=p,
        rotation=(math.pi/2,0,0) if vertical else (0,0,0))
    o=bpy.context.object
    o.name=n;o.data.materials.append(m)
    return keep(g,o)

def arc(g,n,m,loc,profile,start,end,steps):
    x,y,z=loc
    verts=[]
    for j in range(steps+1):
        a=math.radians(start+(end-start)*j/steps)
        verts.extend((x+r*math.cos(a),y+dy,z+r*math.sin(a)) for r,dy in profile)
    k=len(profile)
    f=[tuple(reversed(range(k))),tuple(range(steps*k,(steps+1)*k))]
    for j in range(steps):
        for i in range(k):
            a=j*k+i;b=j*k+(i+1)%k
            f.append((a,b,b+k,a+k))
    return keep(g,add(n,m,verts,f))

def label(g,string,p,size):
    d=bpy.data.curves.new(string,'FONT')
    d.body=string;d.size=size;d.align_x='CENTER';d.align_y='CENTER';d.resolution_u=3
    d.materials.append(white)
    o=bpy.data.objects.new(string,d);s.collection.objects.link(o)
    o.rotation_euler=(math.pi/2,0,math.pi)
    o.location=p
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    return keep(g,bpy.context.object)

room='01 Alcove shell'
retry='02 Inner checkpoint'
portal='03 Exit portal'
fog='04 Fog threshold surround'
# Original physical floor strip in the archival lab is south +56 to +69.
# A thin visual sill joins it back to the bowl slab without a floor-height change.
box(room,'Floor cassette',base,(0,-62.5,-.215),(18,13,.44),.055)
box(room,'Approach floor sill',base,(0,-54,-.205),(16,4.32,.43),.030)
box(room,'Back wall',frame,(0,-69.08,4.5),(18.8,.20,9.0),.045)
for i in range(5):
    y=-67.7+i*2.6
    box(room,'Webbed canopy panel',frame,(0,y,9.0),(18.8,2.59,.44),.065)
    box(room,'Ribbed roof track',sheet,(0,y+1.2,8.65),(18.25,.23,.35),.040)
for x in (-4.9,4.9):
    box(room,'Inset roof key light',edge,(x,-60.4,8.55),(.22,5.7,.16),.027)
    box(room,'Warm roof rail',amber,(x,-60.4,8.452),(.112,5.57,.071),.023)
for sign in (-1,1):
    x=sign*9
    box(room,'Side load wall',frame,(x,-62.5,4.50),(1,13,9),.10)
    for y in [-57.2,-59.9,-62.6,-65.3,-68.0]:
        box(room,'Inset wall skin',sheet,(sign*8.45,y,4.42),(.105,2.58,8.61),.034)
        box(room,'Rib column',edge,(sign*8.35,y-1.26,4.51),(.23,.12,8.70),.028)
    for level in (.32,5.87):
        box(room,'Service conduit band',oxide,(sign*8.33,-62.5,level),(.18,12.50,.20),.035)
    box(room,'Exterior utilitarian light',amber,(sign*8.19,-61.9,3.30),(.09,2.88,.10),.025)
for x in [-7.9,-5.9,-3.9,-1.9,.1,2.1,4.1,6.1,8.1]:
    box(room,'Rear wall pan',sheet,(x,-68.94,4.47),(1.88,.15,8.66),.05)
for i in range(8):
    y=-67.8+i*1.44
    for x in (-6.9,6.9):
        box(room,'Service pavement',floor,(x,y,.017),(2.6,1.39,.027),.009)
# Three embedded floor panels and thin route edge strips keep the walk clear.
for i in range(6):
    box(room,'Inset walkway panel',floor,(0,-57.0-i*1.51,.013),(2.92,1.44,.014),.005)
for x in (-1.61,1.61):
    box(room,'Inset bronze floor seam',oxide,(x,-60.92,.011),(.105,11.37,.012),.004)
for x in (-7.05,7.05):
    box(room,'Service column',frame,(x,-55.42,2.75),(.68,.77,5.5),.063)
    box(room,'Warning paint',yellow,(x,-54.998,2.65),(.43,.085,1.10),.015)
for x in (-6.9,-6.38,-5.86,5.86,6.38,6.90):
    box(room,'Floor warning',yellow,(x,-52.09,.020),(.28,1.23,.033),.009,math.radians(-28 if x<0 else 28))

# Exact archive stake center X-4 and midpoint of +56 and +69.
px,py=-4,-62.5
box(retry,'Beveled retry footing',frame,(px,py,.14),(1.42,1.24,.28),.085)
box(retry,'Raised tread inset',edge,(px,py+.11,.29),(1.18,.80,.075),.035)
box(retry,'Main restart terminal',sheet,(px,py-.10,.89),(.90,.77,1.20),.064)
box(retry,'Copper spine',oxide,(px,py-.29,.92),(.24,.52,1.10),.038)
box(retry,'Terminal face hood',frame,(px,py+.30,1.36),(1.04,.31,.40),.044)
box(retry,'Lit check panel',amber,(px,py+.474,1.415),(.74,.049,.125),.015)
box(retry,'Inbound face',black,(px,py+.475,1.258),(.73,.053,.135),.015)
label(retry,'CHECKPOINT',(px,py+.510,1.26),.108)
for x in (px-.47,px+.47):
    bolt(retry,'Foundation stud',edge,(x,py+.48,.32),.074,.10)
    bolt(retry,'Panel bolt',oxide,(x,py+.482,1.47),.043,.04,8,True)
for sign in (-1,1):
    x=px+sign*.42
    box(retry,'Telemetry rod',frame,(x,py-.23,1.77),(.11,.11,.56),.013)
    box(retry,'Amber rod status',amber,(x,py-.23,2.052),(.088,.088,.092),.014)

# Exact archive exit: X+4, Y+4.2, az1-1.2, 3.4m centerline radius.
p=(4,-67.8,4.2)
for i in range(12):
    a=i*30
    arc(portal,'Cast housing segment',frame,p,
        [(3.03,-.20),(3.21,-.35),(3.69,-.37),(3.85,-.26),
         (3.85,.24),(3.69,.36),(3.19,.34),(3.03,.17)],a+1.3,a+28.7,6)
    arc(portal,'Machined front face',edge,p,[(3.30,.345),(3.68,.345),(3.66,.399),(3.31,.399)],
        a+2,a+28,6)
    arc(portal,'Inset blue arc',blue,p,[(3.11,.220),(3.20,.220),(3.20,.309),(3.12,.309)],
        a+.72,a+29.28,7)
    for t in (a+4.6,a+25.4):
        ang=math.radians(t)
        bolt(portal,'Face bolt',oxide,(4+3.51*math.cos(ang),-67.389,4.2+3.51*math.sin(ang)),.080,.046,8,True)
for x in (2.25,5.75):
    box(portal,'Portal seat block',oxide,(x,-67.775,.35),(.72,1.00,.70),.085)
    box(portal,'Foundry hold-down',frame,(x,-67.75,.105),(1.04,1.25,.21),.045)
box(portal,'Exit sign',frame,(4,-67.43,8.48),(3.65,.29,.55),.055)
box(portal,'Exit enamel keyline',blue,(4,-67.273,8.70),(3.19,.058,.055),.011)
label(portal,'EXIT PORTAL',(4,-67.254,8.45),.255)

# The archive fog plane is at Z+53, with an 18 m visual span and 8 m height.
# This surround leaves an open center, and the optional volume is render only.
for x in (-8.32,8.32):
    box(fog,'Unobtrusive fog side',frame,(x,-53.02,3.96),(.70,.63,7.9),.07)
    box(fog,'Fog strip',amber,(x*.972,-52.645,3.81),(.082,.066,7.40),.024)
for x in (-6,-3,0,3,6):
    box(fog,'Beam panel',edge,(x,-53.02,8.14),(2.96,.65,.38),.047)
box(fog,'Fight side sign',frame,(0,-53.39,8.11),(4.59,.17,.61),.052)
# This label faces the interior; turn it around the vertical axis.
o=label(fog,'ARENA',(0,-53.49,8.08),.300)
o.rotation_euler.z=0

def merge(n,parts):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join()
    o=parts[0];o.name=o.data.name=n
    bpy.context.view_layer.update()
    pts=[o.matrix_world@v.co for v in o.data.vertices]
    low,high=[Vector(fn(p[i] for p in pts) for i in range(3)) for fn in (min,max)]
    center=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
    o.data.transform(Matrix.Translation(-center)@o.matrix_world)
    o.matrix_world=Matrix.Translation(center)
    return o

objects={n:merge(n,oo) for n,oo in groups.items()}
target=out/'e12g-titan-retry-alcove.glb'
export(list(objects.values()),target)
raw=target.read_bytes()
doc=json.loads(raw[20:20+int.from_bytes(raw[12:16],'little')])
tri=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])
assert len(doc['nodes'])==len(doc['meshes'])==4 and tri<9200 and len(raw)<680000,(tri,len(raw))
assert not any(doc.get(k) for k in ('images','skins','animations','extensionsRequired'))
clear_scene()
bpy.ops.import_scene.gltf(filepath=str(bound))
old=[o for o in s.objects if o.type=='MESH' and o.name.startswith('06 South checkpoint pocket')]
assert old
for o in old:o.hide_render=True
prior=set(s.objects)
bpy.ops.import_scene.gltf(filepath=str(target))
imported=set(s.objects)-prior
bpy.context.view_layer.update()
def bvh(parts):
    vs=[];fs=[]
    for o in parts:
        if o.type!='MESH':continue
        n=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
        fs.extend(tuple(n+i for i in p.vertices) for p in o.data.polygons)
    return BVHTree.FromPolygons(vs,fs)
fit=bvh(imported)
composite=bvh(o for o in s.objects if o.type=='MESH' and o not in old)
floors=[]
for y in [-52,-53,-54,-55.5,-56.2,-58,-60,-62,-64,-66]:
    for x in [-1.8,-.9,0,.9,1.8]:
        hit=fit.ray_cast((x,y,.20),(0,0,-1),.36)[0]
        assert hit is not None and -.004<hit.z<.05,(x,y,hit)
        floors.append(hit.z)
corridor=0
for z in [.18,.52,1.05,1.70,2.2]:
    for x in [-1.8,-.9,0,.9,1.8]:
        assert fit.ray_cast((x,-51.45,z),(0,-1,0),14.8)[0] is None
        assert composite.ray_cast((x,-51.45,z),(0,-1,0),14.8)[0] is None, (x,z)
        corridor+=1
portal_mesh=[o for o in imported if o.type=='MESH' and
             (o.name.startswith(portal) or (o.parent and o.parent.name==portal))]
assert portal_mesh
pt=bvh(portal_mesh)
open_rays=0
for x in [-2,-1,0,1,2]:
    for z in [-2,-1,0,1,2]:
        assert pt.ray_cast((4+x,-66,4.2+z),(0,-1,0),2.6)[0] is None
        open_rays+=1

def aim(o,pos,target):
    o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def light(n,p,q,energy,color,size):
    d=bpy.data.lights.new(n,'AREA')
    d.energy,d.color,d.shape,d.size=energy,color,'DISK',size
    o=bpy.data.objects.new(n,d);s.collection.objects.link(o);aim(o,p,q)

def link_mesh(n,mesh):
    o=bpy.data.objects.new(n,mesh)
    s.collection.objects.link(o)
    return o

s.world=bpy.data.worlds.new('Arena indirect')
s.world.use_nodes=True
env=s.world.node_tree.nodes['Background']
env.inputs['Color'].default_value=(.20,.27,.42,1)
env.inputs['Strength'].default_value=.065
light('Rear cool bounce',(5.9,-66.45,6.63),(0,-61,2),2300,(.18,.42,1),5.6)
light('Checkpoint amber pool',(-5.6,-62.2,4.95),(-4.02,-61.8,.6),1320,(1,.45,.19),4.4)
light('High service strip',(0,-58.0,8.15),(0,-62.0,1.6),1450,(.42,.64,1),7)
light('Arena edge bounce',(0,-42,17),(0,-59,2),4450,(.50,.65,1),19)
light('Pod face',(-1.8,-56.45,4.0),(-4,-62.2,1.1),725,(1,.69,.38),4)
# Preview surfaces are deliberately not present in the portable GLB.
def preview(n, stops, scale, rough, alpha=None):
    m=bpy.data.materials.new(n);m.use_nodes=True
    nd=m.node_tree.nodes;nd.clear()
    ln=m.node_tree.links.new
    out=nd.new('ShaderNodeOutputMaterial')
    tc=nd.new('ShaderNodeTexCoord')
    noise=nd.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=scale
    noise.inputs['Detail'].default_value=4
    noise.inputs['Roughness'].default_value=rough
    ln(tc.outputs['Object'],noise.inputs['Vector'])
    ramp=nd.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    for i,(t,c) in enumerate(stops):
        e=ramp.color_ramp.elements[0] if i==0 else ramp.color_ramp.elements.new(t)
        e.position=t;e.color=(*c,1)
    ln(noise.outputs['Fac'],ramp.inputs[0])
    shader=nd.new('ShaderNodeEmission')
    ln(ramp.outputs['Color'],shader.inputs['Color'])
    shader.inputs['Strength'].default_value=1.8
    if alpha is not None:
        mix=nd.new('ShaderNodeMixShader')
        mix.inputs[0].default_value=alpha
        ln(nd.new('ShaderNodeBsdfTransparent').outputs[0],mix.inputs[1])
        ln(shader.outputs[0],mix.inputs[2])
        ln(mix.outputs[0],out.inputs['Surface'])
    else:
        ln(shader.outputs[0],out.inputs['Surface'])
    return m

bpy.ops.mesh.primitive_circle_add(vertices=84,radius=3.025,fill_type='NGON',
    location=(4,-67.79,4.2),rotation=(math.pi/2,0,0))
bpy.context.object.data.materials.append(preview('Exit ion field preview',[
   (.13,(.006,.014,.051)),(.43,(.011,.060,.21)),(.59,(.024,.16,.63)),
   (.71,(.1,.65,.98)),(.82,(.39,.94,1))],1.27,.58))
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,-53,3.67),rotation=(math.pi/2,0,0))
mist=bpy.context.object;mist.name='Review-only optically thin fog';mist.scale=(15.6,7.28,1)
mist.data.materials.append(preview('Fog threshold preview',[
    (.20,(.012,.04,.10)),(.45,(.038,.14,.22)),(.67,(.18,.44,.72)),(.83,(.30,.70,.92))],3.30,.58,.29))
cam=link_mesh('Alcove evidence camera',bpy.data.cameras.new('Alcove evidence camera'))
s.camera=cam
s.render.engine='CYCLES'
s.cycles.samples=38;s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.072
s.view_settings.view_transform='AgX'
s.view_settings.look='AgX - Medium High Contrast'
s.render.resolution_percentage=100
s.render.resolution_x,s.render.resolution_y=1580,1080
s.render.image_settings.file_format='JPEG';s.render.image_settings.color_mode='RGB'
s.render.image_settings.quality=94
for name,eye,point,lens,show in [
    ('entrance',(-.8,-46.3,3.8),(.1,-62.8,3.68),36,False),
    ('retry',(-6.85,-66.35,2.40),(-.85,-53.2,3.2),31,True),
]:
    mist.hide_render=not show
    aim(cam,eye,point);cam.data.lens=lens
    s.render.filepath=str(out/f'nov25-titan-alcove-{name}.jpg')
    if not os.getenv("WSC_GEOMETRY_ONLY"):bpy.ops.render.render(write_still=True)
(out/'validation.json').write_text(json.dumps({
    'scope':'Round 5 portable alcove art; not collision, gameplay, portals or fog effects.',
    'bowlSha256':pin,'archive':{'archiveRef':'ce1cf050b36fa236155ac26d43e721b9012c49df',
        'layoutBlob':'5d019a020361c47187ec889f2bc947f82cd9f98a','labBlob':'51a3b4bef1f2d4891172164d10893d98d450a3b9',
        'bowlWorldOrigin':[150,-150,165],'exitCenterWorld':[154,-145.8,232.8],
        'checkpointAnchorWorld':[146,-149.6,227.5],'fogPlaneCenterWorld':[150,-146,218]},
    'glb':{'bytes':len(raw),'triangles':tri,'sha256':hashlib.sha256(raw).hexdigest(),'meshNames':list(groups)},
    'reimport':{'oldPlaceholdersHiddenForRenders':len(old),'floorFitRays':len(floors),
        'floorYRange':[min(floors),max(floors)],'centerApproachClearRays':corridor,'centerApproachAlsoClearAgainstDonor':True,'exitApertureClearRays':open_rays}
},indent=2)+'\n')

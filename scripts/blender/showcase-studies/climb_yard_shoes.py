"""Measure six rails in the rebuilt West Climb Yard. Export one static shoe."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

base,out=(Path(p).resolve() for p in sys.argv[sys.argv.index('--')+1:])
out.mkdir(parents=True,exist_ok=True)
fingerprint=json.loads((base/'parity.json').read_text())['matched_signature']
expected=Path(__file__).resolve().parent.parent/'west-climb-rock/expected.json'
assert fingerprint in tuple(json.loads(expected.read_text())[key] for key in
                            ('semantic_signature','normalized_semantic_signature'))
bpy.ops.wm.open_mainfile(filepath=str(base/'climb-rock-editable.blend'))
scene=bpy.context.scene
scene.render.use_compositing=False


def bvh(items):
    verts,faces=[],[]
    dg=bpy.context.evaluated_depsgraph_get()
    for src in items:
        o=src.evaluated_get(dg)
        d=o.to_mesh();n=len(verts)
        verts.extend(o.matrix_world@v.co for v in d.vertices)
        faces.extend(tuple(n+j for j in p.vertices) for p in d.polygons)
        o.to_mesh_clear()
    return BVHTree.FromPolygons(verts,faces)


def hit(tree,x,y,z,sign,span):
    p=tree.ray_cast(Vector((x,y,z)),Vector((0,0,sign)),span)[0]
    assert p is not None,(x,y,z)
    return p.z


def project(prefix):
    obs=[o for o in scene.objects if o.type=='MESH' and o.name.startswith(prefix)]
    assert len(obs)==1,(prefix,len(obs))
    return obs[0]


ground=bvh([project('CLIMB | source yard footprint')])
defs=[('A',-166,-28,6),('B',-146,-44,10),('C',-170,-60,14)]
locations=[]
for n,x,y,h in defs:
    deck=bvh([project('CLIMB | deck '+n+' and ladder')])
    for slot,dx in enumerate((-.31,.31),1):
        rx,ry=x+dx,y-3.4
        z_ground=hit(ground,rx,ry,.15,-1,.3)
        z_rail=hit(deck,rx,ry,.10,1,.20)
        offsets=[(rx+ox,ry+oy) for ox,oy in ((-.030,0),(.030,0),(0,-.030),(0,.030))]
        gaps=[hit(deck,xx,yy,.10,1,.20)-hit(ground,xx,yy,.15,-1,.3) for xx,yy in offsets]
        assert max(abs(g-.1425) for g in gaps+[z_rail-z_ground])<.00002
        locations.append({'deck':n,'shoe':slot,'blender_xy':[rx,ry],
            'ground_m':round(z_ground,6),'rail_bottom_m':round(z_rail,6),
            'gap_mm':round((z_rail-z_ground)*1000,3),'deck_z_m':h})


def material(n,c,metal):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1)
    b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=.51
    return m


graphite=material('Climb cast foot steel',(.06,.095,.101),.60)
teal=material('Climb weathered enamel',(.08,.285,.253),.48)
zinc=material('Climb zinc fasteners',(.41,.35,.20),.67)
verts,faces,material_ids=[],[],[]


def ring(z,r,n=8,center=(0,0)):
    return [(center[0]+r*math.cos(math.tau*i/n),center[1]+r*math.sin(math.tau*i/n),z)
            for i in range(n)]


def stack(rings,m):
    start=len(verts); n=len(rings[0])
    verts.extend(v for layer in rings for v in layer)
    f=[tuple(reversed(range(start,start+n)))]
    for j in range(len(rings)-1):
        for i in range(n):
            a=start+j*n+i;b=start+j*n+(i+1)%n
            f.append((a,b,b+n,a+n))
    f.append(tuple(range(start+n*(len(rings)-1),start+n*len(rings))))
    faces.extend(f);material_ids.extend([m]*len(f))


# Overlap the rail at its bottom by 24 mm so the join reads as a sleeve.
# Model origin is the measured ground point; the foot seats 2 mm below it.
stack([ring(-.002,.132),ring(.008,.147),ring(.033,.147),ring(.044,.134)],0)
stack([ring(.036,.103),ring(.093,.103),ring(.128,.086),ring(.152,.086)],1)
stack([ring(.125,.087),ring(.147,.089),ring(.164,.080),ring(.1665,.075)],0)
for c in [(-.095,0),(.095,0),(0,-.095),(0,.095)]:
    stack([ring(.036,.023,6,c),ring(.053,.022,6,c),ring(.057,.016,6,c)],2)
data=bpy.data.meshes.new('Single Climb Yard ladder shoe')
data.from_pydata(verts,[],faces)
for m in (graphite,teal,zinc):data.materials.append(m)
for p,i in zip(data.polygons,material_ids):p.material_index=i
shoe=bpy.data.objects.new(data.name,data)
scene.collection.objects.link(shoe)
bpy.ops.object.select_all(action='DESELECT')
shoe.select_set(True);bpy.context.view_layer.objects.active=shoe
path=out/'w8a-climb-ladder-shoe.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False)
raw=path.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
g=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert len(g['nodes'])==len(g['meshes'])==1
assert not any(k in g for k in ('images','animations','skins'))
triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])
bpy.data.objects.remove(shoe,do_unlink=True)
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(path))
(shoe,)=[o for o in set(scene.objects)-before if o.type=='MESH']
nodes=[]
for i,r in enumerate(locations):
    o=shoe if i==0 else bpy.data.objects.new(f'Ladder shoe {r["deck"]}{r["shoe"]}',shoe.data)
    if i:scene.collection.objects.link(o)
    o.location=(*r['blender_xy'],r['ground_m'])
    nodes.append(o)
    z=r['ground_m']
    r['seat_overlap_mm']=round((z+.1665-r['rail_bottom_m'])*1000,3)
    # Compare against bottom of the unchanged lowest rung, not its center.
    r['nominal_first_rung_clearance_mm']=round((.33-.029-z-.1665)*1000,3)
    assert r['seat_overlap_mm']>23 and r['nominal_first_rung_clearance_mm']>100
bpy.context.view_layer.update()
for o,r in zip(nodes,locations):
    t=bvh([o]);x,y=r['blender_xy']
    assert abs(hit(t,x,y,0,1,.08)-(r['ground_m']-.002))<5e-5
    assert abs(hit(t,x,y,.4,-1,.4)-(r['ground_m']+.1665))<5e-5

for o in list(scene.objects):
    if o.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(o,do_unlink=True)
world=bpy.data.worlds.new('W8a cool daylight')
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.30,.42,.61,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.42
scene.world=world


def light(n,kind,p,target,power,size,c):
    d=bpy.data.lights.new(n,kind);d.energy,d.color=power,c
    if kind=='SUN':d.angle=size
    else:d.size=size
    o=bpy.data.objects.new(n,d);scene.collection.objects.link(o);o.location=p
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()


light('Late warm key','SUN',(-170,-43,11),(-166,-30,2),2.6,.13,(1,.78,.58))
light('Joint fill','AREA',(-169,-35,2.5),(-166,-31.4,.2),375,3.2,(.67,.86,1))
cam=bpy.data.objects.new('Ladder fit review',bpy.data.cameras.new('Ladder fit review'))
scene.collection.objects.link(cam);scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=52;scene.cycles.use_denoising=False
scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.055
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='JPEG'
scene.render.image_settings.quality=91;scene.view_settings.view_transform='AgX'


def render(n,p,target,lens,dim,show=True):
    for o in nodes:o.hide_render=not show
    cam.location=p
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=dim
    scene.render.filepath=str(out/(n+'.jpg'))
    bpy.ops.render.render(write_still=True)


for n,on in [('before',False),('fitted',True)]:
    render(n,(-165.05,-33.64,.57),(-166,-31.395,.23),62,(1110,705),on)
render('exit',(-168.68,-33.3,7.28),(-166,-31.1,6.23),43,(1100,760))
proof={'scope':'Static mounting study. Original terrain, rails, rungs and deck exits unchanged.',
       'verified_base_fingerprint':fingerprint,
       'asset':{'bytes':len(raw),'triangles':triangles,'sha256':hashlib.sha256(raw).hexdigest()},
       'rail_centres':locations,'guard_opening_m':1.5,'upper_rail_rise_m':.78,
       'notes':'Pocket overlaps rail intentionally. No structural, collision or climbing claim.'}
(out/'w8a-shoe-fit.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))

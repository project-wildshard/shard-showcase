"""Static E10c Room 2 art and measured handoff to the existing Room 3 study."""
import hashlib
import json
import math
import os
from pathlib import Path
import runpy
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import clear_scene, export, output_directory

out=output_directory()
r3_script=HERE/'vault_climb_room.py'
r3_digest='9caf60f2789ced4d31c5eb42756bf0cf3e9458134c64216b4ab76f785f000520'
assert hashlib.sha256(r3_script.read_bytes()).hexdigest()==r3_digest
old_args=sys.argv[:]
previous=os.environ.get('WSC_METADATA_ONLY')
sys.argv=['blender','--',str(out/'room3-probe')]
os.environ['WSC_METADATA_ONLY']='1'
try:
    runpy.run_path(str(r3_script),run_name='__main__')
except SystemExit as e:
    assert e.code==0
finally:
    sys.argv=old_args
    if previous is None:os.environ.pop('WSC_METADATA_ONLY',None)
    else:os.environ['WSC_METADATA_ONLY']=previous
scene=bpy.context.scene
LOCAL_TO_R3=25.5
PLATE=.903
PITCH=3.155
SILL=1.006
NEAR_X=5*PITCH/2
R3_X=172.4-160.5-PITCH/2
FAR_X=R3_X-.003


def tree(objs, x_delta=0):
    verts,faces=[],[]
    dg=bpy.context.evaluated_depsgraph_get()
    for src in objs:
        ob=src.evaluated_get(dg)
        m=ob.to_mesh();n=len(verts)
        verts.extend(ob.matrix_world@v.co+Vector((x_delta,0,0)) for v in m.vertices)
        faces.extend(tuple(n+j for j in f.vertices) for f in m.polygons)
        ob.to_mesh_clear()
    return BVHTree.FromPolygons(verts,faces)


def down(t,x,y):
    hit=t.ray_cast(Vector((x,y,1.25)),Vector((0,0,-1)),1.25)[0]
    assert hit is not None,(x,y)
    return hit.z


r3_entry=[o for o in scene.objects if o.name.startswith('Entry tread')]
r3_tread=tree(r3_entry,LOCAL_TO_R3)
nearby=[o for o in scene.objects if o.type=='MESH' and any(
        (o.matrix_world@Vector(v)).x + LOCAL_TO_R3 < FAR_X+.16 for v in o.bound_box)]
assert nearby
r3_shell=tree(nearby,LOCAL_TO_R3)
landing_samples=[down(r3_tread,R3_X+.027,y) for y in (-.6,0,.6)]
assert max(abs(z-SILL) for z in landing_samples)<.0011
room3_backdrop=[]
for o in scene.objects:
    if o.type=="MESH" and o.name.startswith(("Threshold from Room 2","01 wall ladder","Ladder landing")):
        d=o.data
        room3_backdrop.append((o.name,d,Matrix.Translation((LOCAL_TO_R3,0,0))@o.matrix_world))
assert room3_backdrop
clear_scene()

names={
 'plate':('wsc-prop-064-metal-floor-plates.glb','7e4eef8077b1d59fd31d17235ef1cedca8bab9910c0c283bcf5546fae144ed85'),
 'bay':('wsc-arch-002-industrial-wall-bay.glb','24f3a7736d111033d724f0f6244c4d10f757fe3066ea1b8b12d5ef60a5a6f625'),
 'open':('wsc-module-021-open-circular-vault-door.glb','dcaca9e40d0e6421fdd62c1dedf537e7004ad0016b05144beed419377682cc68'),
 'closed':('wsc-prop-063-round-vault-bulkhead.glb','25db93c5d45901a6599674ea857982700f57705c1b171e23978140537e41eedf')}
templates={}
for label,(name,pin) in names.items():
    path=HERE.parents[2]/'public/assets/wildshard-art'/name
    assert hashlib.sha256(path.read_bytes()).hexdigest()==pin
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    objects=sorted(set(scene.objects)-before,key=lambda o:o.name)
    templates[label]=[(o.name,o.data,o.matrix_world.copy()) for o in objects if o.type=='MESH']
    for o in objects:bpy.data.objects.remove(o,do_unlink=True)

placements=[]
def place(key,name,p,yaw=0):
    T=Matrix.Translation(p)@Matrix.Rotation(math.radians(yaw),4,'Z')
    arr=[]
    for n,d,m in templates[key]:
        o=bpy.data.objects.new(f'{name} | {n}',d)
        scene.collection.objects.link(o)
        o.matrix_world=T@m
        arr.append(o)
    placements.append({'key':key,'name':name,'local_origin':p,'yaw':yaw})
    return arr


def mat(n,rgb,metal=.3,em=0):
    m=bpy.data.materials.new(n)
    m.diffuse_color=(*rgb,1);m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*rgb,1)
    b.inputs['Metallic'].default_value=metal
    b.inputs['Roughness'].default_value=.52
    b.inputs['Emission Color'].default_value=(*rgb,1)
    b.inputs['Emission Strength'].default_value=em
    return m


black=mat('Blue black armour',(.063,.104,.129),.50)
steel=mat('Burnished threshold zinc',(.26,.34,.35),.68)
orange=mat('Ochre warning enamel',(.52,.151,.031))
cyan=mat('Cyan route stripe',(.049,.62,.64),.20,1.8)
white=mat('White cold staging lamp',(.64,.81,.88),0,2)


def box(n,p,d,m,bevel=0):
    x,y,z=p;a,b,c=(i*.5 for i in d)
    mesh=bpy.data.meshes.new(n)
    mesh.from_pydata([(x+i*a,y+j*b,z+k*c) for k in (-1,1) for j in (-1,1) for i in (-1,1)],
         [],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)])
    mesh.materials.append(m)
    o=bpy.data.objects.new(n,mesh)
    scene.collection.objects.link(o)
    if bevel:
        mod=o.modifiers.new('Small edge knock','BEVEL')
        mod.width,mod.segments=bevel,1
        o.modifiers.new('Face normals','WEIGHTED_NORMAL')
    return o


# Export only original transition parts. No copy of donor room assets or script-generated scene.
custom=[box('R2 transition | top tread',((NEAR_X+FAR_X)/2,0,SILL-.040),
            (FAR_X-NEAR_X,2.5,.08),steel,.004),
        box('R2 transition | west support',((NEAR_X+9.49)/2,0,.793),
            (9.49-NEAR_X,2.42,.234),black,.02)]
for y in (-1.14,1.14):
    custom.append(box('R2 transition | flush inset marker',
                      ((NEAR_X+FAR_X)/2,y,SILL+.0005),
                      (FAR_X-NEAR_X-.06,.04,.001),cyan))
file=out/'vault-r2-threshold.glb'
export(custom,file)
raw=file.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert not any(k in d for k in ('images','animations','skins','cameras'))
triangles=sum(d['accessors'][p['indices']]['count']//3
              for m in d['meshes'] for p in m['primitives'])
for o in custom:bpy.data.objects.remove(o,do_unlink=True)
contents=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(file))
threshold=[o for o in set(scene.objects)-contents if o.type=='MESH']
t=tree(threshold)
assert not t.overlap(r3_shell), 'Exact Room 3 recipe intersects the new threshold'

# Odd transverse count puts the sight line through the middle tile, not along a seam.
grid=[]
for i in range(-2,3):
    for j in range(-2,3):
        grid+=place('plate',f'R2 floor {i+3}:{j+3}',(PITCH*i,PITCH*j,PLATE))
room2=tree(grid)
join=[]
for y,z3 in zip((-.6,0,.6),landing_samples):
    z2=down(room2,NEAR_X-.027,y)
    new_west=down(t,NEAR_X+.027,y)
    new_east=down(t,FAR_X-.027,y)
    errors=[abs(z2-new_west),abs(z3-new_east)]
    assert max(errors)<.0021,errors
    join.append({'blender_y_m':y,'heights_world_m':[round(z-50,6) for z in (z2,new_west,new_east,z3)],
                 'worst_height_difference_mm':round(max(errors)*1000,4)})

# Matching open bulkhead, lowered so the historic lower lip sits under the plate.
# Explicit visual cross-section tests apply to donor mesh only, not physics.
doors=place('open','R2 toward R3 round bulkhead',(7.43,0,SILL-.99),-90)
portal=tree(doors)
clear_aperture=[]
for y in (-.60,0,.60):
    for h in (.08,.55,1.05,1.70,2.0):
        ray=portal.ray_cast(Vector((2,y,SILL+h)),Vector((1,0,0)),11)[0]
        assert ray is None,(y,h,ray)
        clear_aperture.append([y,h])
place('closed','R2 west end static round bulkhead',(-7.63,0,SILL),90)
place('plate','Exact R3 tread for joining proof',(11.9,0,PLATE))
for n,d,T in room3_backdrop:
    o=bpy.data.objects.new("Actual Room 3 reference | "+n,d)
    scene.collection.objects.link(o)
    o.matrix_world=T

for sign in (-1,1):
    y=sign*8.17
    box('Hab wall backing',(0,y,2.81),(15.93,.35,3.6),black,.04)
    for x in (-5.45,-1.84,1.84,5.45):
        for z in (SILL,SILL+2.082):
            place('bay','Linked industrial bay',(x,y-sign*.15,z),0 if sign>0 else 180)
    for x in (-5.88,0,5.88):
        box('Deep rib',(x,y-sign*.41,2.82),(.27,.43,3.71),steel,.03)
    for x in (-3.25,3.25):
        box('Recess service chest',(x,y-sign*.76,1.51),(2.2,.84,1.0),black,.04)
        box('Recess signal cover',(x,y-sign*1.189,1.71),(1.76,.04,.26),orange,.016)
    for x in (-3.55,3.55):
        box('Lateral inset light',(x,y-sign*.35,4.02),(2.35,.05,.11),cyan,.014)
box('West end backing',(-8.1,0,2.76),(.32,16.48,3.6),black,.045)
for y in (-5.42,5.42):
    box('East end partial backing',(7.73,y,2.75),(.30,5.20,3.5),black,.04)
    box('East reveal panel',(7.51,y,3.36),(.18,2.83,.83),orange,.03)
box('End lintel behind the door',(7.90,0,4.34),(.25,6.08,.60),black,.03)
for y in (-2.585,2.585):
    box('Inset jamb clearance backing',(7.89,y,2.57),(.24,1.21,3.13),black,.03)
# Dark dressing beyond the exact entry remains illustrative and is not exported.
box('Cutaway backdrop at Room 3',(17.8,0,2.95),(.23,6.7,4.9),black,.02)
for y in (-1.28,1.28):
    for x in (-6,-3,0,3,6):
        box('Inlaid wayfinding dash',(x,y,SILL+.013),(1.50,.064,.016),cyan,.004)
ceiling=[]
ceiling.append(box('Room cap',(0,0,4.87),(16.42,16.60,.28),black,.04))
for x in (-4,0,4):
    ceiling.append(box('Overhead steel spine',(x,0,4.49),(.19,16.1,.33),steel,.04))
    for y in (-4.25,4.25):
        ceiling.append(box('Overhead diffuser',(x,y,4.285),(.33,2.3,.09),white,.02))

def lamp(n,p,target,watts,size,color):
    d=bpy.data.lights.new(n,'AREA')
    d.energy,d.size,d.color=watts,size,color
    o=bpy.data.objects.new(n,d)
    scene.collection.objects.link(o);o.location=p
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()


for x in (-5,0,5):
    for y in (-4.15,4.15):
        lamp('Chamber light',(x,y,4.19),(x,y/2,1.05),420,2.1,(.66,.86,1))
lamp('Warm threshold wash',(6.5,1,4.12),(7.5,0,1.62),680,2.5,(1,.52,.23))
lamp('Far route lamps',(11.1,0,3.6),(10.2,0,1.01),610,2.2,(.48,1,.90))
world=bpy.data.worlds.new('Slate Vault environment');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.25,.40,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.31
scene.world=world
cam=bpy.data.objects.new('Room 2 evidence camera',bpy.data.cameras.new('Room 2 evidence camera'))
scene.collection.objects.link(cam);scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=72;scene.cycles.use_denoising=False
scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.037
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='JPEG'
scene.render.image_settings.quality=91;scene.view_settings.view_transform='AgX'


def render(n,pos,target,ortho,lens):
    cam.location=pos
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO' if ortho else 'PERSP'
    if ortho:cam.data.ortho_scale=lens
    else:cam.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=(1340,920)
    scene.render.filepath=str(out/(n+'.jpg'))
    bpy.ops.render.render(write_still=True)


render('room-eye',(-5.90,-.50,SILL+1.70),(7.43,.1,2.5),False,28)
for o in ceiling:o.hide_render=True
render('room-plan',(3.1,0,26),(3.1,0,0),True,30.5)
receipt={'scope':'Static Room 2 art proposal. Room 1 native anchor and all gameplay are out of scope.',
         'placement':'GLTF (+X,+Y,+Z) to world [160.5+x, -50+y, -64+z].',
         'room3_source_sha256':r3_digest,'donors':names,'placement_recipe':placements,
         'floor_count':[5,5],'floor_pitch_m':PITCH,'nominal_opening_span_m':round(R3_X-NEAR_X,6),
         'threshold_span_m':round(FAR_X-NEAR_X,6),'east_joint_gap_m':.003,
         'nominal_threshold_top_world_y':SILL-50,'join_samples':join,
         'no_bvh_surface_intersection_with_room3':True,
         'door_open_mesh_ray_samples_y_and_height':clear_aperture,
         'threshold_asset':{'bytes':len(raw),'triangles':triangles,'sha256':hashlib.sha256(raw).hexdigest()}}
(out/'vault-r2-room.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('VAULT R2',join,len(raw),triangles)

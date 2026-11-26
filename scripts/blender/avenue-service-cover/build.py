"""Rebuild the Avenue paving's optional shoulder-side catch box cover."""
import bpy
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[3]
assets=root/'public/assets/wildshard-art'
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
V=Vector

def clear():
    for ob in list(scene.objects):bpy.data.objects.remove(ob,do_unlink=True)
def bring(p):
    prior=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    return sorted(set(scene.objects)-prior,key=lambda o:o.name)
def mat(n,c,r=.6,m=0):
    d=bpy.data.materials.new(n);d.diffuse_color=(*c,1);d.use_nodes=True
    q=d.node_tree.nodes.get('Principled BSDF')
    q.inputs['Base Color'].default_value=(*c,1)
    q.inputs['Roughness'].default_value=r;q.inputs['Metallic'].default_value=m
    return d

clear()
donor=assets/'wsc-module-004-avenue-paving.glb'
paving=bring(donor)
sha=hashlib.sha256(donor.read_bytes()).hexdigest()
assert sha=='049c6b7e91fa8d05a84178d3280eee72c4221728e535b806b5b4434509936739'
bpy.context.view_layer.update()
def geometry(obs):
    vertices=[];faces=[]
    ds=bpy.context.evaluated_depsgraph_get()
    for o in obs:
        if o.type!='MESH':continue
        e=o.evaluated_get(ds);m=e.to_mesh()
        n=len(vertices);vertices.extend(e.matrix_world@p.co for p in m.vertices)
        m.calc_loop_triangles()
        faces.extend(tuple(n+i for i in q.vertices) for q in m.loop_triangles)
        e.to_mesh_clear()
    return vertices,faces
paving_v,paving_f=geometry(paving)
assert abs(max(v.x for v in paving_v)-2.1)<.00001
assert abs(max(v.z for v in paving_v)-.0455)<.00001
iron=mat('Cast iron, blue-black',(.055,.072,.071),.48,.68)
edge=mat('Wear on black enamel',(.138,.161,.154),.52,.48)
bronze=mat('Aged bronze bosses',(.37,.205,.081),.40,.72)
stone=mat('Quiet warm cut limestone',(.265,.229,.173),.83,0)
inner=mat('Recess shadow steel',(.024,.029,.029),.84,.14)
boxes=[]
def box(name,at,size,material,bevel=.01,segments=2):
    bpy.ops.mesh.primitive_cube_add(size=1,location=at)
    ob=bpy.context.object;ob.name=name;ob.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(material)
    if bevel:
        mod=ob.modifiers.new('Cast or cut edge','BEVEL');mod.width=bevel;mod.segments=segments
        bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
        bpy.ops.object.modifier_apply(modifier=mod.name)
    boxes.append(ob)
    return ob
# One origin-centered drain cassette. The stone shoulder is intentionally
# outside the original module; the slotted surface is horizontal.
for side in (-1,1):
    box('Limestone cheek '+str(side),(side*.198,0,-.062),(.072,.78,.19),stone,.014)
    box('Limestone cap '+str(side),(0,side*.354,-.062),(.324,.072,.19),stone,.014)
box('Recess bottom',(0,0,-.130),(.325,.64,.023),inner,.004,1)
for side in (-1,1):
    box('Cast seat long '+str(side),(side*.148,0,.006),(.035,.637,.070),iron,.008,1)
    box('Cast seat end '+str(side),(0,side*.300,.006),(.264,.035,.070),iron,.008,1)
for k in range(-4,5):
    bar=box('Drain bar %02d'%k,(0,k*.061,.014),(.267,.031,.050),iron,.006,1)
    bar.rotation_euler.z=.125 if k%2==0 else -.125
for side in (-1,1):
    box('Wear lip '+str(side),(side*.142,0,.036),(.014,.52,.010),edge,.003,1)
for a in (-1,1):
    for b in (-1,1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=.014,depth=.010,location=(a*.141,b*.281,.036))
        ob=bpy.context.object;ob.name='Bronze fastener';ob.data.materials.append(bronze);boxes.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in boxes:ob.select_set(True)
bpy.context.view_layer.objects.active=boxes[0]
bpy.ops.object.join()
cover=bpy.context.object;cover.name='Avenue socketed iron cover'
scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
dest=out/'w0b-avenue-service-cover.glb'
bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_animations=False)
raw=dest.read_bytes()
doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert not any(t in doc for t in ('textures','images','animations','skins'))
triangles=sum(doc['accessors'][p['indices']]['count']//3 for m in doc['meshes'] for p in m['primitives'])
assert triangles<1500 and len(raw)<115000,(triangles,len(raw))
bpy.data.objects.remove(cover,do_unlink=True)
placements=[(2.338,-.74,0),(-2.338,1.36,math.pi)]
fitted=[]
for x,y,yaw in placements:
    obs=bring(dest)
    for ob in obs:
        if ob.parent not in obs:
            ob.matrix_world=Matrix.Translation((x,y,0))@Matrix.Rotation(yaw,4,'Z')@ob.matrix_world
    bpy.context.view_layer.update()
    v,f=geometry(obs)
    assert min(abs(p.x) for p in v)>2.10
    top=max(a.z for a in v)
    assert .030<top<.0455 and max(abs(p.y) for p in v)<3.59
    fitted.append(dict(x=x,y_along=y,yaw_rad=yaw,min_edge_clearance_m=min(abs(p.x) for p in v)-2.1,
        maximum_top_m=top,below_original_curb_m=.0455-top))
# Independently check the cassette actually has open slots above its insert.
solo=bring(dest);bpy.context.view_layer.update()
v,f=geometry(solo);tree=BVHTree.FromPolygons(v,f,all_triangles=True)
deep=shallow=0
for yi in range(301):
    y=-.28+yi*.56/300
    hit=tree.ray_cast((0,y,.10),(0,0,-1),.28)[0]
    if hit and hit.z<-.105:deep+=1
    if hit and hit.z>.025:shallow+=1
assert deep>70 and shallow>70,(deep,shallow)
for ob in solo:bpy.data.objects.remove(ob,do_unlink=True)
receipt=dict(scope='Optional decorative inserts just outside the exact WSC-MODULE-004 paving at identity. No drainage simulation or collision change.',
    donor_sha256=sha, asset=dest.name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),triangles=triangles,
    primitives=len(doc['meshes'][0]['primitives']), placements=fitted, open_slot_rays_to_recess=deep,rays_to_bars=shallow, total_slot_rays=301)
(out/'fit.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('AVENUE COVER',receipt)
if os.getenv('WSC_METADATA_ONLY')=='1':sys.exit(0)

def place(obs,x,y,z,az=0):
    for ob in obs:
        if ob.parent not in obs:
            ob.matrix_world=Matrix.Translation((x,y,z))@Matrix.Rotation(az,4,'Z')@ob.matrix_world
    bpy.context.view_layer.update()
for y in [-7.2,7.2]:
    place(bring(donor),0,y,0)
# Staging only: shoulder blends into the separate planter bed, stays
# below the outside stone wall, and is not exported or treated as a collider.
shoulder=mat('Dry compacted ochre shoulder',(.164,.126,.088),.89)
box('Staged west shoulder',(-4.1,0,-.195),(4,24,.30),shoulder,0)
box('Staged east shoulder',(4.1,0,-.195),(4,24,.30),shoulder,0)
for x,y,az in [(-4.15,-2.8,math.pi/2),(4.15,3.3,-math.pi/2)]:
    place(bring(assets/'wsc-prop-014-planter-bed.glb'),x,y,-.039,az)
    place(bring(assets/'wsc-prop-012-deciduous-tree.glb'),x,y+.2,-.037,.33)
scene.world=bpy.data.worlds.new('Clear afternoon');scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background')
bg.inputs[0].default_value=(.43,.57,.75,1);bg.inputs[1].default_value=.48
bpy.ops.object.light_add(type='SUN',location=(4,-5,8))
sun=bpy.context.object;sun.rotation_euler=V((-.64,.52,-.72)).to_track_quat('-Z','Y').to_euler()
sun.data.energy=2.5;sun.data.angle=.12;sun.data.color=(1,.83,.65)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam
scene.render.engine='CYCLES'
scene.cycles.samples=30;scene.cycles.use_denoising=False;scene.cycles.adaptive_threshold=.053
scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
for n,eye,target,lens,wh in [
    ('avenue-cover-detail',(2.96,-1.62,.84),(2.24,-.70,.005),43,(960,900)),
    ('avenue-cover-context',(-.67,-4.4,2.22),(.39,.49,.03),29,(1280,900))]:
    cam.location=eye;cam.rotation_euler=(V(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=wh
    scene.render.filepath=str(out/(n+'.png'))
    bpy.ops.render.render(write_still=True)

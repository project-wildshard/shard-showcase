"""A textureless far render mesh for the verified Band 6 sight screen."""
import bpy
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[3]
A=ROOT/'public/assets/wildshard-art'
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
P=A/'e6-sight-screen.glb'
source=hashlib.sha256(P.read_bytes()).hexdigest()
assert source=='102faeea77538d07423be1a4104c4b9260d39e35a84236157104b11da546db4e'
scene=bpy.context.scene
for o in list(scene.objects):bpy.data.objects.remove(o,do_unlink=True)
def read(path):
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    return sorted(set(scene.objects)-before,key=lambda o:o.name)
def material(n,c,m=.4,r=.53,e=0):
    d=bpy.data.materials.new(n);d.use_nodes=True;d.diffuse_color=(*c,1)
    q=d.node_tree.nodes.get('Principled BSDF')
    for k,v in {'Base Color':(*c,1),'Metallic':m,'Roughness':r,
      'Emission Color':(*c,1),'Emission Strength':e}.items():q.inputs[k].default_value=v
    return d

g=material('Folded grey steel',(.072,.111,.120),.55)
d=material('Ceramic seam and slots',(.033,.050,.057),.23)
s=material('Machined steel ribs',(.201,.243,.251),.73)
r=material('Oxide red kick and cap',(.44,.118,.040),.35,.62)
a=material('Copper end bumpers',(.68,.253,.071),.46)
c=material('Cyan service glass',(.029,.51,.61),.34,.34,.28)
parts=[]
def box(n,p,dim,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=n;o.dimensions=dim;o.data.materials.append(m)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Fold bevel','BEVEL');mod.width=bevel;mod.segments=1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    parts.append(o)
    return o
def slot(x,side):
    y=side*.281
    m=bpy.data.meshes.new("Flat vent")
    m.from_pydata([(x-.13,y,2.025),(x+.13,y,2.025),(x+.13,y,2.121),(x-.13,y,2.121)],[],[(0,1,2,3) if side<0 else (3,2,1,0)])
    o=bpy.data.objects.new("Flat vent",m);scene.collection.objects.link(o);o.data.materials.append(d);parts.append(o)
box('Continuous screen core',(0,0,1.50),(11.98,.48,3),d,0)
for i in range(6):
    x=(i-2.5)*1.98
    box('Folded steel bay',(x,0,1.54),(1.937,.556,2.732),g,.03)
    box('Cap strip',(x,0,2.91),(1.93,.484,.149),r)
    for side in (-1,1):
        box('Oxide kick panel',(x,side*.282,.451),(1.86,.026,.56),r)
        # Keep three contrasting reads at distance without modeled double inset trays.
        for k in (-1,0,1):
            slot(x+.47*k,side)
for x in (-5.925,-3.96,-1.98,0,1.98,3.96,5.925):
    box('Structural rib',(x,0,1.50),(.15,.6,2.95),s,.010)
for side in (-1,1):
    for x in (-5.72,5.72):
        box('Copper bumper',(x,side*.279,1.235),(.27,.038,.45),a)
    for x in (-4.97,4.97):
        box('Cyan lens',(x,side*.295,2.65),(.39,.01,.060),c)
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
model=bpy.context.object;model.name='Band 6 sight screen far'
scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
dest=out/'e6-sight-screen-far.glb'
bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_animations=False)
raw=dest.read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
prims=[p for m in doc['meshes'] for p in m['primitives']]
tris=sum(doc['accessors'][p['indices']]['count']//3 for p in prims)
assert tris<1450 and len(raw)<100000,(tris,len(raw))
assert len(prims)==6 and not any(k in doc for k in ('images','textures','skins','animations','cameras'))
bpy.data.objects.remove(model,do_unlink=True)
near=read(P);far=read(dest)
V=Vector
def shape(obs):
    pts=[];faces=[]
    for o in obs:
        if o.type!='MESH':continue
        i=len(pts);m=o.data;m.calc_loop_triangles()
        pts.extend(o.matrix_world@v.co for v in m.vertices)
        faces.extend(tuple(i+i2 for i2 in p.vertices) for p in m.loop_triangles)
    return [(round(min(p[k] for p in pts),5),round(max(p[k] for p in pts),5)) for k in range(3)],BVHTree.FromPolygons(pts,faces,all_triangles=True)
bounds,ref=shape(near);other,test=shape(far)
assert bounds==other==[(-6,6),(-.3,.3),(0,3)],(bounds,other)
def ray(t,pos,d,v=70):
    return t.ray_cast(pos,d,v)[0] is not None
stats=[]
for angle in (0,25,55,90,135,180):
    p=math.radians(angle);d=V((math.sin(p),math.cos(p),-.12)).normalized()
    u=V((d.y,-d.x,0)).normalized();v=u.cross(d)
    a=b=both=0
    for j in range(49):
        for i in range(201):
            pos=V((0,0,1.5))+u*(-6.5+13*i/200)+v*(-2+4*j/48)-d*25
            n,f=ray(ref,pos,d),ray(test,pos,d)
            a+=n;b+=f;both+=n and f
    stats.append(dict(angle_deg=angle,near_hits=a,far_hits=b,intersection=both,
      silhouette_iou=round(both/(a+b-both),6)))
assert min(a['silhouette_iou'] for a in stats)>.985,stats
heights={}
for y in (.85,1.7,3.1):
    counts=[sum(ray(tree,(-5.3+i*10.6/72,-8,y),(0,1,0),16) for i in range(73)) for tree in (ref,test)]
    heights[str(y)]=counts
assert heights=={'0.85':[73,73],'1.7':[73,73],'3.1':[0,0]},heights
proof=dict(scope='Optional far render mesh only, same placement and source collider retained.',
    donor_sha256=source,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),triangles=tris,primitives=len(prims),
    near_triangles=2916,near_bytes=192052,local_xyz_bounds=bounds,eye_height_rays=heights,angles=stats)
(out/'fit.json').write_text(json.dumps(proof,indent=2)+'\n')
print('BAND 6 FAR',proof)
if os.getenv('WSC_METADATA_ONLY')=='1':sys.exit(0)

# Match both camera setups and transforms. Only the model changes.
rot=Matrix.Rotation(-math.pi/6,4,'Z')
for ob in near+far:
    if ob.parent not in near+far:ob.matrix_world=rot@ob.matrix_world
low=read(A/'e6-low-cover-return.glb')
for ob in low:
    if ob.parent not in low:
        ob.matrix_world=Matrix.Translation((-12.524459,8.212156,0))@Matrix.Rotation(.0351613,4,'Z')@ob.matrix_world
floor=material('Foundry ash review floor',(.124,.104,.079),0,.88)
n=floor.node_tree.nodes;L=floor.node_tree.links
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3.2;tex.inputs['Detail'].default_value=3
coord=n.new('ShaderNodeTexCoord');L.new(coord.outputs['Object'],tex.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color=(.066,.051,.039,1);ramp.color_ramp.elements[1].color=(.194,.138,.083,1)
L.new(tex.outputs['Fac'],ramp.inputs[0]);L.new(ramp.outputs['Color'],n.get('Principled BSDF').inputs['Base Color'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.34;bump.inputs['Distance'].default_value=.076
L.new(tex.outputs['Fac'],bump.inputs['Height']);L.new(bump.outputs[0],n.get('Principled BSDF').inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=160);bpy.context.object.data.materials.append(floor)
scene.world=bpy.data.worlds.new('East evening haze');scene.world.use_nodes=True
p=scene.world.node_tree.nodes['Background']
p.inputs[0].default_value=(.27,.43,.64,1);p.inputs[1].default_value=.45
def aim(obj,target):
    obj.rotation_euler=(V(target)-obj.location).to_track_quat('-Z','Y').to_euler()
for name,kind,eye,target,power,size,col in [
    ('Low orange sun','SUN',(-12,-8,13),(0,0,0),2.8,.12,(1,.77,.57)),
    ('Cold back bounce','AREA',(1,7,8),(0,0,1),1450,11,(.51,.74,1))]:
    d=bpy.data.lights.new(name,kind);d.energy=power;d.color=col
    if kind=='SUN':d.angle=size
    else:d.size=size
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=eye;aim(o,target)
bpy.ops.object.camera_add(location=(9.8,-28,4.5))
cam=bpy.context.object;cam.data.lens=66;aim(cam,(0,0,1.24));scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=28;scene.cycles.use_denoising=False
scene.cycles.adaptive_threshold=.054
scene.render.resolution_x=1240;scene.render.resolution_y=840;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
for mode in ('near','far'):
    for ob in near:ob.hide_render=mode=='far'
    for ob in far:ob.hide_render=mode=='near'
    scene.render.filepath=str(out/('e6-screen-'+mode+'.png'));bpy.ops.render.render(write_still=True)

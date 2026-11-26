"""Fitted east dock-side grate/paint details for the exact C1 donor."""
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

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import clear_scene, output_directory

out=output_directory()
root=Path(__file__).resolve().parents[3]
assetdir=root/'public/assets/wildshard-art'
pins={
    'wsc-scene-007-c1-loading-yard':'77cdcd7033f3c03a8fcf1c8e38b024adfca2470f53cd4af76b5b901a90431394',
    'e11c-c1-dock-shutter-leaf':'444e796844a2557a421ac69c86ca5d18be98595dc1607c7430aa323b4e924fec',
    'e11c-c1-dock-relay-strip':'851d34af7ebb765da8d7a129ddac454c71d568848997b129425e9d10ea95e424',
}
for name,digest in pins.items():
    assert hashlib.sha256((assetdir/(name+'.glb')).read_bytes()).hexdigest()==digest
layout=json.loads((root/'project/layouts/wsc-scene-007-c1-loading.json').read_text())
world_x,_,world_z=layout['origin_world_x_y_z']
scene=bpy.context.scene
clear_scene()

def finish(name,rgb,metal,rough):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    n=m.node_tree.nodes['Principled BSDF']
    n.inputs['Base Color'].default_value=(*rgb,1)
    n.inputs['Metallic'].default_value=metal
    n.inputs['Roughness'].default_value=rough
    return m

iron=finish('Patinated blue cast iron',(.087,.126,.132),.68,.48)
dark=finish('Grate shadow inset',(.021,.030,.030),.30,.8)
rust=finish('Worn ochre casting marks',(.48,.25,.092),.29,.60)
paint=finish('Ochre loading-bay paint',(.65,.326,.075),.09,.68)
cream=finish('Pale enamel witness marks',(.64,.59,.44),.05,.7)

class Mesh:
    def __init__(self):
        self.vertices=[]
        self.faces=[]
        self.materials=[]

    def faces_from(self,xyz,faces,m):
        i=len(self.vertices)
        self.vertices.extend(xyz)
        self.faces.extend(tuple(i+j for j in f) for f in faces)
        self.materials.extend([m]*len(faces))

    def box(self,x,y,z,l,w,h,m):
        self.faces_from([(x+i*l/2,y+j*w/2,z+k*h)
                         for k in (0,1) for j in (-1,1) for i in (-1,1)],
          [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m)

    def paint(self,xy,z,m):
        self.faces_from([(x,y,z) for x,y in xy],[tuple(range(len(xy)))],m)

    def model(self,name):
        d=bpy.data.meshes.new(name)
        d.from_pydata(self.vertices,[],self.faces); d.update()
        mats=list(dict.fromkeys(self.materials))
        for m in mats:d.materials.append(m)
        for p,m in zip(d.polygons,self.materials):p.material_index=mats.index(m)
        o=bpy.data.objects.new(name,d)
        scene.collection.objects.link(o)
        return o

def deliver(name,b):
    o=b.model(name)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active=o
    f=out/(name+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',use_selection=True,
                             export_animations=False,export_texcoords=False)
    raw=f.read_bytes()
    assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
    doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
    assert 'images' not in doc and len(doc['nodes'])==len(doc['meshes'])==1
    assert not any(k in doc['nodes'][0] for k in ('rotation','translation','scale','matrix'))
    tris=sum(doc['accessors'][p['indices']]['count']//3 for p in doc['meshes'][0]['primitives'])
    assert tris<=420 and len(raw)<24576
    bpy.data.objects.remove(o,do_unlink=True)
    return f,{'bytes':len(raw),'triangles':tris,'primitives':len(doc['meshes'][0]['primitives']),
              'sha256':hashlib.sha256(raw).hexdigest()}

# 2.1m cast grate cap, with a dark strip below the visible slots (not a hole).
g=Mesh()
g.box(0,0,.001,2.10,.33,.002,dark)
for x in (-1.014,1.014):g.box(x,0,.003,.072,.33,.008,iron)
for y in (-.147,.147):g.box(0,y,.004,1.956,.036,.007,iron)
for j in range(22):
    x=.085*(j-10.5)
    g.box(x,0,.004,.045,.258,.008,iron)
for x in (-.969,.969):
    g.box(x,0,.004,.021,.258,.008,rust)
grate=deliver('e11c-c1-dock-drain-cap',g)

# Paint lies in the plane of the original yard; stencil edges are split
# to leave concrete between the enamel segments rather than a decal sheet.
s=Mesh()
for x in (-.17,.17):
    s.paint([(x-.060,-.42),(x+.018,-.42),(x+.100,.31),
             (x+.044,.39),(x-.012,.31)],.002,paint)
for y in (-.36,.31):
    s.paint([(-.245,y),(-.221,y),(-.221,y+.046),(-.245,y+.046)],.002,cream)
stencil=deliver('e11c-c1-dock-side-mark',s)

def load(f,loc=(0,0,0),yaw=0):
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(f))
    objects=set(scene.objects)-before
    transform=Matrix.Translation(loc)@Matrix.Rotation(yaw,4,'Z')
    for o in objects:
        if o.parent not in objects:o.matrix_world=transform@o.matrix_world
    bpy.context.view_layer.update()
    return objects

def tree(objects):
    verts,tris=[],[]
    for o in objects:
        if o.type!='MESH':continue
        i=len(verts)
        verts.extend(o.matrix_world@p.co for p in o.data.vertices)
        o.data.calc_loop_triangles()
        tris.extend(tuple(i+k for k in t.vertices) for t in o.data.loop_triangles)
    return BVHTree.FromPolygons(verts,tris,all_triangles=True)

holder=lambda name: assetdir/(name+'.glb')
donor=load(holder('wsc-scene-007-c1-loading-yard'))
receiver=tree(donor)
records=[]
assembled={}
up=Vector((0,0,1))
for name in ('D1','D2'):
    sign=1 if name=='D1' else -1
    x,wz=layout['door_x_z'][name]
    X,Y=x-world_x,world_z-wz
    yaw=sign*math.pi/2
    for side in (-1,1):
        load(holder('e11c-c1-dock-shutter-leaf'),(X-sign*.98,Y+side*3.71,0),yaw)
    load(holder('e11c-c1-dock-relay-strip'),(X+sign*.916,Y,4.21),yaw)
    placed=[]
    for side in (-1,1):
        for label,model,off,road,angle,dim in (
            ('drain',grate,3.07,2.99,yaw+math.pi/2,(2.10,.33)),
            ('paint',stencil,2.88,4.78,yaw,(.60,.84)),
        ):
            center=Vector((X+sign*road,Y+side*off,0))
            m=Matrix.Rotation(angle,3,'Z')
            heights=[]
            for i in range(5):
                for j in range(5):
                    p=center+m@Vector((dim[0]*(i/4-.5),dim[1]*(j/4-.5),0))
                    hit=receiver.ray_cast(p+up*7,-up,8)[0]
                    assert hit is not None,(name,label,p)
                    heights.append(hit.z)
            h=heights[0]
            assert max(heights)-min(heights)<.00001 and -.001<h<.08,(name,label,heights)
            center.z=h
            objects=load(model[0],center,angle)
            overlay,=objects
            mpts=[overlay.matrix_world@v.co for v in overlay.data.vertices]
            assert all(abs(p.y-Y)>2.50 for p in mpts),(name,label)
            assert all(0.0004<p.z-h<.013 for p in mpts),(name,label)
            assert not receiver.overlap(tree(objects)),(name,label)
            # Every reimported vertex has the same court receiver below, not just the layout samples.
            assert all(abs(receiver.ray_cast(Vector((p.x,p.y,7)),-up,8)[0].z-h)<.00002 for p in mpts)
            placed.extend(objects)
            records.append({'dock':name,'side':side,'overlay':label,'floor_rays':25,
                'blender_x_y_z':[round(float(v),6) for v in center],
                'three_x_y_z':[round(float(center.x+world_x),6),round(float(h),6),round(float(world_z-center.y),6)],
                'blender_yaw':round(angle,7),'max_rise_m':round(max(p.z-h for p in mpts),6)})
    assembled[name]=(X,Y,sign,placed)
report={'scope':'visual only, no floor cut, collider, door or wave change','pinned_donors':pins,
        'models':{grate[0].stem:grate[1],stencil[0].stem:stencil[1]},'placements':records}
(out/'e11c-c1-dock-apron.json').write_text(json.dumps(report,indent=2)+'\n')
print('DOCK APRON FIT',len(records),grate[1],stencil[1],flush=True)

if os.getenv('WILDSHARD_VALIDATE_ONLY')!='1':
    scene.render.engine='CYCLES';scene.cycles.samples=40
    scene.cycles.adaptive_threshold=.04;scene.cycles.use_denoising=False
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='WEBP'
    scene.render.image_settings.quality=90
    world=bpy.data.worlds.new('Steel blue dusk')
    scene.world=world;world.use_nodes=True
    bg=world.node_tree.nodes['Background']
    bg.inputs[0].default_value=(.45,.59,.73,1);bg.inputs[1].default_value=.42
    def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
    X,Y,_,_=assembled['D1']
    for name,xyz,target,energy,size,color in (
        ('warm service sodium',(X+5.7,Y-3.2,6),(X+2,Y,1),1700,4.0,(1,.74,.48)),
        ('cold yard bounce',(X+7,Y+4,7),(X+1,Y,1.6),2250,7,(.62,.79,1)),
        ('back room yellow',(X-3.4,Y,3.62),(X+1,Y,.3),550,2.8,(1,.62,.32)),
    ):
        b=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,b);scene.collection.objects.link(o)
        b.energy=energy;b.size=size;b.color=color;o.location=xyz;aim(o,target)
    bpy.ops.object.camera_add()
    cam=bpy.context.object;scene.camera=cam
    def shot(n,xyz,target,lens,res):
        cam.location=xyz;aim(cam,target);cam.data.lens=lens
        scene.render.resolution_x,scene.render.resolution_y=res
        scene.render.filepath=str(out/(n+'.webp'))
        bpy.ops.render.render(write_still=True)
    shot('nov26-e11c-dock-apron-wide',(X+11.5,Y-2.3,4.1),(X+2,Y,1.43),35,(1440,890))
    shot('nov26-e11c-dock-apron-detail',(X+5.8,Y-3.9,.97),(X+3,Y-3.04,.065),39,(1280,900))

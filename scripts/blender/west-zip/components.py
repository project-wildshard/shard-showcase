"""Blender 4.3; run blender -b -t 6 --python build_w08.py."""
import bpy,bmesh,math,random
from pathlib import Path
from mathutils import Vector, Matrix
from math import radians as r
root=REPO/'public/assets/wildshard-art'
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
def collection(name):
    c=bpy.data.collections.new(name);S.collection.children.link(c);return c
def to(obj,c):
    for old in list(obj.users_collection):old.objects.unlink(obj)
    c.objects.link(obj)
    return obj
core=collection('W08 | existing art')
scenic=collection('W08 | illustrative context only')
cable=collection('W08 | illustrative path, not collision')
rig=collection('W08 | cameras and lighting')
def mat(name,color,metal=0,rough=.65):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    return m
def box(name,xyz,dimensions,m,bevel=.06,coll=scenic):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz);o=bpy.context.object;o.name=name;o.dimensions=dimensions
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
    if bevel:
        v=o.modifiers.new('Catch the sun','BEVEL');v.width=bevel;v.segments=2
        o.modifiers.new('Weighted edges','WEIGHTED_NORMAL')
    return to(o,coll)
def glb(pattern):
    p=next(root.glob(pattern+'*.glb'))
    prior=set(S.objects)
    bpy.ops.import_scene.gltf(filepath=str(p))
    allnew=list(set(S.objects)-prior)
    ms=[]
    for o in sorted(allnew,key=lambda o:o.name):
        if o.type=='MESH':ms.append((o.name,o.data,o.matrix_world.copy()))
    for o in allnew:bpy.data.objects.remove(o,do_unlink=True)
    return ms
def place(proto,name,xyz,scale=(1,1,1),yaw=0,coll=core):
    T=Matrix.Translation(Vector(xyz))@Matrix.Rotation(yaw,4,'Z')@Matrix.Diagonal(Vector((*scale,1)))
    for n,d,m in proto:
        o=bpy.data.objects.new(f'{name} | {n}',d);coll.objects.link(o);o.matrix_world=T@m
    return T
# Map (x,y,z), Y up, to Blender (x,-z,y), Z up.
def map_to_blender(p):return Vector((p[0],-p[2],p[1]))
A=map_to_blender((-212,45,-34))
B=map_to_blender((-115,14,-16.5))
span=(B-A).length
tower=glb('wsc-module-001')
roof=glb('wsc-module-008')
pad=glb('wsc-prop-035')
fittings=glb('wsc-prop-033')
heading=math.atan2(B.y-A.y,B.x-A.x)
forward=Vector((math.cos(heading),math.sin(heading),0))
# Line up the rebuilt model's outward-facing clevis to the exact map anchor.
launch_base=A-forward*6.05-Vector((0,0,45))
place(tower,'MODULE-001 · West grapple tower',launch_base,yaw=heading+math.pi/2)
place(roof,'MODULE-008 · Cyan roof cap',(B.x,B.y,11.60),(1.55,1.7,1),heading)
place(pad,'PROP-035 · Landing pad',(B.x,B.y,12.0))
# Use only the factory-art terminals from PROP-033; do not stretch its sample mesh.
facing=(B-A).to_track_quat('X','Z').to_matrix().to_4x4()
for label,point,sgn in [('launch',A,-1),('landing',B,1)]:
    kept=0
    for n,d,m in fittings:
        mesh=d.copy();mesh.transform(m)
        bm=bmesh.new();bm.from_mesh(mesh)
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if sgn*v.co.x<4.42],context='VERTS')
        if bm.faces:
            bm.to_mesh(mesh);o=bpy.data.objects.new(f'PROP-033 | {label} terminal | {n}',mesh);core.objects.link(o)
            o.matrix_world=Matrix.Translation(point)@facing@Matrix.Translation((-sgn*4.65,0,-.34));kept+=1
        else:bpy.data.meshes.remove(mesh)
        bm.free()
    assert kept
steel=mat('Cable | blackened high-tensile steel',(.045,.060,.073),.7,.37)
curve=bpy.data.curves.new('99m plan run | 103.33m spatial span | illustrative','CURVE');curve.dimensions='3D';curve.bevel_depth=.065;curve.bevel_resolution=3
sp=curve.splines.new('POLY');sp.points.add(96)
for i,p in enumerate(sp.points):
    t=i/96;v=A.lerp(B,t);v.z-=4*1.2*t*(1-t);p.co=(*v,1)
assert (Vector(sp.points[0].co[:3])-A).length<1e-5
assert (Vector(sp.points[-1].co[:3])-B).length<1e-5
line=bpy.data.objects.new('W08 illustrative cable (no gameplay)',curve);cable.objects.link(line);curve.materials.append(steel)
concrete=mat('Town | buff limestone',(.58,.33,.14))
cornice=mat('Town | cut sandstone',(.77,.50,.28))
earth=mat('Frontier | dune grass',(.20,.255,.065))
pathmat=mat('Town | dusty limestone paving',(.36,.32,.24))
trim=mat('Town | weathered dark timber',(.083,.036,.019))
glass=mat('Town | shaded blue-green window',(.044,.12,.13),.23,.28)
def sitebox(name,site,dimensions,m,b=.06):
    x,y,z=site; c,s=math.cos(heading),math.sin(heading)
    o=box(name,(B.x+c*x-s*y,B.y+s*x+c*y,z),dimensions,m,b);o.rotation_euler.z=heading;return o
sitebox('Illustrative roof tie-down | flange',(1.86,0,12.16),(.84,.53,.27),steel)
sitebox('Illustrative roof tie-down | mast',(1.86,0,13.03),(.37,.34,1.91),steel)
sitebox('Illustrative roof tie-down | terminal arm',(1.02,0,13.95),(1.92,.24,.27),steel)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'w08-components.blend'))

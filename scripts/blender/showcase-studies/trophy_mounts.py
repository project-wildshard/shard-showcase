"""Rebuild the twelve placed shared trophy mounts without the plaza .blend."""
from pathlib import Path
import bpy,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import output_directory,clear_scene,export
clear_scene()
s=bpy.context.scene
for name,color,metal,rough in (
 ('Charcoal graphite • inset',(.078,.085,.091),.28,.54),
 ('Honey brass • cast',(.58,.31,.073),.78,.37),
):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
 bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
c=bpy.data.collections.new('W14 | empty trophy mounts');s.collection.children.link(c)
verts=[];faces=[];slots=[]
def block(x,y,z,a,b,c,mat):
    q=len(verts)
    verts.extend((x+a*i*.5,y+b*j*.5,z+c*k*.5) for i,j,k in ((-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)))
    poly=[(0,2,6,4),(1,5,7,3),(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6)]
    faces.extend(tuple(q+j for j in f) for f in poly);slots.extend([mat]*len(poly))
# The graphite inset and two flat mount tabs are deliberately empty.
block(0,0,0,.57,.045,.57,0)
for t in (-.270,.270):
    block(0,.023,t,.57,.011,.022,1)
    block(t,.023,0,.022,.011,.518,1)
for x in (-.148,.148):block(x,.026,.15,.048,.012,.036,1)
# Small blank brass line below each mount, leaving the actual earned info to UI.
block(0,.001,-.340,.366,.03,.050,0);block(0,.019,-.340,.324,.009,.004,1)

data=bpy.data.meshes.new('W14 Shared two-material display mount')
data.from_pydata(verts,[],faces);data.update()
for name in ('Charcoal graphite • inset','Honey brass • cast'):
 data.materials.append(bpy.data.materials[name])
for face,slot in zip(data.polygons,slots):face.material_index=slot
m=bpy.data.objects.new('W14 trophy mount 01',data);c.objects.link(m)
m.location=(0,0,0);bpy.context.view_layer.objects.active=m;m.select_set(True)
mod=m.modifiers.new('Mount arrises','BEVEL');mod.width=.004;mod.segments=1;bpy.ops.object.modifier_apply(modifier=mod.name)
m.data.calc_loop_triangles()
count=len(m.data.loop_triangles); assert count==396
X=[-42+i*1.25 for i in (-2.5,-1.5,-.5,.5,1.5,2.5)]
Z=(1.58,2.26);y=-17.841
objects=[]
for i,(x,z) in enumerate((x,z) for z in Z for x in X):
    ob=m if i==0 else m.copy()
    if i:c.objects.link(ob)
    ob.name=f'W14 trophy mount {i+1:02d}';ob.location=(x,y,z);objects.append(ob)
assert len({ob.data for ob in objects})==1
assert all(abs(ob.location.y-y)<1e-5 for ob in objects)
print('TROPHY_MOUNTS',len(objects),'shared_mobile',count,'placed',count*len(objects),flush=True)
export(objects,output_directory()/'west-plaza-empty-mounts.glb')

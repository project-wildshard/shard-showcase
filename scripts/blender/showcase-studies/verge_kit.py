"""Rebuild the Band 2 two-prop verge kit without its preview scene."""
from pathlib import Path
import bpy,math,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import output_directory,clear_scene,export
clear_scene()
s=bpy.context.scene
def solid(n,rgba,r=.82):
 m=bpy.data.materials.new(n);m.diffuse_color=(*rgba,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgba,1);bs.inputs['Roughness'].default_value=r
 return m
stone=solid('B2 shale chips',(.216,.174,.119));grass=solid('B2 dry edge grass',(.218,.217,.082));alt=solid('B2 green stems',(.14,.183,.072))
def mesh(n,vs,fs,mats,ids=None):
 m=bpy.data.meshes.new(n);m.from_pydata(vs,[],fs);m.update()
 for a in mats:m.materials.append(a)
 if ids:
  for f,z in zip(m.polygons,ids):f.material_index=z
 return m
tuft=mesh('B2 reusable edge clump',[(math.cos(i*.9)*w,math.sin(i*.9)*w,z) for i in range(7) for w,z in ((.038,0),(-.038,0),(.12,.24+.075*math.cos(i)),(.24,.28+.075*math.cos(i)))],[(i*4,i*4+1,i*4+2) for i in range(7)]+[(i*4+1,i*4+3,i*4+2) for i in range(7)],(grass,alt),[i%2 for i in range(14)])
chip=mesh('B2 reusable shale chip',[(-.13,-.09,0),(.13,-.08,0),(.12,.076,0),(-.13,.09,0),(.02,-.04,.088),(.046,.04,.087)],[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5),(4,5,3)],(stone,))
objects=[]
for name,x,m in (('Dry edge grass',0,tuft),('Shale chip',.7,chip)):
 assert all(f.area>1.e-6 for f in m.polygons)
 o=bpy.data.objects.new(name,m);s.collection.objects.link(o);o.location.x=x;objects.append(o)
export(objects,output_directory()/'band2-verge-kit.glb')

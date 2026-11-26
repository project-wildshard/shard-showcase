"""Two lightweight aligned W4b GLBs: fixed yoke and independently liftable bar."""
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/blender/showcase-studies'))
from common import clear_scene,export
src,out=map(Path,sys.argv[sys.argv.index('--')+1:])
out.mkdir(parents=True,exist_ok=True)
g=json.loads(src.read_text())['gate']
assert g=={'x':-26.14,'baseY':4.72,'z':196,'half':[.088,.49,1.83],'lift':1.78,'ticks':36}
clear_scene()

def mat(n,c,m):
    o=bpy.data.materials.new(n)
    o.use_nodes=True
    q=o.node_tree.nodes.get('Principled BSDF')
    q.inputs['Base Color'].default_value=(*c,1)
    q.inputs['Roughness'].default_value=.57
    q.inputs['Metallic'].default_value=m
    o.diffuse_color=(*c,1)
    return o

iron=mat('Graphite hoist steel',(.046,.070,.078),.65)
grey=mat('Burnished steel guide',(.21,.28,.29),.66)
orange=mat('Orange rolled enamel',(.78,.23,.028),.28)
grip=mat('Black impact rollers',(.023,.030,.032),0)
parts=[]

def box(n,p,d,m,r=0,turn=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object
    o.name=n
    o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(m)
    if r:
        q=o.modifiers.new('Machined edge','BEVEL')
        q.width=r
        q.segments=1
        bpy.ops.object.modifier_apply(modifier=q.name)
    o.rotation_euler.x=turn
    parts.append(o)

def finish(name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join()
    actor=bpy.context.object
    actor.name=name
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    assert actor.location.length<1e-8
    export([actor],out/(name+'.glb'))
    bpy.data.objects.remove(actor,do_unlink=True)
    parts.clear()

# X along ramp, local Y across in Blender, local Z vertical.
for side in (-1,1):
    y=side*1.947
    box('Bolted shoe',(0,y,-.69),(.49,.305,.12),iron,.015)
    box('Hoist leg',(0,y,.78),(.306,.191,2.86),iron,.021)
    box('Guide strip',(.015,y-side*.084,.79),(.209,.042,2.72),grey,.008)
    box('Upper winch casing',(0,y,2.11),(.49,.29,.42),orange,.034)
    for x in (-.13,.13):
        for v in (-.103,.103):
            box('Anchor bolt',(x,y+v,-.618),(.047,.047,.024),grey,.006)
box('Upper header',(0,0,2.448),(.280,4.15,.151),iron,.017)
box('Top cover',(0,0,2.535),(.338,4.235,.058),grey,.010)
finish('w4b-ball-gate-yoke')

# Occupies a bounded rectangular contact envelope for the local fixture.
box('Boxed shutter',(0,0,0),(.136,3.659,.98),iron,0)
for side in (-1,1):
    x=side*.074
    for i in range(12):
        y=(i-5.5)*.27
        box('Slashed hazard enamel',(x,y,.025),(.025,.110,.64),orange,.004,side*.43)
    for z in (-.402,.402):
        box('Replaceable guide lip',(x,0,z),(.027,3.61,.050),grey,.005)
for sign in (-1,1):
    for z in (-.318,.318):
        box('Roller key',(0,sign*1.777,z),(.174,.091,.124),grip,.008)
finish('w4b-ball-gate-bar')

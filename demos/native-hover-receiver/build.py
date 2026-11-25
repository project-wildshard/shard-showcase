"""Build the reversible D7 high-kicker receiver in the exact original Blender scene."""
import json
from math import degrees, atan
from pathlib import Path
import sys

import bpy
from mathutils import Vector

out=Path(sys.argv[sys.argv.index("--")+1]).resolve()
out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
x0,x1,x2=-167.39,-184.5,-201.0
y0,y1=4.798,.0319
z0=154.0
half=2.3
pivot=Vector((x0,-z0,0))
donors=tuple(o for o in scene.objects if o.type=="MESH")
bounds={}
for ob in donors:
    xs,ys,zs=zip(*(ob.matrix_world@Vector(c) for c in ob.bound_box))
    if max(xs)<x2 or min(xs)>x0 or max(ys)<-z0-half or min(ys)>-z0+half: continue
    bounds[ob.name]=[round(v,6) for v in (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))]
assert all(name.startswith(("HOVER | ramp 4.8 ","HOVER | zone paving","HOVER | ground extension")) for name in bounds), bounds
wall=frozenset(ob for ob in donors if ob.name.startswith("HOVER | launch wall east"))
assert wall
wall_gap=x2-max((o.matrix_world@Vector(c)).x for o in wall for c in o.bound_box)
assert wall_gap>5.8

segments=24
knots=[(x0,y0),(x1,y0)] + [(x1+(x2-x1)*t,y1+(y0-y1)*(1-3*t*t+2*t*t*t)) for t in (i/segments for i in range(1,segments+1))]
def height(x):
    if x>=x1:return y0
    for (xa,ya),(xb,yb) in zip(knots[1:-1],knots[2:]):
        if x>=xb:return ya+(yb-ya)*(x-xa)/(xb-xa)
    return y1

def material(name,rgb,metal=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    n=m.node_tree.nodes.get("Principled BSDF")
    n.inputs["Base Color"].default_value=(*rgb,1)
    n.inputs["Metallic"].default_value=metal
    n.inputs["Roughness"].default_value=.64
    return m

grip=material("Receiver | graphite rubber ripple",(.063,.082,.085),.12)
hold=material("Receiver | rollout warm wear",(.12,.125,.115),.08)
edge=material("Receiver | verdigris painted boundary",(.038,.40,.38),.17)
frame=material("Receiver | blackened steel stringers",(.045,.07,.081),.65)
accent=material("Receiver | fired orange crib brackets",(.42,.125,.038),.35)
under=material("Receiver | dark pressed deck sides",(.074,.107,.113),.40)
parts=[]
def obj(name,vs,faces,mats):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([Vector(v)-pivot for v in vs],[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    scene.collection.objects.link(ob);ob.location=pivot
    for m in mats:mesh.materials.append(m)
    parts.append(ob)
    return ob

# Co-planar material stripes, no raised geometry in the riding surface.
widths=(-half,-half+.13,-half+.23,half-.23,half-.13,half)
stride=len(widths)
top=obj("D7 Receiver Riding Surface",
    [(x,-z0+width,y) for x,y in knots for width in widths],
    [(i*stride+j,i*stride+j+1,(i+1)*stride+j+1,(i+1)*stride+j)
     for i in range(len(knots)-1) for j in range(stride-1)], [grip,hold,edge])
for p in top.data.polygons:
    row,col=divmod(p.index,stride-1)
    p.material_index=2 if col in (1,3) else (1 if row and row%5 in (0,1) else 0)
# 140 mm rolled edge and a single thin fascia per side, visual only.
for side in (-1,1):
    ob=obj(f"D7 Receiver rolled edge {side:+}",
           [(x,-z0+side*half,max(.002,y-d)) for x,y in knots for d in (0,.14)],
           [(2*i,2*i+1,2*i+3,2*i+2)[::side] for i in range(len(knots)-1)], [under])

def beam(a,b,wide,tall,name,m):
    p,q=Vector(a),Vector(b)
    d=(q-p).normalized(); sideways=d.cross(Vector((0,0,1)))
    if sideways.length<1e-5:sideways=Vector((0,1,0))
    sideways.normalize(); up=sideways.cross(d).normalized()
    vs=[end+sideways*(s*wide/2)+up*(t*tall/2) for end in (p,q) for s,t in ((-1,-1),(1,-1),(1,1),(-1,1))]
    return obj(name,vs,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)], [m])

supports=[-168.35,-172.4,-176.5,-180.6,-184.5,-188.55,-192.55,-196.5]
for i,x in enumerate(supports):
    y=height(x)-.24
    for s in (-1,1):
        z=-z0+s*1.89
        beam((x,z,.09),(x,z,y),.18,.22,"D7 Receiver steel leg",frame)
        beam((x-.37,z,.09),(x+.37,z,.09),.39,.11,"D7 Receiver low footing",under)
        if i+1<len(supports):
            nx=supports[i+1]
            # Constant-section diagonals cross each bay below the playable surface.
            beam((x,z,.25),(nx,z,height(nx)-.26),.10,.14,"D7 Receiver truss diagonal",accent)
    beam((x,-z0-2.08,y),(x,-z0+2.08,y),.22,.235,"D7 Receiver crosshead",frame)

assert all(p.normal.z>0 for p in top.data.polygons)
compact=[top]
for m,group in [(m,[p for p in parts if p is not top and p.data.materials[0] == m]) for m in (frame,accent,under)]:
    bpy.ops.object.select_all(action="DESELECT")
    for p in group:p.select_set(True)
    bpy.context.view_layer.objects.active=group[0]
    bpy.ops.object.join()
    group[0].name="D7 Receiver | "+m.name.split(" | ")[1]
    compact.append(group[0])
parts=compact
bpy.ops.object.select_all(action="DESELECT")
for p in parts:
    p.location=(0,0,0)
    p.select_set(True)
bpy.context.view_layer.objects.active=top
path=out/"w5a-high-kicker-receiver.glb"
bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",use_selection=True,export_animations=False)
new=list(parts)
bpy.ops.import_scene.gltf(filepath=str(path))
meshes=[p for p in scene.objects if p.type=="MESH" and p not in donors and p not in new]
assert len(meshes)==4
for p in meshes:p.location+=pivot
bpy.context.view_layer.update()
top2,= (p for p in meshes if p.name.startswith("D7 Receiver Riding Surface"))
v=[top2.matrix_world@p.co for p in top2.data.vertices]
top2.data.calc_loop_triangles()
tri=[i for t in top2.data.loop_triangles for i in t.vertices]
assert len(tri)==6*(len(knots)-1)*(stride-1)
coords=[round(n,7) for p in v for n in (p.x,p.z,-p.y)]
assert abs(min(coords[::3])-x2)<2e-5 and abs(max(coords[::3])-x0)<2e-5
assert max(coords[1::3])<4.8 and abs(min(coords[1::3])-y1)<1e-6
assert min(coords[2::3])>151.69 and max(coords[2::3])<156.31
slope=max(abs((yb-ya)/(xb-xa)) for (xa,ya),(xb,yb) in zip(knots,knots[1:]))
(out/"receiver.json").write_text(json.dumps(dict(name=top2.name,vertices=coords,triangles=tri,
  fit=dict(x=x0,flat_end=x1,rollout_end=x2,span=2*half,lane_z=z0,crest_overlap_m=.01,
    wall_clearance_m=round(wall_gap,5),max_grade_degrees=round(degrees(atan(slope)),4),
    touching_donor_bounds=bounds,bytes=path.stat().st_size)))+"\n")
for p in new:bpy.data.objects.remove(p,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/"receiver-review.blend"))

"""G2 level passage and southwest entrance sector; no replacement of donor art."""
import json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent.parent/"scripts/blender/showcase-studies"))
from common import clear_scene,export
out=Path(sys.argv[sys.argv.index("--")+1]);out.mkdir(parents=True,exist_ok=True)
clear_scene()
P=(110.,214.)
center=Vector((146.,186.))
mouth=Vector((115.,214.))
axis=(center-mouth).normalized()
cross=Vector((-axis.y,axis.x))
seam=[(Vector(P),Vector((0,1)),4.,0.),(mouth,Vector((0,1)),4.,.05)]
for r,half in [(38,4.05),(34,4.22),(28,4.78),(24,5.45),(20,6.05)]:
    seam.append((center-axis*r,cross,half,.05))

def mat(name,rgb,met,rough,emit=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
    n=m.node_tree.nodes["Principled BSDF"]
    for k,v in [("Base Color",(*rgb,1)),("Metallic",met),("Roughness",rough),("Emission Color",(*rgb,1)),("Emission Strength",emit)]:
        n.inputs[k].default_value=v
    return m
M=[mat("01 Warm durable concrete",(.36,.306,.235),.08,.82),
   mat("02 Weathered charcoal steel",(.079,.098,.103),.48,.57),
   mat("03 Industrial oxide enamel",(.57,.194,.051),.42,.54),
   mat("04 Dull gold traffic strips",(.61,.417,.14),.20,.61),
   mat("05 Warm ceramic lens",(1,.46,.072),.12,.38,1.5)]
groups={}
F=[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
# The points below go clockwise in map coordinates, counter-clockwise
# after conversion to Blender's north-positive convention.
def build(name,p,bot,top,m):
    v,f,s=groups.setdefault(name,([],[],[]));i=len(v)
    if not isinstance(top,(list,tuple)):top=[top]*len(p)
    v.extend((a-P[0],P[1]-b,h) for H in (top,[bot]*len(p)) for (a,b),h in zip(p,H))
    f.extend(tuple(i+k for k in q) for q in F);s.extend([m]*6)
def road(a,b):
    o,q,w,ht=a
    oo,qq,ww,hh=b
    build("01 G2 level paving",[o+q*w,oo+qq*ww,oo-qq*ww,o-q*w],-.34,[ht,hh,hh,ht],0)
for a,b in zip(seam,seam[1:]):road(a,b)
def box(name,x,z,y0,y1,w,d,m,ux=Vector((1,0)),uz=Vector((0,1))):
    p=Vector((x,z))
    build(name,[p-ux*w/2+uz*d/2,p+ux*w/2+uz*d/2,
                p+ux*w/2-uz*d/2,p-ux*w/2-uz*d/2],y0,y1,m)
for zz in (210.25,217.75):
    box("02 Entry parapets",112.5,zz,0,3.8,5,.5,1)
    box("02 Entry parapets",112.5,zz,3.8,4,5,.53,2)
    box("02 Entry parapets",114.78,zz,0,4.12,.44,.83,2)
    box("90 Reference lenses",114.54,zz,2.8,2.92,.165,.38,4)
for r in (28,31.5,35,39):
    c=center-axis*r
    for sign in (-1,1):
        p=c+cross*sign*2.85
        box("90 Traffic inlays",p.x,p.y,.051,.072,1.28,.12,3,axis,cross)
# Preserve the Round 5 terrace levels either side of the .24-rad opening.
# Short neighbouring sectors are not the remainder of Court 3.
t=math.atan2(mouth.y-center.y,mouth.x-center.x)
def polar(r,a):return center+Vector((math.cos(a),math.sin(a)))*r
for lo,hi in [(t-.53,t-.242),(t+.242,t+.53)]:
    for k in range(5):
        a=lo+(hi-lo)*k/5;b=lo+(hi-lo)*(k+1)/5
        for r0,r1,height,m in [(28,34,1.5,0),(34,40,3,0),(40,42,6,1)]:
            points=[polar(r1,b),polar(r1,a),polar(r0,a),polar(r0,b)]
            build("03 Entry terrace sections",points,-.34,height,m)
            if r0==40:
                build("03 Entry terrace sections",points,5.82,6.08,2)
parts=[]
for name,(v,f,s) in groups.items():
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(v,[],f)
    for m in M:mesh.materials.append(m)
    for face,i in zip(mesh.polygons,s):face.material_index=i
    obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);parts.append(obj)
# Orient normals consistently for the closed convex strips and wall blocks.
bpy.ops.object.select_all(action="DESELECT")
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
export(parts,out/"e11c-g2-c3-threshold.glb")
(out/"geometry-plan.json").write_text(json.dumps({"pivot":[110,0,214],"axis":list(axis),
    "seam":[[list(p),list(h),w,z] for p,h,w,z in seam],"radial_limit":[20,42],
    "adjacent_sectors_halfangle_rad":[.242,.53]},indent=2)+"\n")

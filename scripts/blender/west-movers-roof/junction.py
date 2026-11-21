import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
P=OUT;P.mkdir(parents=True,exist_ok=True);S=bpy.context.scene
removed=[]
for o in list(S.objects):
 if 'MOVERS | Station6 west return rail' in o.name and abs(o.location.y-102.6)<.1:removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
base={o.name for o in S.objects if o.type=='MESH'}
def mat(n,c,metal=0):
 m=bpy.data.materials.new('JUNCTION '+n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.72;return m
M=[mat('cedar',(.32,.104,.028)),mat('cedar amber',(.41,.165,.045)),mat('hemp',(.60,.406,.209)),mat('tank teal',(.13,.28,.29),.35),mat('steel bands',(.065,.105,.11),.5),mat('roof',(.36,.43,.40)),mat('warm edge',(.65,.46,.23),.3)]
def box(n,pos,dim,ma,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name='JUNCTION | '+n;o.dimensions=dim;o.rotation_euler.z=rot;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[ma]);return o
def rod(n,a,b,r,ma,verts=8):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();v=d.cross(Vector((0,0,1)))
 if v.length<.001:v=d.cross(Vector((0,1,0)))
 v.normalize();w=d.cross(v);vs=[tuple(p+r*(math.cos(i*math.tau/verts)*v+math.sin(i*math.tau/verts)*w)) for p in [a,b] for i in range(verts)];fs=[tuple(range(verts-1,-1,-1)),tuple(range(verts,2*verts))]+[(i,(i+1)%verts,(i+1)%verts+verts,i+verts) for i in range(verts)];mesh=bpy.data.meshes.new(n);mesh.from_pydata(vs,[],fs);mesh.materials.append(M[ma]);o=bpy.data.objects.new('JUNCTION | '+n,mesh);S.collection.objects.link(o);return o
def cyl(n,pos,r,h,ma):
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=r,depth=h,location=pos);o=bpy.context.object;o.name='JUNCTION | '+n;o.data.materials.append(M[ma]);return o
def ring(n,z,r,thick,ma):
 for i in range(96):
  a=i*math.tau/96;b=(i+1)*math.tau/96;rod(n,(-206+r*math.cos(a),104+r*math.sin(a),z),(-206+r*math.cos(b),104+r*math.sin(b),z),thick,ma,6)
# Source-defined landmark envelope R16, roof top18; all architectural vocabulary inferred.
cyl('landmark tank shell',(-206,104,8.85),15.96,17.7,3);cyl('continuous landable roof',(-206,104,17.85),16,.3,5)
for z in [.35,5.8,11.6,17.65]:ring('tank hoop band',z,15.98,.12,4)
for i in range(32):
 a=i*math.tau/32;rod('vertical shell seam',(-206+15.97*math.cos(a),104+15.97*math.sin(a),.5),(-206+15.97*math.cos(a),104+15.97*math.sin(a),17.4),.055,4,6)
# Roof perimeter guard except east bridge entrance, no gameplay fit claim.
for i in range(48):
 a=i*math.tau/48
 if min(a,math.tau-a)<.13:continue
 x=-206+15.65*math.cos(a);y=104+15.65*math.sin(a);rod('roof perimeter post',(x,y,18),(x,y,19.1),.065,4)
for i in range(96):
 a=i*math.tau/96;b=(i+1)*math.tau/96
 if a<.13 or b>math.tau-.13:continue
 for z in [18.5,19.1]:rod('roof rail',(-206+15.65*math.cos(a),104+15.65*math.sin(a),z),(-206+15.65*math.cos(b),104+15.65*math.sin(b),z),.045,4,6)
A=Vector((-168,103,18));B=Vector((-190,104,18));D=B-A;L=D.length;U=D/L;V=Vector((-U.y,U.x,0));yaw=math.atan2(U.y,U.x);sag=.65
# Deck planks constructed at native thickness, not uniformly scaled donor.
N=54
for i in range(N):
 t=(i+.5)/N;p=A+D*t;p.z-=4*sag*t*(1-t)+.075
 box('individual cedar plank',p,(L/N-.025,1.6,.15),i%2,yaw)
for p,n in [(A,'deck'),(B,'roof')]:
 box(n+' flush threshold',p-Vector((0,0,.058)),(.65,1.6,.14),1,yaw)
 for side in [-1,1]:rod(n+' portal post',p+V*side*.94,p+V*side*.94+Vector((0,0,1.25)),.11,0)
for side in [-1,1]:
 for k in range(N):
  t=k/N;q=(k+1)/N;a=A+D*t+V*side*.87;b=A+D*q+V*side*.87
  a.z+=1.08-4*sag*t*(1-t);b.z+=1.08-4*sag*q*(1-q);rod('continuous hand rope',a,b,.045,2)
  if k%3==0:rod('rope hanger',a,a-Vector((0,0,1.06)),.025,2,6)
# Shared roof hook is a labelled static proxy, no grapple configuration or extra catalogue id.
rod('roof hook pedestal',(-206,104,18),(-206,104,19.4),.12,6)
bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=6,location=(-206,104,19.7),major_radius=.42,minor_radius=.065,rotation=(math.pi/2,0,0));bpy.context.object.name='JUNCTION | static hook proxy';bpy.context.object.data.materials.append(M[6])
new=[o for o in S.objects if o.type=='MESH' and o.name not in base];tri=sum(len(o.data.polygons)*2 for o in new)
(P/'manifest.json').write_text(json.dumps({'source_anchors_map':[[-168,18,-103],[-190,18,-104]],'span_m':L,'visual_width_m':1.6,'inferred_sag_m':sag,'tank_source':{'center_map_xz':[-206,-104],'radius_m':16,'roof_y_m':18},'removed_baseline_meshes':removed,'new_meshes':len(new),'status':'static art-only WIP; no physics, construction or gameplay qualification','vocabulary':'WSC-PROP-048 cedar/hemp palette; constructed native planks, no scaled asset; tank is source-scale landmark not enlarged prop'},indent=2))

# Reviewed build already includes correction in p.z-.058 threshold center.
bpy.ops.object.select_all(action='DESELECT')
for o in S.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(P/'west-shared-roof-WIP.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'west-shared-roof-editable.blend'))

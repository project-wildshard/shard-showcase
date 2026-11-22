"""Build both reviewed static Crate Mite variants from editable geometry."""
from pathlib import Path
import math,bpy,sys
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import output_directory,clear_scene,export

def build(phone, *, far=False, yard=False):
    clear_scene()
    bpy.data.orphans_purge(do_recursive=True)
    s=bpy.context.scene
    C=bpy.data.collections.new('Crate Mite | static silhouette test');s.collection.children.link(C)
    parts=[]
    def mat(n,c,met=0.,rough=.55,em=None):
     m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1);b=m.node_tree.nodes.get('Principled BSDF')
     b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=met;b.inputs['Roughness'].default_value=rough
     if em:b.inputs['Emission Color'].default_value=(*em[0],1);b.inputs['Emission Strength'].default_value=em[1]
     return m
    lava=mat('Mite | fired orange powder coat',(.53,.18,.041),.30,.52)
    edge=mat('Mite | warm chamfer',(.72,.36,.108),.29,.48)
    lock=mat('Mite | charcoal reinforced polymer',(.045,.061,.064),.27,.54)
    cast=mat('Mite | bevel grey machined alloy',(.15,.204,.203),.63,.43)
    rubber=mat('Mite | compression tread',(.023,.028,.026),.12,.7)
    eye=mat('Mite | day cyan lens',(.025,.59,.68),.20,.28,((.014,.93,1.),1.7))
    eye_matte=mat('Mite | unlit lens ring',(.025,.24,.245),.21,.45)
    def mesh(name,verts,faces,materials,indices=None):
     d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
     o=bpy.data.objects.new(name,d);C.objects.link(o);parts.append(o)
     for m in materials:d.materials.append(m)
     if indices:
      for f,i in zip(d.polygons,indices):f.material_index=i
     return o
    def box(name,x,y,z,w,d,h,c,m,b=None,rx=0,ry=0):
     X,Y=w/2,d/2;c=min(c,X*.4,Y*.4)
     pts=[(-X+c,-Y),(X-c,-Y),(X,-Y+c),(X,Y-c),(X-c,Y),(-X+c,Y),(-X,Y-c),(-X,-Y+c)] if c else [(-X,-Y),(X,-Y),(X,Y),(-X,Y)]
     n=len(pts);vs=[(a,b,sz*h/2) for sz in (-1,1) for a,b in pts]
     fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
     o=mesh(name,vs,fs,(m,b) if b else (m,),([0,0]+[i%2 for i in range(n)]) if b else None)
     o.location=(x,y,z);o.rotation_euler=(rx,ry,0);return o
    def ring(name,center,profile,n,mats,side_materials,cap=None):
     verts=[(r*math.cos(a*math.tau/n+math.pi/n),dy,r*math.sin(a*math.tau/n+math.pi/n)) for r,dy in profile for a in range(n)]
     faces=[];idx=[]
     for j,m in enumerate(side_materials):
      for i in range(n):
       faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i));idx.append(m)
     if cap is not None:faces.append(tuple(range((len(profile)-1)*n,len(profile)*n)));idx.append(cap)
     o=mesh(name,verts,faces,mats,idx);o.location=center;return o
    assert not (far and yard)
    if far:
     # Preserve the chamfered crate and its lid seam. Fuse each collar, strut
     # and foot into a single wedge, with no textures or new rig joints.
     box('Single canted-wall crate shell',0,0,.361,.56,.51,.27,.049,lava,edge)
     box('Orange clamp lid',0,0,.535,.60,.55,.123,.061,lava,cast)
     box('Rigid charcoal bumper',0,0,.239,.568,.517,.073,0,lock)
     for sx in (-1,1):
      for sy in (-1,1):
       x=sx*.238;y=sy*.172
       # The lower rectangle is wider and offset out from the upper joint.
       # Build in local space so the skinner still deduces the four leg slots.
       v=[(sx*.061+dx*.075,sy*.021+dy*.073,-.226)
          for dx,dy in ((-1,-1),(1,-1),(1,1),(-1,1))]
       v += [(dx*.055,dy*.058,.019)
             for dx,dy in ((-1,-1),(1,-1),(1,1),(-1,1))]
       f=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
       o=mesh('Angled pressure leg and foot',v,f,(cast,rubber),[1,0,0,1 if sx>0 else 0,0,1 if sx<0 else 0])
       o.location=(x,y,.23)
     ring('Sealed octagonal eye stack',(0,-.255,.365),
          [(.112,0),(.081,-.032)],8,(eye_matte,eye),[0],1)
     bpy.context.view_layer.update()
     assert sum(len(f.vertices)-2 for o in parts for f in o.data.polygons)==138
     return parts
    # One 0.6m crate; mechanical gussets are trim geometry rather than texture.
    box('Single canted-wall crate shell',0,0,.361,.56,.51,.27,.049,lava,edge)
    box('Orange clamp lid',0,0,.543,.60,.55,.101,.061,lava,cast if phone else edge)
    box('Rigid charcoal bumper',0,0,.239,.58,.533,.073,.061,lock,cast)
    box('Lid edge seam',0,0,.482,.58,.527,.033,.027,lock)
    for x in (-.159,.159):
     box('Flat restraint strap',x,0,.596,.061,.455,.011,0,lock)
     box('Recessed nose latch',x,-.267,.486,.050,.026,.052,0,cast)
    for sx in (-1,1):
     for sy in (-1,1):
      x=sx*.238;y=sy*.172
      box('Four short joint collars',x,y,.203,.127,.126,.099,0,cast,ry=sx*.20)
      box('Angled pressure leg',x+sx*.033,y,.126,.096,.118,.161,0,cast if phone else lock,lock if phone else None,rx=sy*.15,ry=-sx*.26)
      if phone:box('Short single-piece foot',x+sx*.065,y+sy*.021,.039,.152,.147,.077,0,rubber,edge)
      else:box('Chamfered industrial foot',x+sx*.065,y+sy*.021,.039,.157,.151,.077,.021,rubber,cast)
    if yard:
     steel=mat('Mite | scuffed steel pins',(.35,.402,.377),.76,.36)
     badge=mat('Mite | pale yard enamel',(.74,.65,.425),.2,.52)
     # Browser hero: details remain rigidly weighted to the same seven bones.
     # Preserve the silhouette and gameplay bounds of the validated native rig.
     for sx in (-1,1):
      for sy in (-1,1):
       x=sx*.238;y=sy*.172
       box('Orange clamp corner plate',sx*.244,sy*.219,.522,.117,.10,.093,.018,cast)
       box('Orange clamp raised corner',sx*.248,sy*.221,.570,.073,.071,.018,.008,steel)
       joint=ring('Four short axle and cap',(x+sx*.041,y,.201),
        [(.048,.011),(.052,0),(.049,-.023),(.028,-.030)],8,(lock,cast,steel),[0,1,2],2)
       joint.rotation_euler.z=sx*math.pi/2
       knee=ring('Angled pressure knee pin',(x+sx*.058,y+sy*.036,.117),
        [(.032,0),(.037,-.013),(.033,-.028),(.021,-.033)],8,(lock,edge,steel),[0,1,2],2)
       if sy>0:knee.rotation_euler.z=math.pi
       box('Angled pressure outer armor',x+sx*.055,y,.104,.086,.121,.087,.011,lava,cast,rx=sy*.16,ry=-sx*.21)
       box('Short single-piece steel toe',x+sx*.066,y+sy*.067,.052,.126,.058,.044,.009,edge,cast)
     for x in (-.178,.178):
      box('Recessed nose armor saddle',x,-.270,.427,.101,.032,.093,.013,cast,lock)
      for z in (.395,.456):
       ring('Recessed nose socket screw',(x,-.290,z),[(.012,0),(.013,-.006),(.009,-.009)],6,(lock,steel),[0,1],1)
     box('Rigid body front grille',0,-.280,.264,.295,.025,.053,.013,cast,lock)
     for i in range(3):
      box('Rigid body enamel stitch',-.080+.031*i,-.295,.264,.015,.005,.023,.002,badge,ry=.46)
     ring('Sealed octagonal eye guard',(0,-.271,.365),[(.121,0),(.108,-.022),(.093,-.028)],16,(cast,steel),[0,1])
     for n in range(8):
      a=n*math.tau/8
      box('Sealed octagonal radial lug',.107*math.cos(a),-.297,.365+.107*math.sin(a),.013,.010,.010,0,steel,ry=-a)
    ring('Sealed octagonal eye stack',(0,-.255,.365),[(.119,0),(.111,-.021),(.087,-.029),(.072,-.034)],16 if yard else 12 if phone else 8,(lock,cast,eye_matte,eye),[0,1,2],3)
    bpy.context.view_layer.update()
    tris=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in parts)
    low=min((o.matrix_world@Vector(v)).z for o in parts for v in o.bound_box)
    high=max((o.matrix_world@Vector(v)).z for o in parts for v in o.bound_box)
    print('MITE_TRIANGLES',tris,'MINMAXZ',low,high,flush=True)
    assert (1100<=tris<=2000 if yard else tris==(386 if phone else 422)) and abs(high-low-.6)<.025
    return parts

if __name__ == "__main__":
    out=output_directory()
    for phone in (False,True):
        variant="-phone" if phone else ""
        export(build(phone),out/f"wsc-actor-001-crate-mite{variant}-study.glb")

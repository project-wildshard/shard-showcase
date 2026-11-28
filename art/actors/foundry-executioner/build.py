"""Rebuild the Foundry Executioner silhouette study. Blender 4.3+; metres."""
import bpy, bmesh, sys
from math import sin, cos, pi
from mathutils import Vector
from pathlib import Path

out = Path(sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else '/tmp/executioner')
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
MODEL = bpy.data.collections.new('Executioner | Editable Form')
scene.collection.children.link(MODEL)
def material(name, rgb, metal=0, rough=.55):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    return m
fabric=material('01 · Fireproof black wool',(.039,.048,.049),.0,.83)
iron=material('02 · Blue-black quenched steel',(.109,.142,.149),.82,.32)
oxide=material('03 · Old copper patina',(.21,.087,.044),.72,.40)
edge=material('04 · Exposed hammered edges',(.245,.258,.24),.87,.27)
leather=material('05 · Cured oxblood hide',(.063,.031,.020),.04,.72)
apron=material('05b · Leather apron',(.141,.064,.039),.04,.76)
bone=material('06 · Burned refractory ceramic',(.57,.47,.32),.12,.49)
def grain(mat, strength, distance, scale, low, high):
    tree=mat.node_tree; p=tree.nodes.get('Principled BSDF')
    coords=tree.nodes.new('ShaderNodeTexCoord')
    physical=tree.nodes.new('ShaderNodeTexNoise')
    physical.inputs['Scale'].default_value=scale
    physical.inputs['Detail'].default_value=3.2
    tree.links.new(coords.outputs['Object'],physical.inputs['Vector'])
    bump=tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=distance
    tree.links.new(physical.outputs['Fac'],bump.inputs['Height'])
    macro=tree.nodes.new('ShaderNodeTexNoise');macro.inputs['Scale'].default_value=18
    macro.inputs['Detail'].default_value=4
    tree.links.new(coords.outputs['Object'],macro.inputs['Vector'])
    color=tree.nodes.new('ShaderNodeValToRGB')
    for el, rgb in zip(color.color_ramp.elements,[low,high]):el.color=(*rgb,1)
    tree.links.new(macro.outputs['Fac'],color.inputs[0])
    tree.links.new(color.outputs['Color'],p.inputs['Base Color'])
    tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
grain(fabric,.26,.002,315,(.009,.011,.012),(.072,.069,.055))
grain(iron,.35,.005,83,(.045,.054,.057),(.19,.205,.205))
grain(bone,.23,.0021,121,(.25,.175,.113),(.72,.64,.49))
grain(apron,.32,.004,214,(.042,.015,.009),(.24,.107,.058))
grain(leather,.25,.003,193,(.021,.012,.008),(.11,.066,.046))
shale=material('07 · Set / graphite',(.038,.044,.046),.05,.8)
clay=material('Silhouette check · neutral',(.34,.34,.34),0,.64)
def surface(name, verts, faces, mat, bevel=0, sub=0, thickness=0):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    obj=bpy.data.objects.new(name,data);MODEL.objects.link(obj);data.materials.append(mat)
    for p in data.polygons:p.use_smooth=True
    if sub:
        mod=obj.modifiers.new('Curvature / quad subdivision','SUBSURF');mod.levels=sub
    if thickness:
        mod=obj.modifiers.new('Forged plate thickness','SOLIDIFY');mod.thickness=thickness
    if bevel:
        mod=obj.modifiers.new('Caught light / rolled edge','BEVEL');mod.width=bevel;mod.segments=3
    return obj

def loft(name, rings, mat, a=None, b=None, count=24, sub=2, form=None):
    """Rings are (height, halfwidth, halfdepth, x offset, y offset)."""
    if a is not None:
        a,b=Vector(a),Vector(b); v=(b-a).normalized()
        u=(Vector((0,1,0)).cross(v)).normalized();w=v.cross(u)
        length=(b-a).length
    verts=[];faces=[]
    for i,(z,xr,yr,x,y) in enumerate(rings):
        for j in range(count):
            t=2*pi*j/count
            u0=x+xr*cos(t); v0=y+yr*sin(t)
            if form:u0,v0=form(z,t,u0,v0)
            pt=(u0,v0,z) if a is None else a+v*(z*length)+u*u0+w*v0
            verts.append(pt)
    for i in range(len(rings)-1):
        for j in range(count):
            k=i*count+j;l=i*count+(j+1)%count
            faces.append((k,l,l+count,k+count))
    faces+=[tuple(reversed(range(count))),tuple(range(len(verts)-count,len(verts)))]
    return surface(name,verts,faces,mat,sub=sub)

def limb(name,a,b,radii,mat=fabric,offset=0):
    return loft(name,[(z,x,y,0,offset) for (z,x,y) in radii],mat,a,b)

def shell(name,a,b,rows,mat,span=1.6):
    """Open, curved armor shell along the limb axis; weighted silhouette at each meridian."""
    a,b=Vector(a),Vector(b);axis=(b-a).normalized()
    u=Vector((0,1,0)).cross(axis).normalized();v=axis.cross(u)
    verts=[];faces=[];n=23
    for z,rx,ry,sweep,notch in rows:
        for j in range(n):
            t=(j/(n-1)-.5)*2
            ang=t*span+sweep
            bulge=1+.028*cos(ang*3)
            p=a+(b-a)*(z+notch*(1-t*t))+u*(rx*sin(ang)*bulge)-v*(ry*cos(ang)*bulge)
            verts.append(p)
    for i in range(len(rows)-1):
        for j in range(n-1):
            k=i*n+j;faces.append((k,k+1,k+n+1,k+n))
    return surface(name,verts,faces,mat,bevel=.0016,sub=1,thickness=.007)

def line(name, pts, radius, mat):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12
    s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
    for bp,p in zip(s.bezier_points,pts):bp.co=p;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
    c.bevel_depth=radius;c.bevel_resolution=3
    ob=bpy.data.objects.new(name,c);MODEL.objects.link(ob);c.materials.append(mat)
    return ob

loft('Quilted suit | rib cage / pelvis',[
    (.91,.076,.060,0,.025),(.96,.147,.089,0,.023),(1.05,.169,.102,0,.016),
    (1.12,.143,.091,0,.01),(1.19,.138,.084,0,.013),(1.25,.149,.099,0,.012),
    (1.35,.176,.108,.008,.009),(1.44,.197,.116,.012,.005),(1.51,.221,.110,.015,.008),
    (1.57,.205,.090,.014,.013),(1.62,.151,.067,.01,.015),(1.65,.062,.051,.01,.01)],fabric)
loft('Gorget underlayer',[(1.57,.093,.071,.012,.012),(1.64,.075,.067,.01,.003),
    (1.69,.058,.055,.012,-.013),(1.73,.055,.056,.012,-.026)],leather)
loft('Helmet bowl | swept cranial profile',[
    (1.678,.035,.038,.015,-.057),(1.70,.068,.069,.013,-.046),
    (1.76,.082,.083,.013,-.028),(1.82,.091,.097,.013,-.009),
    (1.88,.090,.083,.013,-.001),(1.927,.066,.064,.013,.007),(1.945,.024,.028,.013,.011)],iron)
loft('Visor | recessed face socket',[
    (1.716,.034,.027,.013,-.068),(1.75,.055,.041,.013,-.075),
    (1.79,.069,.048,.013,-.071),(1.835,.075,.048,.013,-.061),(1.867,.062,.032,.013,-.057)],fabric)
shell('Porcelain visor | angular cheek plane',(.013,-.037,1.713),(.013,-.024,1.872),[
    (.03,.042,.073,0,-.08),(.18,.055,.088,0,-.015),(.42,.067,.099,0,.024),
    (.55,.071,.094,0,-.018)],bone,1.21)
line('Visor brow | continuous knife line',
     [(-.072,-.069,1.835),(-.046,-.106,1.821),(.013,-.134,1.818),(.071,-.101,1.827),(.098,-.059,1.845)],.005,edge)
line('Mask ridge',
     [(.013,-.092,1.706),(.013,-.124,1.741),(.013,-.139,1.773)],.0035,edge)
for s in (-1,1):
    line('Eye slit',[(.013+s*.021,-.121,1.808),(.013+s*.046,-.106,1.811),(.013+s*.066,-.088,1.817)],.002,oxide)

shell('Cuirass | compound curvature breastplate',(.006,.012,1.17),(.015,.015,1.575),[
    (.025,.131,.092,.03,.015),(.12,.143,.108,.025,.010),(.40,.170,.120,.018,.02),
    (.68,.198,.134,.01,.023),(.84,.222,.130,0,-.02),(.98,.174,.110,-.035,-.12)],iron,1.46)
line('Forged diagonal raised seam',[(-.168,-.064,1.56),(-.097,-.113,1.525),
     (.010,-.123,1.451),(.072,-.095,1.373),(.127,-.054,1.30)],.003,edge)
shell('Dorsal steel guard',(.006,.017,1.245),(.018,.017,1.585),[
    (0,.140,.096,pi,0),(.21,.156,.107,pi,0),(.65,.189,.116,pi,0),(.98,.164,.082,pi,-.07)],iron,1.21)
for i in range(3):
    z=1.08+i*.044
    shell('Overlapping waist lame %s'%i,(0,.009,z),(0,.010,z+.090),[
          (0,.148,.099,-.05,-.12),(.23,.155,.110,-.045,-.03),(.79,.144,.107,-.065,.05),
          (1,.133,.096,-.06,.04)],oxide if i==0 else iron,1.49)

upper=[(0,.087,.075),(.13,.099,.087),(.33,.091,.082),(.58,.079,.073),(.85,.053,.052),(1,.047,.052)]
lower=[(0,.047,.049),(.19,.068,.060),(.40,.071,.062),(.68,.053,.049),(.90,.036,.035),(1,.036,.036)]
thigh=[(0,.095,.096),(.15,.114,.109),(.37,.106,.108),(.65,.080,.082),(.88,.060,.061),(1,.056,.057)]
shin=[(0,.054,.055),(.16,.067,.064),(.38,.074,.068),(.69,.046,.050),(.91,.039,.044),(1,.040,.048)]
for side, shoulder, elbow, wrist, hip, knee, ankle in [
    ('R',(.205,.015,1.544),(.306,-.027,1.264),(.335,-.103,1.030),
         (.095,.014,1.006),(.130,-.072,.555),(.160,-.104,.090)),
    ('L',(-.186,.027,1.537),(-.293,.046,1.254),(-.326,-.009,1.016),
         (-.097,.023,1.009),(-.137,.040,.550),(-.195,.104,.091))]:
    limb('Arm '+side+' | deltoid / triceps',shoulder,elbow,upper)
    limb('Arm '+side+' | forearm tendons',elbow,wrist,lower)
    limb('Leg '+side+' | quadriceps / hamstrings',hip,knee,thigh)
    limb('Leg '+side+' | calf taper',knee,ankle,shin)
    if side=='R':
        shell('Right pauldron | drawn flange',elbow,shoulder,[
            (.57,.112,.101,.58,-.24),(.70,.125,.111,.57,-.17),(.89,.134,.121,.57,-.04),
            (1.13,.117,.111,.53,.14),(1.24,.052,.052,.43,.19)],iron,1.68)
        shell('Right rerebrace | heat band',elbow,shoulder,[
            (.42,.076,.070,.48,-.03),(.52,.093,.088,.48,-.05),(.73,.099,.092,.48,.00)],oxide,1.51)
    else:
        shell('Left fireproof shoulder guard',elbow,shoulder,[
            (.66,.096,.078,-.4,-.13),(.84,.105,.087,-.4,-.03),(1.03,.085,.073,-.4,.01)],leather,1.42)
    shell('Hand-shaped vambrace '+side,wrist,elbow,[
       (.03,.044,.049,0,.022),(.19,.053,.057,.02,.02),(.57,.073,.070,0,-.03),
       (.82,.075,.069,0,-.07),(.90,.061,.056,0,-.12)],iron,1.39)
    shell('Shin | tapered sabaton guard '+side,ankle,knee,[
       (.03,.048,.058,0,.046),(.16,.050,.059,0,.031),(.48,.069,.072,0,.02),
       (.84,.075,.069,0,-.045),(.93,.067,.057,0,-.04)],iron,1.37)
    shell('Rounded knee cop '+side,ankle,knee,[
       (.89,.067,.070,0,-.04),(.97,.082,.083,0,.00),(1.08,.077,.078,0,.05),
       (1.16,.052,.058,0,.06)],iron,1.49)
    shell('Hanging curved tasset '+side,knee,hip,[
       (.39,.076,.078,0,-.13),(.47,.087,.091,0,-.09),(.68,.108,.117,0,-.04),
       (.88,.115,.118,0,.005),(.955,.103,.109,0,.045)],leather,1.33)
    x,y,z=ankle
    loft('Boot '+side+' | toe and instep',[
      (.013,.063,.117,x,y-.056),(.025,.069,.122,x,y-.057),(.052,.068,.124,x,y-.056),
      (.078,.058,.099,x,y-.051),(.113,.049,.070,x,y-.016),(.151,.043,.044,x,y)],leather)
    wx,wy,wz=wrist
    a=(wx,wy-.016,wz-.093)
    limb('Glove cuff '+side,(wx,wy,wz-.022),(wx,wy+.010,wz+.039),
        [(0,.033,.034),(.12,.041,.042),(.82,.044,.048),(1,.042,.046)],leather)
    limb('Glove palm '+side,a,wrist,[(0,.034,.016),(.24,.040,.023),(.59,.041,.024),(1,.029,.027)],leather)
    sign=1 if side=='R' else -1
    for j in range(4):
        x=wx+(j-1.45)*.016; y=wy-.023; z=wz-.074
        limb('Glove digit '+side+str(j),(x-sign*.007,y-.017,z-(.066-.006*abs(j-1))),
             (x,y,z),[(0,.006,.006),(.20,.008,.009),(.53,.0088,.009),(.84,.009,.009),(1,.010,.009)],leather)
    limb('Opposing thumb '+side,(wx-sign*.048,wy-.024,wz-.065),(wx-sign*.025,wy-.002,wz-.022),
      [(0,.007,.008),(.23,.011,.011),(.68,.014,.014),(1,.015,.015)],leather)

# Open hood and wrapped cowl. The front opening traces the cheek and brow; it is not a sphere.
shell('Hood | pointed seam and face opening',(.013,.001,1.56),(.013,-.008,1.98),[
    (.00,.158,.086,pi,-.046),(.16,.145,.122,pi,-.014),(.33,.116,.137,pi,-.042),
    (.51,.112,.135,pi,-.025),(.70,.106,.161,pi,-.012),
    (.87,.078,.148,pi,.04),(.97,.037,.085,pi,.045),(1.0,.007,.040,pi,.02)],
    fabric,2.43)
shell('Neck cowl | rolled cloth',(.010,.007,1.52),(.013,-.012,1.70),[
    (.02,.181,.111,.02,-.10),(.15,.174,.127,.02,.04),(.42,.134,.101,-.02,-.07),
    (.55,.137,.106,-.06,.08),(.78,.098,.101,-.02,-.02),(.97,.096,.076,.03,.05)],fabric,1.79)
loft('Waist belt | hand cut heavy hide',[
    (1.107,.150,.101,0,.006),(1.113,.158,.110,0,.006),
    (1.151,.155,.112,0,.006),(1.156,.149,.102,0,.006)],leather,count=32,sub=1)

def drape(name, side, inside, outside, hem, center, mat, back=False):
    # Quad sheet in body space, with curved vertical folds that strengthen away from the belt.
    verts=[];faces=[];U=24;V=32
    for i in range(V):
        v=i/(V-1)
        for j in range(U):
            u=j/(U-1)
            x=side*((1-u)*inside+u*outside+(u-.28)*.047*v)
            length=hem + .065*sin(u*pi) - .08*u + .020*sin(u*7.8+side)
            z=1.128-v*length+(x*side)*.042
            y=-center + .10*(abs(x)/.265)**2
            y-=.046*sin(pi*v*.86)
            y+=(.008+.026*v)*sin(u*12.7+v*2.9+side*.8)
            if side==1 and not back:y-=.045*sin(pi*v*.82)*(u**.55)
            y+=.013*cos(v*15.5+u*4.3)*(1-v)
            if back:y=-y+.014
            verts.append((x,y,z))
    for i in range(V-1):
        for j in range(U-1):
            k=i*U+j;faces.append((k,k+1,k+1+U,k+U))
    return surface(name,verts,faces,mat,sub=1,thickness=.004,bevel=.0008)

drape('Front leather apron | overlapped left tail',-1,.018,.218,.71,.153,apron)
drape('Front leather apron | longer right tail',1,-.029,.197,.78,.163,apron)
drape('Rear split mantle | left',-1,.018,.229,.60,.141,fabric,True)
drape('Rear split mantle | right',1,.018,.226,.66,.143,fabric,True)
line('Apron suspension strap left',[(-.135,-.082,1.131),(-.109,-.123,1.056),(-.105,-.142,.961)],.009,leather)
line('Apron suspension strap right',[(.119,-.093,1.131),(.117,-.132,1.056),(.117,-.147,.953)],.009,leather)

def aim(o,point): o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
def lamp(label,loc,watts,size,color):
    d=bpy.data.lights.new(label,'AREA');d.energy=watts;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new(label,d);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,1.12));return o
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.007))
bpy.context.object.name='Stage | not part of asset'
bpy.context.object.data.materials.append(shale)
cam=bpy.data.cameras.new('Examination plate');cam.type='ORTHO';cam.ortho_scale=2.25
camera=bpy.data.objects.new('Examination plate',cam);scene.collection.objects.link(camera);scene.camera=camera
camera.location=(2.5,-7.0,2.6);aim(camera,(0,0,1.0))
world=bpy.data.worlds.new('Studio liner');scene.world=world;world.use_nodes=True
world.node_tree.nodes.get('Background').inputs[0].default_value=(.18,.20,.23,1)
world.node_tree.nodes.get('Background').inputs[1].default_value=.25
key=lamp('Large key',(-3,-4,4),360,4,(1,.94,.89))
fill=lamp('Frontal fill',(2,-3,2),140,3,(.86,.91,1))
rim=lamp('Contour',(1.7,2.2,3.2),270,2,(.93,.95,1))
scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=False
scene.render.resolution_x=700;scene.render.resolution_y=880;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'executioner-study.blend'),compress=True)
scene.view_layers[0].material_override=clay
scene.render.filepath=str(out/'executioner-clay.png')
bpy.ops.render.render(write_still=True)
scene.view_layers[0].material_override=None
key.data.color=(1,.79,.57);rim.data.color=(.61,.81,1)
scene.render.filepath=str(out/'executioner-steel.png')
bpy.ops.render.render(write_still=True)

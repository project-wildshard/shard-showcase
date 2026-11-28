"""Rebuild the Foundry Executioner silhouette study. Blender 4.3+; metres."""
import bpy, bmesh, sys
from math import sin, cos, pi
from mathutils import Vector
from pathlib import Path

extra=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(extra[0] if extra else '/tmp/executioner')
hybrid='hybrid' in extra[1:]
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
iron=material('02 · Blue-black quenched steel',(.109,.142,.149),.82,.42)
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
grain(iron,.23,.0028,117,(.045,.054,.057),(.19,.205,.205))
grain(bone,.23,.0021,121,(.25,.175,.113),(.72,.64,.49))
grain(apron,.35,.0023,165,(.029,.012,.007),(.175,.071,.036))
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

def shell(name,a,b,rows,mat,span=1.6,hem=None):
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
    obj=surface(name,verts,faces,mat,bevel=.0016,sub=1,thickness=.007)
    if hem:
        # Use the authored endpoints with a tiny relief in the shell normal.
        for rid in hem:
            pts=[]
            for j in range(2,n-2,3):
                point=Vector(verts[rid*n+j])
                center=a+(b-a)*rows[rid][0]
                radial=point-center;radial-=axis*radial.dot(axis)
                pts.append(point+radial.normalized()*.001)
            line(name+' | raised hem '+str(rid),pts,.0024,edge)
    return obj

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
# Two individually fitted ceramic panels make a recessed real sight opening.
maskA=(.013,-.046,1.706);maskB=(.013,-.026,1.923)
shell('Ceramic face | lower jaw',maskA,maskB,[
 (.018,.021,.070,0,-.025),(.11,.037,.088,0,-.04),(.29,.052,.106,0,-.036),
 (.47,.067,.108,.007,-.016),(.53,.071,.112,.007,-.013)],bone,1.11)
shell('Ceramic face | upper brow',maskA,maskB,[
 (.565,.071,.109,.007,-.014),(.62,.070,.114,.009,-.011),
 (.78,.068,.102,.008,.02),(.91,.049,.085,0,.019),(.96,.030,.065,0,.011)],bone,1.11)
line('Kiln enamel fissure',[(.025,-.110,1.725),(.018,-.131,1.755),(.022,-.144,1.786),(.017,-.146,1.817)],.0012,oxide)

shell('Cuirass | compound curvature breastplate',(.006,.012,1.17),(.015,.015,1.575),[
    (.025,.131,.092,.03,.015),(.12,.143,.108,.025,.010),(.40,.170,.120,.018,.02),
    (.68,.198,.134,.01,.023),(.84,.222,.130,0,-.02),(.98,.174,.110,-.035,-.12)],iron,1.46,(0,))
line('Forged diagonal raised seam',[(-.168,-.064,1.56),(-.097,-.113,1.525),
     (.010,-.123,1.451),(.072,-.095,1.373),(.127,-.054,1.30)],.003,edge)
shell('Dorsal steel guard',(.006,.017,1.245),(.018,.017,1.585),[
    (0,.140,.096,pi,0),(.21,.156,.107,pi,0),(.65,.189,.116,pi,0),(.98,.164,.082,pi,-.07)],iron,1.21)
for i in range(3):
    z=1.08+i*.044
    shell('Overlapping waist lame %s'%i,(0,.009,z),(0,.010,z+.090),[
          (0,.148,.099,-.05,-.12),(.23,.155,.110,-.045,-.03),(.79,.144,.107,-.065,.05),
          (1,.133,.096,-.06,.04)],oxide if i==0 else iron,1.49)

def joined_limb(name, a, pivot, b, upper, lower):
    # One watertight loop flow over the joint. Adjacent rings share vertices, including elbow/knee.
    a,pivot,b=map(Vector,(a,pivot,b));axes=[(pivot-a).normalized(),(b-pivot).normalized()]
    tangent=(axes[0]+axes[1]).normalized()
    rings=[]
    for is_lower, profile in enumerate((upper,lower)):
        for t,r,d in profile:
            if is_lower and t==0:continue
            center=(pivot if is_lower else a).lerp(b if is_lower else pivot,t)
            q=max(0,1-(t if is_lower else 1-t)/.33)
            axis=axes[is_lower].lerp(tangent,q).normalized()
            rings.append((center,axis,r,d))
    verts=[];faces=[];n=28
    for i,(center,axis,r,d) in enumerate(rings):
        u=(Vector((0,1,0)).cross(axis)).normalized();v=axis.cross(u)
        for j in range(n):
            t=j*2*pi/n
            fold=1+.048*sin(3*t+i*.63)+.024*cos(t*6-i*.9)
            verts.append(center+fold*(r*cos(t)*u+d*sin(t)*v))
    for i in range(len(rings)-1):
        for j in range(n):
            k=i*n+j;l=i*n+(j+1)%n;faces.append((k,l,l+n,k+n))
    faces+=[tuple(reversed(range(n))),tuple(range(len(verts)-n,len(verts)))]
    return surface(name,verts,faces,fabric,sub=2)

upper=[(0,.087,.075),(.13,.099,.087),(.33,.091,.082),(.58,.079,.073),(.85,.053,.052),(1,.047,.052)]
lower=[(0,.047,.049),(.19,.068,.060),(.40,.071,.062),(.68,.053,.049),(.90,.036,.035),(1,.036,.036)]
thigh=[(0,.095,.096),(.15,.114,.109),(.37,.106,.108),(.65,.080,.082),(.88,.060,.061),(1,.056,.057)]
shin=[(0,.054,.055),(.16,.067,.064),(.38,.074,.068),(.69,.046,.050),(.91,.039,.044),(1,.040,.048)]
for side, shoulder, elbow, wrist, hip, knee, ankle in [
    ('R',(.205,.015,1.544),(.331,-.029,1.265),(.401,-.107,1.043),
         (.095,.014,1.006),(.130,-.072,.555),(.192,-.104,.090)),
    ('L',(-.186,.027,1.537),(-.322,.041,1.263),(-.394,-.016,1.027),
         (-.097,.023,1.009),(-.137,.040,.550),(-.230,.102,.091))]:
    joined_limb('Continuous sleeve '+side,shoulder,elbow,wrist,upper,lower)
    joined_limb('Continuous trousers '+side,hip,knee,ankle,thigh,shin)
    if side=='R':
        shell('Right pauldron | drawn flange',elbow,shoulder,[
            (.57,.112,.101,.58,-.24),(.70,.125,.111,.57,-.17),(.89,.134,.121,.57,-.04),
            (1.13,.117,.111,.53,.14),(1.24,.052,.052,.43,.19)],iron,1.68)
        shell('Right rerebrace | heat band',elbow,shoulder,[
            (.42,.076,.070,.48,-.03),(.52,.093,.088,.48,-.05),(.73,.099,.092,.48,.00)],oxide,1.51)
        shell('Right lower articulated lame',elbow,shoulder,[
            (.44,.097,.084,.55,-.19),(.49,.111,.094,.54,-.10),
            (.65,.121,.106,.54,.036),(.74,.108,.093,.54,.045)],iron,1.64,(0,))
        shell('Pauldron raised crest',elbow,shoulder,[
            (.70,.130,.111,.52,-.10),(.82,.138,.123,.53,-.03),
            (1.05,.135,.125,.47,.13),(1.23,.072,.070,.43,.24)],iron,1.28)
    else:
        shell('Left fireproof shoulder guard',elbow,shoulder,[
            (.66,.096,.078,-.4,-.13),(.84,.105,.087,-.4,-.03),(1.03,.085,.073,-.4,.01)],leather,1.42)
    shell('Hand-shaped vambrace '+side,wrist,elbow,[
       (.03,.044,.049,0,.022),(.19,.053,.057,.02,.02),(.57,.073,.070,0,-.03),
       (.82,.075,.069,0,-.07),(.90,.061,.056,0,-.12)],iron,1.39)
    shell('Shin | tapered sabaton guard '+side,ankle,knee,[
       (.03,.048,.058,0,.046),(.16,.050,.059,0,.031),(.48,.069,.072,0,.02),
       (.84,.075,.069,0,-.045),(.93,.067,.057,0,-.04)],iron,1.37,(2,))
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
    loft('Boot '+side+' | leather welt',[
      (.009,.061,.117,x,y-.056),(.012,.069,.125,x,y-.058),
      (.023,.071,.128,x,y-.057),(.030,.064,.122,x,y-.056)],fabric,sub=1)
    line('Boot '+side+' | broken toe seam',[
      (x-.044,y-.128,.057),(x-.020,y-.140,.070),(x+.010,y-.139,.073),
      (x+.039,y-.128,.062)],.0019,edge)
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
            x=side*((1-u)*inside+u*outside+(u-.32)*.042*v-.034*sin(v*pi)*u)
            length=hem + .072*sin(u*pi) - .17*u + .018*sin(u*7.8+side)
            z=1.128-v*length+(x*side)*.042
            y=-center + .10*(abs(x)/.265)**2
            y-=.046*sin(pi*v*.86)
            y+=(.008+.026*v)*sin(u*12.7+v*2.9+side*.8) + .006*sin(5*u+12*v)*sin(pi*v)
            if side==1 and not back:y-=.045*sin(pi*v*.82)*(u**.55)
            y+=.013*cos(v*15.5+u*4.3)*(1-v)
            if back:y=-y+.014
            verts.append((x,y,z))
    for i in range(V-1):
        for j in range(U-1):
            k=i*U+j;faces.append((k,k+1,k+1+U,k+U))
    result=surface(name,verts,faces,mat,sub=1,thickness=.004,bevel=.0008)
    # Hem seam is sampled from the same sheet, so it follows the actual wrinkles.
    if not back:
        indexes=[(V-2)*U+i for i in range(1,U-1,3)]
        line(name+' | stitched hem',[(verts[k][0],verts[k][1]-.002,verts[k][2]+.001) for k in indexes],.00115,leather)
    return result

drape('Front leather apron | overlapped left tail',-1,.018,.218,.71,.153,apron)
drape('Front leather apron | longer right tail',1,-.029,.197,.78,.163,apron)
drape('Rear split mantle | left',-1,.018,.229,.60,.141,fabric,True)
drape('Rear split mantle | right',1,.018,.226,.66,.143,fabric,True)
line('Apron suspension strap left',[(-.135,-.082,1.131),(-.109,-.123,1.056),(-.105,-.142,.961)],.009,leather)
line('Apron suspension strap right',[(.119,-.093,1.131),(.117,-.132,1.056),(.117,-.147,.953)],.009,leather)

# Fine hardware follows silhouette and hanging load, not decorative cubes.
line('Waist belt | hand-wrought buckle',[
  (-.052,-.116,1.142),(-.047,-.127,1.155),(-.015,-.127,1.157),
  (-.011,-.127,1.126),(-.042,-.127,1.126),(-.052,-.116,1.142)],.0038,edge)
line('Waist belt | keeper pin',[(-.045,-.129,1.143),(-.016,-.128,1.139)],.0022,oxide)
if hybrid:
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from hybrid_fit import apply_collection
    apply_collection(MODEL)
    scene['executioner_fit']='hybrid'
else:
    scene['executioner_fit']='authored'
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
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False
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

# A less forgiving profile and reduced desktop-equivalent figure size.
scene.view_layers[0].material_override=clay
key.data.color=(1,.95,.92);rim.data.color=(.94,.95,1)
camera.location=(7.5,-1.25,2.1);aim(camera,(0,0,1.02))
scene.render.filepath=str(out/'executioner-profile.png')
bpy.ops.render.render(write_still=True)
scene.view_layers[0].material_override=None
cam.ortho_scale=5.6; camera.location=(2.4,-8,3.8);aim(camera,(0,0,1.05))
scene.render.resolution_x=1100;scene.render.resolution_y=620
scene.render.filepath=str(out/'executioner-distance.png')
bpy.ops.render.render(write_still=True)

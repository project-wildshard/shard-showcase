# Runs with geometry.py's reimported fixtures and exact native replay.
receipt=Path(sys.argv[-1]).resolve()
run=json.loads(receipt.read_text())
assert run["fixtures"]==fixtures and run["repeatExactly"] and run["airTicks"]==0
assert hashlib.sha256(out.read_bytes()).hexdigest()==run["geometrySha256"]
output=receipt.parent

# A world/targets hit is not an occlusion query. Check actual scene
# approach rays independently in Blender; do not infer LOS from a flag.
roots=[o for o in scene.objects if o.name.startswith("Six Targets | ")]
native_geometry=tree([o for o in scene.objects if o not in roots and o.parent not in roots])
fixture_geometry=tree([o for o in scene.objects if o in roots or o.parent in roots])
sight=[]
for hit in run["attempts"]:
    x,y,z=hit["origin"]
    eye=V((x,-z,y+1.54))
    x,y,z=hit["aim"]
    point=V((x,-z,y))
    delta=point-eye
    direction=delta.normalized()
    blocker=native_geometry.ray_cast(eye,direction,delta.length)[0]
    assert blocker is None,(hit["name"],blocker)
    fixture=fixture_geometry.ray_cast(eye,direction,delta.length+(.07 if hit["slot"]=="sword" else 0))
    if hit["slot"]=="spear":
        assert fixture[0] is None,(hit["name"],fixture)
    else:
        assert fixture[0] is not None,(hit["name"],fixture)
    sight.append(dict(id=hit["name"], environment_blocked=False,fixture_intercept=fixture[0] is not None))
(output/"sight.json").write_text(json.dumps(sight,indent=2)+"\n")

route=bpy.data.collections.new("W3a rehearsal visualization only")
scene.collection.children.link(route)

def color(name,tint,emission=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*tint,1)
    m.use_nodes=True
    shader=m.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value=(*tint,1)
    shader.inputs["Emission Color"].default_value=(*tint,1)
    shader.inputs["Emission Strength"].default_value=emission
    return m

trail=[color("Blade route",(.104,.60,.53),.36),color("Ring route",(.90,.36,.074),.30)]
def curve(name,points,radius,material):
    data=bpy.data.curves.new(name,"CURVE")
    data.dimensions="3D";data.bevel_depth=radius;data.bevel_resolution=2
    spline=data.splines.new("POLY")
    spline.points.add(len(points)-1)
    for p,c in zip(spline.points,points):
        p.co=(*c,1)
    data.materials.append(material)
    obj=bpy.data.objects.new(name,data);route.objects.link(obj)
    return obj

for i,key in enumerate(["sword","spear"]):
    path=[]
    for tick,x,y,z,slot,scored in run["frames"]:
        if tick<=run["started"] or slot!=i:
            continue
        point=V((x,-z,y+.025))
        if not path or (point-path[-1]).length>.095:
            path.append(point)
    curve(key+" verified capsule travel",path,.035,trail[i])

for row in run["attempts"]:
    if row["gained"]!=1:
        continue
    x,y,z=row["aim"]
    curve(row["name"]+" earned review tick", [(x+.12,-z+.25,y+.87),
      (x+.04,-z+.25,y+.78),(x-.15,-z+.25,y+1.0)],.035,trail[0 if row["slot"]=="sword" else 1])

for o in list(scene.objects):
    if o.type in ("LIGHT","CAMERA"):
        bpy.data.objects.remove(o,do_unlink=True)
scene.render.engine="CYCLES"
scene.cycles.use_denoising=False
scene.cycles.samples=27
scene.world=bpy.data.worlds.new("Warm late daylight")
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value=(.43,.58,.72,1)
bg.inputs["Strength"].default_value=.25
scene.view_settings.view_transform="AgX"
scene.render.image_settings.file_format="PNG"
scene.render.resolution_percentage=100
sun=bpy.data.lights.new("Afternoon soft sun","SUN")
sun.energy=2.5;sun.color=(1,.78,.57);sun.angle=math.radians(10)
ob=bpy.data.objects.new("Afternoon soft sun",sun)
scene.collection.objects.link(ob)
ob.rotation_euler=V((-.9,.6,-1.15)).to_track_quat("-Z","Y").to_euler()
cam=bpy.data.cameras.new("W3a proof cameras")
ob=bpy.data.objects.new("W3a proof cameras",cam)
scene.collection.objects.link(ob);scene.camera=ob
ring_hit=next(a for a in run["attempts"] if a["name"]=="spear-1")
x,y,z=ring_hit["origin"]
a,b,c=ring_hit["aim"]
for name,loc,target,size,lens in [
    ("overview",(-1,-70,31),(-24,-92,.5),(1280,890),40),
    ("ring",(x+.19,-z+.78,y+1.54),(a,-c,b-.28),(670,940),31),
]:
    ob.location=loc
    ob.rotation_euler=(V(target)-ob.location).to_track_quat("-Z","Y").to_euler()
    cam.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath=str(output/f"{name}.png")
    bpy.ops.render.render(write_still=True)

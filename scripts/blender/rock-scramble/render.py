# Runs inside build.py's Blender context with the fixed reviewed scene.
scene.render.engine = "CYCLES"
scene.cycles.samples = 26
scene.cycles.use_denoising = False
scene.world = bpy.data.worlds.new("Cloudy slate blue")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (.38, .53, .67, 1.)
bg.inputs["Strength"].default_value = .22
scene.view_settings.view_transform = "AgX"
scene.render.image_settings.file_format = "PNG"
scene.render.resolution_percentage = 100
for ob in list(scene.objects):
    if ob.type in ("LIGHT","CAMERA"):
        bpy.data.objects.remove(ob,do_unlink=True)

sun = bpy.data.lights.new("Late west sun","SUN")
sun.energy = 2.15
sun.angle = math.radians(9)
sun.color = (1.,.80,.60)
ob = bpy.data.objects.new("Late west sun",sun)
scene.collection.objects.link(ob)
ob.rotation_euler = (V((-207,-50,0))-V((-246,-104,40))).to_track_quat("-Z","Y").to_euler()

cam = bpy.data.cameras.new("South face views")
ob = bpy.data.objects.new("South face views",cam)
scene.collection.objects.link(ob)
scene.camera = ob
cam.clip_end=470
for name,pos,target,size,lens in [
    ("overview",(-246,-97,25),(-212,-59,7.6),(1270,870),42),
    ("portrait",(-220.4,-77.2,3.4),(-214.2,-64.7,8.8),(620,910),33),
]:
    ob.location=pos
    ob.rotation_euler = (V(target)-ob.location).to_track_quat("-Z","Y").to_euler()
    cam.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=size
    scene.render.filepath = str(out/f"{name}.png")
    bpy.ops.render.render(write_still=True)

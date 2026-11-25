"""Preserve the E1d closed asset and export a separate hollow opening version."""
import hashlib
import json
import math
import struct

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

def build(out, scene, box, mat, source_closed):
    # Existing author primitives remain distinct until this opt-in path.
    refs=[o for o in scene.objects if o.type=="MESH"]
    coords=[o.matrix_world@v.co for o in refs for v in o.data.vertices]
    lo,hi=([f(q[i] for q in coords) for i in range(3)] for f in (min,max))
    dims=(1.4,1.0,.9)
    def nrm(v):
        return Vector([d*((v[k]-lo[k])/(hi[k]-lo[k])-(.5 if k<2 else 0)) for k,d in enumerate(dims)])
    lid_names=("Pressed lid","Dark inlaid lid crown","Lid shock rail","Lid latch","Latch slot","Lid stripe")
    lids=[o for o in refs if any(o.name.startswith(k) for k in lid_names)
          or o.name.startswith("Recessed fastener") and o.location.z>.86]
    assert len(lids)==13,len(lids)
    # Hollow the two solid donor pieces inside their outer boundaries.
    liner=mat("Recessed manganese interior",(.029,.053,.055),.27,.69)
    cut=box("Chamber cutter",(0,.005,.498),(1.164,.750,.798),liner,.037)
    for proto in ("Welded lower shell","Peripheral rubber seam"):
        shell=next(o for o in refs if o.name==proto)
        shell.data.materials.append(liner)
        b=shell.modifiers.new("Hollow under gasket","BOOLEAN");b.operation="DIFFERENCE";b.solver="EXACT";b.object=cut
        bpy.context.view_layer.objects.active=shell
        bpy.ops.object.modifier_apply(modifier=b.name)
        assert any(p.material_index==1 for p in shell.data.polygons),proto
    bpy.data.objects.remove(cut,do_unlink=True)
    rubber=mat("Lid underside gasket",(.031,.041,.041),.07,.77)
    panel=box("Under lid inset liner",(0,-.001,.637),(1.197,.806,.018),rubber,.007)
    lids.append(panel);refs.append(panel)
    # A normalized rear cylinder holds the exact hinge axis. All indices are
    # source primitives, not guessed components of an already merged GLB.
    hinge_co=nrm(Vector((0,.472,.622)))
    for o in refs:
        mx=o.matrix_world.copy()
        o.data.transform(mx);o.matrix_world=Matrix.Identity(4)
        for v in o.data.vertices:v.co=nrm(v.co)
        o.data.update()
    bpy.context.view_layer.update()
    def join(obs,name):
        bpy.ops.object.select_all(action="DESELECT")
        for o in obs:o.select_set(True)
        bpy.context.view_layer.objects.active=obs[0]
        bpy.ops.object.join()
        o=bpy.context.object;o.name=o.data.name=name
        return o
    fixed=join([o for o in refs if o not in lids],"E1d_ScripChest_FixedShell")
    moving=join(lids,"E1d_ScripChest_Lid")
    moving.data.transform(Matrix.Translation(-hinge_co))
    moving.location=hinge_co
    moving.rotation_mode="QUATERNION"
    # Hold the clasp, ease out of the seat, then settle at a 102 degree stop.
    scene.render.fps=30
    schedule=[(0,0),(3,0),(6,6),(10,27),(15,64),(20,95),(24,102),(27,102)]
    from mathutils import Quaternion
    for frame,degrees in schedule:
        moving.rotation_quaternion=Quaternion((1,0,0),-math.radians(degrees))
        moving.keyframe_insert(data_path="rotation_quaternion",frame=frame)
    act=moving.animation_data.action;act.name="E1d_Scrip_Lid_Open"
    for channel in act.fcurves:
        for key in channel.keyframe_points:key.interpolation="LINEAR"
    scene.frame_start=0;scene.frame_end=27;scene.frame_set(0)
    path=out/"e1d-band1-scrip-opening.glb"
    bpy.ops.object.select_all(action="DESELECT")
    fixed.select_set(True);moving.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",
        use_selection=True,export_animations=True,export_force_sampling=False,export_anim_slide_to_zero=True,
        export_texcoords=False)
    raw=path.read_bytes()
    assert struct.unpack_from("<4sII",raw)==(b"glTF",2,len(raw))
    d=json.loads(raw[20:20+struct.unpack_from("<I",raw,12)[0]])
    assert not any(k in d for k in ("images","skins","cameras"))
    a,=d["animations"];assert a["name"]==act.name
    c,=a["channels"];assert c["target"]["path"]=="rotation"
    tris=sum(d["accessors"][p["indices"]]["count"]//3 for m in d["meshes"] for p in m["primitives"])
    assert len(raw)<190000 and tris<2300,(len(raw),tris)
    receipt={"scope":"Animated hollow donor variant, no payout or native interaction",
             "untouched_closed_sha256":hashlib.sha256(source_closed.read_bytes()).hexdigest(),
             "new_sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"triangles":tris,
             "clip":a["name"],"seconds":.9,"opening_degrees":102,"hinge_blender_m":[round(x,6) for x in hinge_co]}
    # Actual glTF reimport; keep only its two meshes to render and test the chamber.
    bpy.data.objects.remove(fixed,do_unlink=True);bpy.data.objects.remove(moving,do_unlink=True)
    before=set(scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    objs=[o for o in scene.objects if o not in before and o.type=="MESH"]
    fixed=next(o for o in objs if "FixedShell" in o.name)
    moving=next(o for o in objs if "Lid" in o.name)
    scene.frame_set(27);bpy.context.view_layer.update()
    def tree(obj):
        vs=[obj.matrix_world@v.co for v in obj.data.vertices]
        return BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in obj.data.polygons])
    floor=tree(fixed)
    heights=[]
    for ux in (-.40,-.20,0,.20,.40):
        for uy in (-.25,-.12,0,.12,.25):
            p,normal,*_=floor.ray_cast(Vector((ux,uy,1.15)),Vector((0,0,-1)),1.2)
            assert p is not None and normal.z>.85 and .07<p.z<.16,(ux,uy,p)
            heights.append(p.z)
    overlaps=[]
    for frame in range(10,28):
        scene.frame_set(frame);bpy.context.view_layer.update()
        overlaps.append(len(floor.overlap(tree(moving))))
    assert overlaps == [0]*18,overlaps
    receipt["released_lid_verified_frames"]=[10,27]
    receipt["interior_rays"]=len(heights)
    receipt["interior_floor_range_m"]=[round(f(heights),6) for f in (min,max)]
    (out/"e1d-band1-scrip-opening-proof.json").write_text(json.dumps(receipt,indent=2)+"\n")
    return moving,fixed

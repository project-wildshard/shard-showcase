from pathlib import Path
import bpy, sys

def output_directory():
    if "--" not in sys.argv or len(sys.argv[sys.argv.index("--")+1:]) != 1:
        raise SystemExit("Pass a single output directory after --.")
    out = Path(sys.argv[-1]).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    return out

def clear_scene():
    for obj in tuple(bpy.context.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

def export(parts, destination):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.export_scene.gltf(filepath=str(destination), export_format="GLB",
        use_selection=True, export_animations=False)

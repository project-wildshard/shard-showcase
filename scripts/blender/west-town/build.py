"""Regenerate whole-town static WIP from tracked placement and parent recipes."""
import argparse,hashlib,json,runpy,struct,subprocess,sys
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;repo=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=a.output.resolve();assert repo not in out.parents and out!=repo
expected=json.loads((HERE/'expected.json').read_text())
lots=subprocess.check_output(['node',str(HERE/'town-plan.mjs')])
assert hashlib.sha256(lots).hexdigest()==expected['town_lots_sha256']
out.mkdir(parents=True,exist_ok=True)
(out/'town-lots.json').write_bytes(lots)
sys.argv=['blender','--','--output',str(out/'prior')]
runpy.run_path(str(HERE.parent/'west-zip/build.py'),run_name='__main__')
bpy.ops.wm.open_mainfile(filepath=str(out/'prior/west-zip-route-editable.blend'))
runpy.run_path(str(HERE/'assemble.py'),init_globals={'OUT':out})
runpy.run_path(str(HERE/'validate.py'),init_globals={'out':out,'HERE':HERE,'expected':expected})

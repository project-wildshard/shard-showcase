"""Blender4.3.2 source-only continuation; output outside checkout."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;repo=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=a.output.resolve();assert repo not in out.parents and out!=repo
for d in json.loads((HERE/'dependencies.json').read_text()):
 f=repo/d['path'];assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==d['sha256'],d
out.mkdir(parents=True,exist_ok=True)
sys.argv=['blender','--','--output',str(out/'r02')]
runpy.run_path(str(HERE.parent/'west-scene-r02/build.py'),run_name='__main__')
bpy.ops.wm.open_mainfile(filepath=str(out/'r02/west-linked-r02-editable.blend'))
runpy.run_path(str(HERE/'movers.py'),init_globals={'OUT':out/'movers','REPO':repo})
runpy.run_path(str(HERE/'junction.py'),init_globals={'OUT':out/'junction','REPO':repo})
sig=runpy.run_path(str(HERE.parent/'west-scene-r02/semantic_glb.py'))['signature']
expected=json.loads((HERE/'expected.json').read_text());results={}
for key,n in [('movers','west-r02-plus-movers-WIP.glb'),('junction','west-shared-roof-WIP.glb')]:
 f=out/key/n;actual=sig(f);assert list(actual)==expected[key]['semantic_signature'],(key,actual,expected[key])
 results[key]={'matched_signature':actual,'rebuilt_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
(out/'parity.json').write_text(json.dumps(results,indent=2))
print('MOVERS AND SHARED ROOF SEMANTIC PARITY PASS',results)

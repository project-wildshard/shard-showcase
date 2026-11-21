"""Tracked-only static Hover Park build."""
import argparse,hashlib,json,runpy,struct,sys
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;repo=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=a.output.resolve();assert repo not in out.parents and out!=repo
pins=json.loads((HERE/'dependencies.json').read_text())
for n,h in pins.items():
 f=repo/'public/assets/wildshard-art'/n;assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==h,n
out.mkdir(parents=True,exist_ok=True)
sys.argv=['blender','--','--output',str(out/'prior')]
runpy.run_path(str(HERE.parent/'west-climb-rock/build.py'),run_name='__main__')
bpy.ops.wm.open_mainfile(filepath=str(out/'prior/climb-rock-editable.blend'))
runpy.run_path(str(HERE/'assemble.py'),init_globals={'OUT':out,'REPO':repo,'PINS':pins})
f=out/'hover-park-WIP.glb';b=f.read_bytes()
assert struct.unpack_from('<4sII',b)==(b'glTF',2,len(b))
expected=json.loads((HERE/'expected.json').read_text())
m=json.loads((out/'integration.json').read_text())
assert all(m[k]==v for k,v in expected['placement'].items())
sig=runpy.run_path(str(HERE.parent/'west-scene-r02/semantic_glb.py'))['signature']
strict=actual=sig(f);changes=0
if list(actual)!=expected['semantic_signature']:
 normalize=runpy.run_path(str(HERE.parent/'west-zip/arm_uv.py'))['normalize']
 temporary=out/'parity-arm-uv.glb'
 try:
  changes=normalize(f,temporary);actual=sig(temporary)
  assert list(actual)==expected['normalized_semantic_signature'],(actual,expected)
 finally:
  temporary.unlink(missing_ok=True)
runpy.run_path(str(HERE/'verify.py'),init_globals={'OUT':out})
(out/'parity.json').write_text(json.dumps({'matched_signature':actual,'raw_signature':strict,'inherited_arm_uv_writes':changes,'rebuilt_sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)},indent=2)+'\n')
print('HOVER PARK SEMANTIC PARITY AND REIMPORT QA PASS',actual)

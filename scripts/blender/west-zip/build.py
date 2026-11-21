"""Rebuild the reviewed static West zipline from tracked sources."""
import argparse,hashlib,json,runpy,struct,sys
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;repo=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=a.output.resolve();assert repo not in out.parents and out!=repo
for d in json.loads((HERE/'dependencies.json').read_text()):
 f=repo/d['path'];assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==d['sha256'],d
out.mkdir(parents=True,exist_ok=True)
runpy.run_path(str(HERE/'components.py'),init_globals={'REPO':repo,'OUT':out})
sys.argv=['blender','--','--output',str(out/'prior')]
runpy.run_path(str(HERE.parent/'west-movers-roof/build.py'),run_name='__main__')
bpy.ops.wm.open_mainfile(filepath=str(out/'prior/junction/west-shared-roof-editable.blend'))
runpy.run_path(str(HERE/'assemble.py'),init_globals={'OUT':out,'COMPONENTS':out/'w08-components.blend'})
f=out/'west-zip-route-WIP.glb';b=f.read_bytes()
assert struct.unpack_from('<4sII',b)==(b'glTF',2,len(b))
g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert not g.get('skins') and not g.get('animations')
assert all('uri' not in x for x in g.get('images',[])+g.get('buffers',[]))
sig=runpy.run_path(str(HERE.parent/'west-scene-r02/semantic_glb.py'))['signature']

strict=sig(f);expected=json.loads((HERE/'expected.json').read_text())
normalize=runpy.run_path(str(HERE/'arm_uv.py'))['normalize']
normalized=out/'parity-arm-uv.glb'
try:
 changes=normalize(f,normalized);actual=sig(normalized)
 assert list(actual)==expected['normalized_semantic_signature'],(actual,expected)
finally:
 normalized.unlink(missing_ok=True)
(out/'parity.json').write_text(json.dumps({'matched_signature':actual,'raw_signature':strict,'known_arm_uv_values':[.3125000596046448,.3125],'rebuilt_arm_uv_writes':changes,'rebuilt_sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)},indent=2)+'\n')
print('WEST ZIP SEMANTIC PARITY PASS, SCOPED ARM UV NORMALIZATION',actual)

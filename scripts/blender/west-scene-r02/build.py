"""Blender4.3.2: --python build.py -- --output /absolute/scratch [--render]."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--render',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
repo=HERE.parents[2];out=a.output.resolve()
# Never mix generated binaries into tracked source or shared asset directories.
assert repo not in out.parents and out!=repo,'Choose a separate scratch output directory outside checkout'
manifest=json.loads((HERE/'dependencies.json').read_text())
for d in manifest['dependencies']:
 f=repo/d['path'];assert f.is_file(),f'Missing tracked dependency: {d["path"]}'
 assert hashlib.sha256(f.read_bytes()).hexdigest()==d['sha256'],f'Changed dependency: {d["path"]}'
out.mkdir(parents=True,exist_ok=True)
common={'REPO':repo,'RENDER':a.render}
runpy.run_path(str(HERE/'stable.py'),init_globals={**common,'OUT':out/'stable'})
runpy.run_path(str(HERE/'assemble.py'),init_globals={**common,'OUT':out/'baseline'})
runpy.run_path(str(HERE/'finish.py'),init_globals={**common,'OUT':out,'STABLE_FILE':out/'stable/stable-gate-frontage-art-WIP.glb'})
runpy.run_path(str(HERE/'views.py'),init_globals={**common,'OUT':out})
runpy.run_path(str(HERE/'validate.py'),init_globals={'OUT':out})
print('HASH-PINNED WEST R02 REBUILD COMPLETE')

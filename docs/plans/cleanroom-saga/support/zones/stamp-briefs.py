# Stamp the shared brief (BRIEF.md beside this file) into every zone's
# clean room as README.md: a "# <zone name>" title line, then the brief,
# byte for byte. Zone-specific things (the boss, the look) live in each
# ZONE-DESCRIPTION.md, never in the brief. Also refreshes the copies here.
# Usage: python3 -I stamp-briefs.py [--check]
import os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEMOS = os.path.expanduser('~/projects/game-demos')
ZONES = {
  'signal-dunes': 'Signal Dunes', 'sky-reach': 'Sky Reach',
  'mossgate': 'Mossgate Hollow', 'brasscap': 'Brasscap Mesa',
  'driftwood': 'Driftwood Isle', 'pine-hollow': 'Pine Hollow',
  'nalati': 'Nalati Grasslands', 'nine-dragon': 'Nine Dragon Stack',
}
brief = open(f'{HERE}/BRIEF.md').read()
check = '--check' in sys.argv
bad = 0
for slug, name in ZONES.items():
    room = f'{DEMOS}/{slug}-clean-room'
    want = f'# {name}\n\n{brief}'
    path = f'{room}/README.md'
    have = open(path).read() if os.path.exists(path) else None
    if have != want:
        bad += 1
        if check: print('stale', path); continue
        open(path, 'w').write(want)
        print('wrote', path)
    if not check:
        os.makedirs(f'{HERE}/{slug}', exist_ok=True)
        shutil.copy(f'{room}/ZONE-DESCRIPTION.md', f'{HERE}/{slug}/ZONE-DESCRIPTION.md')
sys.exit(1 if check and bad else 0)

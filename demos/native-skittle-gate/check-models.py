"""Check actual exported local-space dimensions against the bench's kinematic box."""
import hashlib
import json
import struct
import sys
from pathlib import Path

d=Path(sys.argv[1])
g=json.loads((d/'proof.json').read_text())['gate']
result={}
for label in ('bar','yoke'):
    f=d/f'w4b-ball-gate-{label}.glb'
    b=f.read_bytes()
    magic,ver,length,n=struct.unpack_from('<4sIII',b,0)
    assert (magic,ver,length)==(b'glTF',2,len(b))
    j=json.loads(b[20:20+n])
    assert not j.get('textures') and not j.get('animations')
    node,=j['nodes']
    assert not {'translation','rotation','scale','matrix'}&node.keys(),node
    prim=j['meshes'][node['mesh']]['primitives']
    bounds=[j['accessors'][p['attributes']['POSITION']] for p in prim]
    lo=[min(q['min'][k] for q in bounds) for k in range(3)]
    hi=[max(q['max'][k] for q in bounds) for k in range(3)]
    if label=='bar':
        for i,half in enumerate(g['half']):
            assert max(abs(lo[i]+half),abs(hi[i]-half))<.002,(lo,hi)
    else:
        assert abs(lo[1]+.75)<1e-6
        assert hi[1]>g['lift']+g['half'][1]
    result[label]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'min':lo,'max':hi,
        'primitives':len(prim),'triangles':sum(j['accessors'][p['indices']]['count']//3 for p in prim)}
(d/'models.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))

"""Check exact exported architecture, including an unobstructed inner rectangle."""
import json
import math
from pathlib import Path
import struct
import sys

b=Path(sys.argv[1]).read_bytes()
assert struct.unpack_from('<4sII',b)==(b'glTF',2,len(b)) and len(b)<262144
n,kind=struct.unpack_from('<I4s',b,12)
assert kind==b'JSON'
g=json.loads(b[20:20+n]); buf=b[28+n:]
assert not g.get('images') and not g.get('animations')
assert {nd['name'] for nd in g['nodes']}=={'Masonry_Shell','Open_Portal_Frame','Lens_And_Keycard_Detail'}
def accessor(i):
    a=g['accessors'][i]; v=g['bufferViews'][a['bufferView']]
    fmt='<'+{'SCALAR':1,'VEC3':3}[a['type']]*{5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']]
    start=v.get('byteOffset',0)+a.get('byteOffset',0); stride=v.get('byteStride',struct.calcsize(fmt))
    return [struct.unpack_from(fmt,buf,start+j*stride) for j in range(a['count'])]
def cut(poly,i,sign,t):
    q=[]
    for a,c in zip(poly,poly[1:]+poly[:1]):
        da=(a[i]-t)*sign; dc=(c[i]-t)*sign
        if da>=0:q.append(a)
        if (da>=0)!=(dc>=0):
            f=da/(da-dc); q.append(tuple(a[k]+f*(c[k]-a[k]) for k in range(2)))
    return q
count=0; mins=[math.inf]*3; maxs=[-math.inf]*3
for nd in g['nodes']:
    # Source assembly joins in the same unrotated frame with pivots on the sill.
    assert not any(k in nd for k in ('translation','matrix','rotation','scale','children')),nd
    for p in g['meshes'][nd['mesh']]['primitives']:
        assert p.get('mode',4)==4
        ps=accessor(p['attributes']['POSITION'])
        ix=accessor(p['indices'])
        assert len(ix)%3==0
        count+=len(ix)//3
        for v in ps:
            for j in range(3): mins[j]=min(mins[j],v[j]);maxs[j]=max(maxs[j],v[j])
        for i in range(0,len(ix),3):
            poly=[ps[j][:2] for j, in ix[i:i+3]]
            for axis,sign,edge in [(0,1,-.80),(0,-1,.80),(1,1,.065),(1,-1,2.95)]:
                if poly:poly=cut(poly,axis,sign,edge)
            assert not poly,('geometry in walk-in opening',nd['name'],poly)
assert count<5000 and abs(mins[1])<.01
size=tuple(round(h-l,3) for l,h in zip(mins,maxs))
print(f'Training Vault portal: {len(b):,} bytes, {count:,} triangles, bounds {size} m; clear 1.6 × 2.885 m inner region')

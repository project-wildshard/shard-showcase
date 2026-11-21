import json,struct,hashlib,math
from pathlib import Path
p=Path(__file__).resolve().parent
out=[]
for f in sorted(p.glob('*.glb')):
 b=f.read_bytes();magic,ver,size=struct.unpack_from('<4sII',b);assert magic==b'glTF' and ver==2 and size==len(b)
 n,typ=struct.unpack_from('<II',b,12);g=json.loads(b[20:20+n]);assert typ==0x4e4f534a
 assert not g.get('skins') and not g.get('animations')
 assert all('uri' not in x for x in g.get('buffers',[])+g.get('images',[]))
 tris=0
 for mesh in g['meshes']:
  for prim in mesh['primitives']:
   assert prim.get('mode',4)==4
   a=g['accessors'][prim['indices']];assert a['count']%3==0;tris+=a['count']//3
   a=g['accessors'][prim['attributes']['POSITION']];assert all(math.isfinite(v) for v in a['min']+a['max'])
 assert len(b)<1000000 and tris<15000
 out.append({'file':f.name,'bytes':len(b),'triangles':tris,'meshes':len(g['meshes']),'materials':len(g['materials']),'sha256':hashlib.sha256(b).hexdigest(),'checks':'GLB2 lengths, embedded resources, finite position bounds, indexed triangles, no rig/animation, <1 MB and <15k triangles: PASS'})
(p/'checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

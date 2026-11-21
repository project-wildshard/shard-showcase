import json,struct,hashlib,math,sys
from pathlib import Path
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()/'tmp/w10-mounting-block';f=P/'wsc-plan-008-horse-mounting-block-wip.glb';b=f.read_bytes()
magic,version,length=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and length==len(b)
n,t=struct.unpack_from('<II',b,12);assert t==0x4e4f534a;j=json.loads(b[20:20+n]);assert not j.get('extensionsRequired');assert all('uri' not in v for v in j.get('buffers',[]));assert not j.get('images');assert not j.get('animations');bn,bt=struct.unpack_from('<II',b,20+n);assert bt==0x004e4942;binary=b[28+n:28+n+bn]
tri=0
for mesh in j['meshes']:
 for p in mesh['primitives']:
  assert p.get('mode',4)==4
  a=j['accessors'][p['attributes']['POSITION']];assert a['componentType']==5126;v=j['bufferViews'][a['bufferView']];off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12)
  assert all(math.isfinite(x) for i in range(a['count']) for x in struct.unpack_from('<fff',binary,off+i*stride))
  ind=j['accessors'][p['indices']];assert ind['count']%3==0;tri+=ind['count']//3
validation=json.loads((P/'validation.json').read_text());assert tri==validation['triangles'];assert validation['blender_z_up_bounds']['min'][2]>=-1e-6
out={'valid_glb2':True,'finite_positions':True,'embedded_only':True,'no_external_textures':True,'no_animations':True,'triangle_count_matches_reimport':tri,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};(P/'glb-check.json').write_text(json.dumps(out,indent=2)+'\n');print(out)

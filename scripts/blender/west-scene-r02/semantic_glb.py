import json,struct,hashlib
from pathlib import Path
def signature(path):
 b=Path(path).read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);bin=b[28+n:]
 def accessor(i,triangles=False):
  a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);size={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];stride=v.get('byteStride',size);raw=b''.join(bin[offset+j*stride:offset+j*stride+size] for j in range(a['count']));
  if triangles:
   vals=struct.unpack('<'+{5121:'B',5123:'H',5125:'I'}[a['componentType']]*a['count'],raw);rows=[tuple(vals[j:j+3]) for j in range(0,len(vals),3)];raw=json.dumps(sorted(min(t,t[1:]+t[:1],t[2:]+t[:2]) for t in rows)).encode()
  return hashlib.sha256(raw).hexdigest()
 def material(i):
  m=json.loads(json.dumps(g['materials'][i]));m.pop('name',None)
  def walk(x):
   if isinstance(x,dict):
    for k,v in list(x.items()):
     if k.endswith('Texture') and isinstance(v,dict):
      tex=g['textures'][v['index']];im=g['images'][tex['source']];bv=g['bufferViews'][im['bufferView']];v['index']=hashlib.sha256(bin[bv.get('byteOffset',0):bv.get('byteOffset',0)+bv['byteLength']]).hexdigest()
     else:walk(v)
   elif isinstance(x,list):
    for v in x:walk(v)
  walk(m);return m
 result=[]
 for nd in g['nodes']:
  if 'mesh' not in nd:continue
  assert not nd.get('children'),'nested mesh graph unsupported'
  trans={k:nd[k] for k in ['matrix','translation','rotation','scale'] if k in nd}
  for pr in g['meshes'][nd['mesh']]['primitives']:
   result.append(json.dumps({'transform':trans,'attributes':{k:accessor(v) for k,v in pr['attributes'].items()},'indices':accessor(pr['indices'],True),'material':material(pr['material'])},sort_keys=True))
 return hashlib.sha256('\n'.join(sorted(result)).encode()).hexdigest(),len(result)
if __name__=='__main__':
 import sys
 for f in sys.argv[1:]:print(f,signature(f))

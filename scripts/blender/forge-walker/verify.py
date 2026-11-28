"""Verify the runtime Walker export and hand/socket contract without Blender."""
from pathlib import Path
import json, math, struct, sys
path=Path(sys.argv[1])
raw=path.read_bytes()
assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
size,kind=struct.unpack_from('<II',raw,12)
assert kind==0x4e4f534a
g=json.loads(raw[20:20+size]);binary=28+size
nodes=g['nodes']; names={n['name']:i for i,n in enumerate(nodes)}
parents={child:n['name'] for n in nodes for child in n.get('children',[])}
required=['root','pelvis','chest','head','pack','coat']
for side in ['L','R']:
 required.extend(n+'_'+side for n in ['upper','elbow','hand','hip','knee','boot'])
assert all(n in names for n in required)
for socket,expected in [('grip_R','hand_R'),('grip_L','hand_L'),('ground_socket','root')]:
 assert parents[names[socket]]==expected
assert max(map(abs,nodes[names['ground_socket']].get('translation',[0,0,0])))<1e-5
assert not g.get('images') and not g.get('cameras')
expected={'Idle','Stride','Turn','Dodge','Hit','Defeat','Sweep','Chop','Thrust'}
assert {a['name'] for a in g['animations']}==expected
def read(i,count):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];off=binary+v.get('byteOffset',0)+a.get('byteOffset',0)
 assert a['componentType']==5126
 return [struct.unpack_from('<'+'f'*count,raw,off+j*v.get('byteStride',4*count)) for j in range(a['count'])]
proof={}
for a in g['animations']:
 changed=set();duration=0;deltas={}
 for c in a['channels']:
  target=c['target'];sampler=a['samplers'][c['sampler']]
  times=read(sampler['input'],1);p=target['path']
  rows=read(sampler['output'],4 if p=='rotation' else 3)
  assert len(times)==len(rows) and all(math.isfinite(x) for r in rows for x in r)
  name=nodes[target['node']]['name'];duration=max(duration,times[-1][0]-times[0][0])
  delta=max(math.dist(rows[0],r) for r in rows)
  if delta>.012:changed.add(name);deltas[name]=round(delta,3)
 assert changed and .36<=duration<=1.65
 if a['name'] in ('Sweep','Chop','Thrust'):assert {'chest','upper_R','elbow_R'}<=changed
 proof[a['name']]={'durationSeconds':round(duration,3),'movingNodes':sorted(changed),'deltas':deltas}
assert len({json.dumps(proof[k]['deltas'],sort_keys=True) for k in ['Sweep','Chop','Thrust']})==3
tri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])
assert 0<tri<9000 and len(raw)<650000
print(json.dumps({'triangles':tri,'bytes':len(raw),'articulatedJoints':len(required),
 'sockets':{'grip_R':'hand_R','grip_L':'hand_L','ground_socket':'root'},'clips':proof},indent=2))

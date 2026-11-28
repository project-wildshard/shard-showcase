"""Verify original robot export skeleton motion and drop-in yard sockets."""
import json,math,struct,sys
from pathlib import Path
root=Path(sys.argv[1])
expected={'sentry':'windmill','skitter':'pounce','wasp':'beam','ram':'charge'}
clips={'Idle','Move','Turn','Windup','Attack','Recover','Hit','Special','Defeat'}
out=[]
for name,behavior in expected.items():
 f=root/(name+'.glb');b=f.read_bytes()
 assert struct.unpack_from('<4sII',b)==(b'glTF',2,len(b))
 n,k=struct.unpack_from('<II',b,12); assert k==0x4e4f534a
 g=json.loads(b[20:20+n]);offset=28+n
 nd=g['nodes']; names={x['name']:x for x in nd}
 assert {'root','body','head','ground_socket','weak_socket','attack_socket'}<=names.keys()
 assert max(map(abs,names['ground_socket'].get('translation',[0,0,0])))<1e-5
 assert not g.get('images') and not g.get('cameras')
 assert {a['name'] for a in g['animations']}==clips
 def stream(i,k):
  a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];start=offset+v.get('byteOffset',0)+a.get('byteOffset',0)
  assert a['componentType']==5126
  return [struct.unpack_from('<'+'f'*k,b,start+j*v.get('byteStride',4*k)) for j in range(a['count'])]
 data={}
 for a in g['animations']:
  d=0;changed=set();signature=[]
  for c in a['channels']:
   t=c['target'];s=a['samplers'][c['sampler']];p=t['path']
   t0=stream(s['input'],1);o=stream(s['output'],4 if p=='rotation' else 3)
   assert len(t0)==len(o) and all(math.isfinite(x) for v in o for x in v)
   node=nd[t['node']]['name'];d=max(d,t0[-1][0]-t0[0][0])
   span=max(math.dist(o[0],v) for v in o)
   if span>.015:changed.add(node);signature.append((node,p,round(span,3)))
  assert changed and .32<=d<=1.65,a['name']
  data[a['name']]={'duration':round(d,3),'moving_nodes':sorted(changed),'signature':signature}
 assert data['Attack']['signature']!=data['Special']['signature']
 tri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])
 assert 0<tri<=6500
 out.append({'id':next(x for x in names if x.startswith('WSC-ENM-')).split()[0],
   'file':f.name,'behavior':behavior,'triangles':tri,'bytes':len(b),'clips':data,
   'status':'modeled and rigged; prototype yard integration pending'})
print(json.dumps({'enemy_types':out,'variant_count':0,'clip_count':len(out)*len(clips)},indent=2))

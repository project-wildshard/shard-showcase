from pathlib import Path
import json,struct,hashlib,math
p=OUT;b=(p/'west-linked-r02.glb').read_bytes();magic,ver,size=struct.unpack_from('<4sII',b);assert magic==b'glTF' and ver==2 and size==len(b);g=json.loads(b[20:20+struct.unpack_from('<I',b,12)[0]])
assert not g.get('skins') and not g.get('animations');assert all('uri' not in x for x in g.get('buffers',[])+g.get('images',[]))
assert all(math.isfinite(v) for a in g['accessors'] for k in ['min','max'] for v in a.get(k,[]))
names=[x.get('name','') for x in g['nodes']];assert not any(n.startswith('Stable WIP') for n in names)
r={'status':'WIP asset integrity PASS; engine/gameplay NOT TESTED','bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'nodes':len(g['nodes']),'unique_meshes':len(g['meshes']),'unique_triangles':sum(g['accessors'][a['indices']]['count']//3 for m in g['meshes'] for a in m['primitives']),'finite_accessors':True,'embedded_resources':True,'old_stable_proxy_removed':True,'unchanged_source_units':'metres','gate_clear_width_m':12,'eye_height_m':1.75,'mounted_eye_height_m':2.6,'roundtrip':'exported GLB freshly reimported in Blender by build driver'}
(p/'QA.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))

import runpy
semantic=runpy.run_path(str(Path(__file__).with_name('semantic_glb.py')))['signature']
sig,count=semantic(p/'west-linked-r02.glb')
assert sig=='7428d16f297dd3399d8f9735e1123168422af3722362d18d949097a999d0067b',(sig,count)
r['rendered_r02_semantic_fingerprint']=sig
r['matched_rendered_r02_primitives']=count
r['render_status']='Optional --render; integrity test does not claim pixels were freshly rendered'
(p/'QA.json').write_text(json.dumps(r,indent=2))
print('MATCHES REVIEWED R02 GEOMETRY, WINDING, MATERIALS AND TRANSFORMS',sig)

import hashlib,json,re,sys
from pathlib import Path
if len(sys.argv)!=3:
    raise SystemExit('Usage: extract-round5-atlas.py <pinned layout.js> <out.json>')
p=Path(sys.argv[1]);b=p.read_bytes()
sha=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
assert sha=='5d019a020361c47187ec889f2bc947f82cd9f98a',sha
s=b.decode()
ids={'01':'West Town','02':'Weapon Range','03':'Physics Yard','04':'Riding Course','MP':'Paddock','05':'Movers Run',
     '06':'Grapple Course','10':'Climb Yard','H':'The Rock','11':'Hover Park','07':'Stealth Yard',
     '08F':'Gauntlet Forecourt','08A':'C1 Loading Yard','08B':'C2 The Pit','08C':'C3 Foreman’s Floor',
     'TG':'Titan Portal','M6':'Big Pallet','TV':'Vault Gate'}
def row(k,s):
    for m in re.split(r',\s*(?=\{ id:)',s):
        if m.lstrip().startswith("{ id: '"+k+"'"):return m
    # Comments sometimes separate groups from the previous row.
    return re.search(r"\{ id: '"+k+r"',[\s\S]*?(?=\n\s*\{ id:|\n\];)",s)[0]
def n(key,h):return float(re.search(r'\b'+key+r':\s*(-?\d+(?:\.\d+)?)',h).group(1))
def norm(a):return [int(x) if int(x)==x else x for x in a]
def nums(s):return norm([float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',s)])
block=re.search(r'export const ZONES = \[\n([\s\S]+?)\n\];',s)[1]
zones={}
for k,label in ids.items():
    line=row(k,block);shape=re.search(r"shape: '([^']+)'",line)[1]
    if k=='01':line=re.search(r'export const TOWN = \{(.*?)\};',s)[1]
    if shape=='rect':d=norm([n(x,line) for x in ['x0','x1','z0','z1']])
    elif shape=='rects':d=json.loads(re.search(r'list: (\[\[.*?\]\])',line)[1])
    else:d=norm([n(x,line) for x in ['x','z','r']+(['halfLen'] if shape=='stadium' else [])])
    zones[k]={'label':label,'shape':shape,'geometry':d}
gate_block=re.search(r"export const GATES = \[([\s\S]+?)\n\];",s)[1]
gates=[[m[0],int(m[1]),int(m[2])] for m in re.findall(r"\{ id: '([A-Z]+)', name: '[^']+', x: (-?\d+), z: (-?\d+)",gate_block)]
assert len(gates)==6,gates
road=re.search(r'export const ROAD = \{(.*?)\};',s)[1];assert 'x1: STRIP.inner' in road
strip=re.search(r'export const STRIP = \{(.*?)\};',s)[1]
layer_vault=nums(re.search(r"name: 'Training Vault interior \(4 rooms\)', box: \[([^\]]+)",s)[1])
layer_titan=nums(re.search(r"name: 'Crate Titan arena \(floor, stands, sky\)', box: \[([^\]]+)",s)[1])
assert layer_vault==[151,221,-99,-29,-40,-30] and layer_titan==[80,220,95,235,-156,-80]
arena=re.search(r'export const TITAN_ARENA = \{([\s\S]+?)\n\};',s)[1]
pinned={
 'source':{'repository':'Raynos/project-wildshard-singleplayer','ref':'ce1cf050b3','path':'art/showcase-template/round-5-blockout/layout.js','blob_sha1':sha},
 'semantics':{'x':'east','z':'south','y':'up','dimensions':'metres'},
 'cell':nums(re.search(r'export const CELL = (\d+), HALF = (\d+)',s)[0]),
 'surface':{'zones':zones,'seam_x':n('SEAM_X',s.replace('SEAM_X =','SEAM_X:')),
            'town_gates':gates,'east_road':norm([n('x0',road),n('inner',strip),-n('half',road),n('half',road)]),
            'ring':norm([n('inner',strip),n('outer',strip)]),
            'gauntlet_passages':[nums(m) for m in re.findall(r"passage: \[([^\]]+)",s)],
            'titan_road':nums(re.search(r'export const TITAN_ROAD = \{(.*?)\};',s)[1].replace('x0','a').replace('x1','b').replace('z0','c').replace('z1','d')),
            'cave_mouths':[nums(re.search(r'cave'+m+r': \[([^\]]+)',s)[1]) for m in ['N','S']],
            'titan_portal':nums(re.search(r'arch: \{ x: (\d+), z: (\d+), w: \d+, h: \d+, portalR: \d+ \}',s)[0])[:2]},
 'below':{'vault_bounds_round5':layer_vault,'vault_bounds_D41':[151,221,-99,-29,-50,-30],
          'titan_layer_round5':layer_titan,'titan_floor_y':int(n('y',arena)),'titan_sky_y':int(n('ceiling',arena)),
          'titan_floor_diameter':int(2*n('floorR',arena)),'titan_stands_diameter':int(2*n('standsR',arena))},
 'overlays':{'D7':'Launch walls; not a true halfpipe','D41':'Vault envelope y −50…−30','D61':'No player heatmap or minimap band borders',
             'D4':['Yard Boss','Weapon Range','Riding lap','Movers top deck','Zip into town','Report at East Gate']}}
assert pinned['cell']==[500,250]
assert pinned['surface']['titan_road']==[120,222,124,136]
assert pinned['surface']['gauntlet_passages']==[[25,35,184,190],[96,115,210,218],[188,208,182,190]]
assert pinned['surface']['titan_portal']==[216,229]
Path(sys.argv[2]).write_text(json.dumps(pinned,ensure_ascii=False,indent=2)+'\n')

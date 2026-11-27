import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
const root=new URL('../../../project/layouts/',import.meta.url)
const docs={}
for(const name of ['w11a-gate-lanterns-proof','w11a-obelisk-lighting','w11a-record-board-light-proof','w6d-movers-start']){
 const b=readFileSync(new URL(name+'.json',root))
 docs[name]={sha256:createHash('sha256').update(b).digest('hex'),data:JSON.parse(b)}
}
const files=Object.fromEntries(Object.entries(docs).map(([k,v])=>[k,v.sha256]))
const gate=docs['w11a-gate-lanterns-proof'].data.gates
const obelisk=docs['w11a-obelisk-lighting'].data
const movers=docs['w6d-movers-start'].data
const record=docs['w11a-record-board-light-proof'].data.find(r=>r.donor==='Movers')
const round=n=>+n.toFixed(6)
const points={},groups={},origins={},rows=[]
function lamp(id,at,meshMount,colour,gain,distance,bank){
 const point=id+'.point',parent=id+'.lens'
 points[point]=at.map(round)
 groups[parent]=id
 origins[id]=meshMount
 rows.push({id,parent,initially:false,draws:[],
  light:{at:{point},colour,gain,distance,decay:2,shared:true,waves:[[.82+bank*.23,.17,.013]]}})
}
for(const [place,i,bank] of [['Stable',0,0],['West',0,0],['West',1,1]]){
 const row=gate[place].lanterns[i]
 lamp(`west.gate.${place.toLowerCase()}.${i+1}`,row.light_three_xyz_m,
  {kind:'gate',at:row.mount_three_xyz_m,yaw:gate[place].yaw_deg*Math.PI/180},0xffbd76,46,9,bank)
}
const [ox,oz]=[obelisk.obelisk_world_xyz[0],-obelisk.obelisk_world_xyz[1]]
obelisk.fixture_quadrant_offsets_m.forEach(([dx,by],i)=>{
 const dz=-by,n=Math.hypot(dx,dz)
 lamp('west.obelisk.'+(i+1),[ox+dx-.25*dx/n,.303,oz+dz-.25*dz/n],
  {kind:'obelisk',at:[ox+dx,0,oz+dz],yaw:Math.atan2(-dx/n,-dz/n)},0xffb66a,65,13,i%2+2)
})
const [x,z]=movers.board_map_xz,[sx,sz]=movers.start_map_xz
assert.deepEqual(movers.board_footing_z_m,[0,0])
const norm=Math.hypot(sx-x,sz-z),fx=(sx-x)/norm,fz=(sz-z)/norm
lamp('west.movers.record',[x+.513*fx,record.seat_y_m+.035,z+.513*fz],
 {kind:'movers',board:[x,0,z],at:[x+.12*fx,record.seat_y_m,z+.12*fz],yaw:Math.atan2(fx,fz)},0xffbc78,16,4,1)
const clock={units:'phase',dayFraction:20/24,start:0,sun:{maxElevation:72,azimuthOffset:0},
 schedule:[{phase:'day',from:6,to:18,minutes:20},{phase:'night',from:18,to:30,minutes:4}],
 fixed:{midday:.416667,golden:.763889,sunset:20/24,night:.916667},
 presets:{dawn:0,noon:.416667,dusk:20/24,night:.916667}}
const result={scope:'W11a light-row candidate and local consumer test only; no installed client plan, weather or production look.',
 provenance:files,clock,scenePoints:points,emitterGroups:groups,artMounts:origins,nightGate:{from:18,to:6},emitters:{version:1,input:'west.night.pool',clock:'west.night.seconds',rows}}
writeFileSync(process.argv[2],JSON.stringify(result,null,2)+'\n')

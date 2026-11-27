import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const [file,out]=process.argv.slice(2)
const raw=readFileSync(file),data=JSON.parse(raw)
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const engine=req.resolve('@wildshard/engine/package.json'),formatSource=req.resolve('@wildshard/format/lightEmitters'),format=resolve(dirname(formatSource),'../..','package.json')
assert.equal(JSON.parse(readFileSync(engine)).version,'0.1.44')
assert.equal(JSON.parse(readFileSync(format)).version,'0.43.0')
const at=p=>import(pathToFileURL(join(dirname(engine),p)).href)
await at('scripts/format-hook.mjs')

const {parseLightEmitters}=await import(pathToFileURL(formatSource).href)
const {clockHour,clockDayPhase,scheduleSeconds,stepDayClock,checkDayClockState}=await at('src/shared/engine/sim/dayClock.ts')
const {SiteLights}=await at('src/client/engine/fx/SiteLights.ts')
const {Object3D,PointLight,Vector3}=await import(pathToFileURL(join(dirname(req.resolve('three')),'three.module.js')).href)

const rows=parseLightEmitters(data.emitters)
assert.throws(()=>parseLightEmitters({...data.emitters,rows:[...data.emitters.rows,data.emitters.rows[0]]}))
assert.throws(()=>parseLightEmitters({...data.emitters,rows:[{...data.emitters.rows[0],light:{...data.emitters.rows[0].light,decay:1}}]}))
const root=new Object3D(), states=[], banks=new Map(), anchors=[]
for(const row of rows.rows){
 assert(data.emitterGroups[row.parent]===row.id)
 const {light}=row, key=JSON.stringify(light.waves)
 assert(light.shared)
 let bank=banks.get(key)
 if(bank===undefined){
  bank=new SiteLights({flicker:{depth:1,waves:light.waves}})
  const point=bank.addLight(new PointLight(light.colour,0,light.distance,light.decay))
  root.add(point);banks.set(key,bank)
 }
 const a=new Object3D(), state={lit:false}
 a.position.fromArray(data.scenePoints[light.at.point]);anchors.push(a);states.push(state)
 bank.addLamp(a,light.colour,light.gain,light.distance,state,'fire')
}
const lamps=()=>root.children.filter(o=>o.isPointLight)
const fixed=lamps()
assert.equal(fixed.length,4)
let last=false
const cycle=scheduleSeconds(data.clock.schedule)
assert.equal(cycle,1440)
const eye=new Vector3()
const round=n=>+n.toFixed(6)
const capture=()=>lamps().map(l=>({position:l.position.toArray().map(round),intensity:round(l.intensity),distance:l.distance,colour:l.color.getHex()}))
function update(value,seconds,where) {
 const hour=clockHour(data.clock,value)
 const lit=hour>=data.nightGate.from||hour<data.nightGate.to
 if(lit!==last){for(const state of states)state.lit=lit;last=lit}
 eye.fromArray(where)
 for(const bank of banks.values())bank.step(seconds,eye)
 assert.deepEqual(lamps(),fixed)
 assert(states.every(s=>s.lit===lit))
 assert(lamps().every(l=>lit?l.intensity>0:l.intensity===0))
 return lit
}
let value=data.clock.start
const transitions=[],dt=.25
for(let tick=0;tick<=cycle/dt;tick++){
 const was=last,t=tick*dt
 update(value,t,[-32,1.72,9])
 if(last!==was)transitions.push({second:t,lit:last,hour:round(clockHour(data.clock,value))})
 value=stepDayClock(data.clock,value,dt,1,cycle)
}
assert.equal(transitions.length,2)
assert(Math.abs(transitions[0].second-1200)<=dt&&transitions[0].lit)
assert(Math.abs(transitions[1].second-1440)<=dt&&!transitions[1].lit)
const valueFor=(sec)=>sec/cycle
const restored=checkDayClockState(JSON.parse(JSON.stringify({value:valueFor(1300),paused:false,scale:1,cycle,held:null,last:clockDayPhase(data.clock,valueFor(1300))})))
for(const name of ['west.gate.stable.1','west.gate.west.1','west.gate.west.2','west.movers.record','west.obelisk.1','west.obelisk.2','west.obelisk.3','west.obelisk.4']){
 const point=data.scenePoints[name+'.point']
 assert(update(restored.value,1300,point))
 assert(capture().some(l=>l.position.every((p,i)=>Math.abs(p-point[i])<1e-6)&&l.intensity>0),name)
}
const review={}
for(const [k,where] of Object.entries({obelisk:[-45,1.72,8],movers:[-70.8,1.72,-92.4]})){
 update(restored.value,1300,where);const active=capture()
 update(0,0,where);const off=capture()
 assert(off.every(a=>a.intensity===0))
 review[k]={eye:where,night:active,day:off}
}
writeFileSync(out,JSON.stringify({engine:'0.1.44',format:'0.43.0',fixtureSHA256:createHash('sha256').update(raw).digest('hex'),anchors:rows.rows.length,
 stablePointLights:fixed.length,gateTransitions:transitions,quarterSecondSteps:cycle/dt,restoreHour:round(clockHour(data.clock,restored.value)),
 allAnchorsVisited:true,review},null,2)+'\n')

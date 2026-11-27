import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {empty,finish,format,restore} from './record.mjs'

const [input,output]=process.argv.slice(2)
const replay=JSON.parse(readFileSync(input))
const previous=JSON.parse(readFileSync(new URL('../../project/layouts/w3a-native-range-entry-proof.json',import.meta.url)))
assert.equal(replay.geometrySha256,previous.geometrySha256)
assert.equal(replay.engine,previous.engine)
assert.equal(replay.format,previous.format)
assert.equal(replay.closedGate.flags.length,0)
const asc=replay.entryRuns.map(run=>{
  assert.equal(run.airTicks,0)
  assert.equal(run.maxStalls,0)
  assert.equal(run.drillClockTicks,1309)
  return {drill:'six-dummies',started:run.gateToYard.tick,attempts:run.attempts}
})
const initial=empty()
let set=initial
for(const run of asc){
  set=finish(set,run)
  assert.equal(set.lastTicks,1309)
  assert.equal(set.bestTicks,1309)
}
const restored=restore(JSON.stringify(set))
assert.deepEqual(set,restored)
assert.equal(format(initial.bestTicks),'--')
assert.equal(format(restored.bestTicks),'21.82 s')
const case0=asc[0]
assert(replay.negativeControls.length===4&&replay.negativeControls.every(a=>a.gained===0))
assert.deepEqual(finish(initial,{...case0,attempts:[...replay.negativeControls,...case0.attempts]}),restored)
const shift=(r,n)=>({...r,attempts:r.attempts.map(a=>({...a,landingTick:a.landingTick+n}))})
const slow=finish(restored,shift(case0,60)),fast=finish(slow,shift(case0,-30))
assert.deepEqual([slow.bestTicks,slow.lastTicks,fast.bestTicks,fast.lastTicks],[1309,1369,1279,1279])
assert.equal(format(fast.bestTicks),'21.32 s')
for(const r of [
  {...case0,attempts:[]},
  {...case0,attempts:[null]},
  {...case0,attempts:case0.attempts.slice(0,5)},
  {...case0,attempts:[...case0.attempts,case0.attempts[0]]},
  {...case0,attempts:case0.attempts.map((a,i)=>i===2?{...a,slot:'spear'}:a)},
  {...case0,attempts:case0.attempts.map((a,i)=>i===2?{...a,landingTick:case0.started}:a)},
  {...case0,drill:'rifle'},
]){
  assert.equal(finish(restored,r),restored)
  assert.equal(finish(initial,r),initial)
}
for(const bad of ['{','null','{}','{"version":2}','{"version":1,"bestTicks":9,"lastTicks":7}']){
  assert.deepEqual(restore(bad),initial)
}
const fit=JSON.parse(readFileSync(new URL('../../project/layouts/w3a-range-record-face-proof.json',import.meta.url)))
const asset=new URL('../../public/assets/wildshard-art/w3a-range-record-face.glb',import.meta.url)
assert.equal(createHash('sha256').update(readFileSync(asset)).digest('hex'),fit.insertSha256)
const receipt={
  scope:'Native W3a replay consumed by a standalone record/view fixture; no live board/update/persistence host.',
  geometrySha256:replay.geometrySha256,
  faceSha256:fit.insertSha256,
  offsetsM:replay.entryRuns.map(run=>run.gateToYard.offset),
  snapshots:{initial:['--','--','--'],restored:[format(restored.bestTicks),'--','--']},
  observedBestTicks:restored.bestTicks,
  synthetic:{slower:[slow.bestTicks,slow.lastTicks],faster:[fast.bestTicks,fast.lastTicks]},
  rejected:['empty (closed gate)','malformed attempt','unfinished','repeated target','wrong equipment','out-of-order tick','unrelated drill'],
  badSavedStatesRejected:5
}
writeFileSync(output,JSON.stringify(receipt,null,2)+'\n')
console.log(JSON.stringify(receipt))

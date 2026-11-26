// Extend the exact same native lap driver with reimported rail collision.
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync, writeFileSync } from 'node:fs'
import { drive } from '../native-riding-lap/sample.mjs'
const [input,proof,traces]=process.argv.slice(2)
assert(input&&proof&&traces,'Pass exact geometry, proof and render-trace paths')
const raw=readFileSync(input), geometry=JSON.parse(raw)
assert.deepEqual(geometry.rows.map(q=>[q.x,q.z,q.threeYawDeg]),[[-165,-148,90],[-125,-148,90],[-110,-224,-90],[-160,-224,-90]])
const rails=geometry.rows.map(q=>{
  const beam=q.parts.filter(p=>p.name.startsWith('Jump rail stripe')||p.name.startsWith('Pole end cap'))
  assert.equal(q.parts.length,32)
  assert.equal(beam.length,12)
  const crest=Math.max(...beam.flatMap(p=>p.v.filter((_,i)=>i%3===1)))
  const xs=beam.flatMap(p=>p.v.filter((_,i)=>i%3===0))
  assert(Math.abs(crest-1.198)<1e-6)
  return {...q,crest,span:[Math.min(...xs)-1.2,Math.max(...xs)+1.2]}
}).sort((a,b)=>[2,1,4,3].indexOf(a.id)-[2,1,4,3].indexOf(b.id))

const round=x=>+x.toFixed(6)
function at(a,b,x){
  const t=(x-a.x)/(b.x-a.x)
  return {tick:a.tick+(b.tick-a.tick)*t,x,y:a.y+(b.y-a.y)*t,z:a.z+(b.z-a.z)*t,
    hp:Math.min(a.hp,b.hp)}
}
function railResult(q,trace){
  const ss=[]
  let crossing=null
  const toward=(p,x)=>(p.x-x)*q.direction
  for(let i=1;i<trace.length;i++){
    const [a,b]=[trace[i-1],trace[i]]
    // Window selects this straight only; the opposite lap edge is 76 m away.
    if(Math.abs(a.z-q.z)>6||Math.abs(b.z-q.z)>6)continue
    if(toward(a,q.x)<0&&toward(b,q.x)>=0&&!crossing)crossing=at(a,b,q.x)
    for(const x of q.span)if(toward(a,x)<0&&toward(b,x)>=0)ss.push(at(a,b,x))
    if(b.x>=q.span[0]&&b.x<=q.span[1])ss.push(b)
  }
  assert(crossing&&ss.length>=10,q.id)
  const near=trace.filter(p=>Math.abs(p.z-q.z)<6&&Math.abs(p.x-q.x)<12)
  const before=near.find(p=>toward(p,q.x)<-8), after=near.find(p=>toward(p,q.x)>8)
  assert(before&&after,q.id)
  const minY=Math.min(...ss.map(p=>p.y))
  return {rail:q.id,crossing:{...crossing,lateral:round(crossing.z-q.z)},checkedSpanSamples:ss.length,
    crestGapM:round(minY-q.crest),maxAbsSpanLateralM:round(Math.max(...ss.map(p=>Math.abs(p.z-q.z)))),
    peakM:round(Math.max(...near.map(p=>p.y))),initialY:round(before.y),landedY:round(after.y),
    healthy:near.every(p=>p.hp===100),points:near.filter((p,i)=>i%3===0).map(({x,y,z})=>[round(x),round(y),round(z)])}
}
function sample(offset,skip,fit){
  const options={withHp:true,install:(sim,R,groups)=>{
    const world=sim.physics.world
    for(const q of rails){
      for(const p of q.parts)world.createCollider(R.ColliderDesc.trimesh(new Float32Array(p.v),new Uint32Array(p.t))
        .setCollisionGroups(groups('WORLD')))
      const fits=fit==='raw'?[]:q.id===4&&fit==='receiver'?[q.receiver.panel,...q.receiver.stands]:[q.apron]
      for(const part of fits)world.createCollider(R.ColliderDesc.cuboid(...part.half).setTranslation(...part.center)
          .setCollisionGroups(groups('WORLD')))
    }
  }}
  const run=drive(offset,skip,options)
  const samples=rails.map(q=>railResult(q,run.trace))
  assert(run.result)
  assert.deepEqual(run.result.misses,skip?[1]:[])
  assert(run.trace.every(p=>p.hp===100))
  assert(samples.every(q=>Math.abs(q.initialY-.025)<.003&&Math.abs(q.landedY-.025)<.003))
  assert(samples.every(q=>q.maxAbsSpanLateralM<1.2))
  return {offset,skip,fit,score:run.result,samples,maxError:round(run.maxError)}
}

const runs=[]
for(const offset of [-.5,0,.5]) for(const skip of [false,true]) for(const fit of ['raw','flush','receiver']){
  const r=sample(offset,skip,fit)
  console.log({offset,skip,fit,time:r.score.elapsed,gaps:r.samples.map(q=>q.crestGapM),lateral:r.samples.map(q=>q.maxAbsSpanLateralM)})
  runs.push(r)
}
for(const r of runs){
  assert(r.samples.every(q=>r.fit==='raw'?q.peakM<.04:
    r.fit==='flush'&&q.rail===4?q.crestGapM<0:
    q.crestGapM>.025&&q.peakM>1.4),JSON.stringify(r.samples.map(({points,...p})=>p)))
  assert.equal(+(r.score.total-r.score.elapsed).toFixed(3),r.skip?5:0)
}
assert.deepEqual(sample(0,false,'receiver'),runs.find(q=>!q.offset&&!q.skip&&q.fit==='receiver'))
writeFileSync(proof,JSON.stringify({scope:'Stock rider physics with exact rail triangle meshes and optional existing apron box fits, on synthetic flat track. Ring score offline and horizontal only. No rig/rider-body clearance, course install or phone.',
  engine:'0.1.44',gaitsTopMps:13,pins:geometry.pins,geometrySha256:createHash('sha256').update(raw).digest('hex'),
  rails:rails.map(({parts,...p})=>({...p,partCount:parts.length})),runs:runs.map(({samples,...r})=>({...r,samples:samples.map(({points,...p})=>p)}))},null,2)+'\n')
writeFileSync(traces,JSON.stringify(runs.filter(q=>!q.offset&&!q.skip),null,2)+'\n')

import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'

const [shellPath,joinedPath,out]=process.argv.slice(2)
const read=p=>JSON.parse(readFileSync(p,'utf8'))
const before=read(shellPath),after=read(joinedPath)
const six=['West','East','Stable','Movers','Park','Range']
const summarize=d=>{
  assert.equal(d.samples.length,18)
  assert(d.samples.every(r=>r.reachedMouth&&r.longestStall===0))
  assert(!d.wall.completed&&!d.wall.reachedMouth&&d.wall.longestStall===30)
  assert.equal(d.engine,'0.1.44')
  const round=v=>Math.round(v*1000)/1000
  return {geometrySha256:d.geometrySha256,meshes:d.meshes,triangles:d.triangles,
    gates:Object.fromEntries(six.map(name=>{
      let rows=d.samples.filter(r=>r.name===name)
      assert.deepEqual(rows.map(r=>r.offset),[-.42,0,.42])
      return [name,{gateXZ:rows[1].route.at(-2),outsideGoalXZ:rows[1].route.at(-1),
        complete:rows.filter(r=>r.completed).length,grounded:rows.filter(r=>r.longestAir===0).length,
        centerWalkM:round(rows[1].distance),maxAirTicks:Math.max(...rows.map(r=>r.longestAir)),
        centerEndXYZ:rows[1].last.map(round)}]
    })),blockedWest:{stalledTicks:d.wall.longestStall,endXYZ:d.wall.last.map(round)}}
}
const shell=summarize(before),joined=summarize(after)
assert.deepEqual(six.map(g=>shell.gates[g].complete),[3,3,3,3,0,0])
assert.deepEqual(six.map(g=>joined.gates[g].complete),[3,3,3,3,3,3])
assert.deepEqual(six.map(g=>joined.gates[g].grounded),[3,3,3,3,3,3])
writeFileSync(out,JSON.stringify({
  scope:'Input-driven stock player on reconstructed art collision. No new traversal geometry, native install, production spawn, touch or draw-call measurement.',
  engine:'0.1.44',hz:60,testStartXZ:[-120,0],mouthOffsetsM:[-.42,0,.42],shell,joined},null,2)+'\n')

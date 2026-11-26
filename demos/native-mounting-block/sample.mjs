import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const packagePath=req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(packagePath)).version,'0.1.44')
const root=dirname(packagePath)
const at=p=>import(pathToFileURL(join(root,p)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')), 'rapier_wasm3d_bg.wasm')))
const folder=resolve(process.argv[2]), raw=readFileSync(join(folder,'block-collision.json'))
const source=JSON.parse(raw)
const [x,y,z]=source.origin
const modeNames=['exact','treads','nothing']
function bench(offset,mode,reverse=false,save=false,speed=2.2){
  const front=z+2.0, platform=z-.30, begin=reverse?platform:front, goal=reverse?front:z-.12
  const sign=Math.sign(goal-begin),yaw=sign>0?Math.PI:0
  const host=new SimHost({version:SIM_API_VERSION,id:'w10a-block-approach',seed:25,
    ground:{size:500,height:0},player:{at:{x:x+offset,y:reverse?.67:.12,z:begin},yaw,speed},
    entities:[],quests:[],weapon:{id:'fixture-disabled',damage:0}}, {rapier:R,ground:false})
  const p=host.players.get('actor.player'),world=host.physics.world
  const labels=new Map()
  const box=(name,x,y,z,hx,hy,hz)=>{
    const c=world.createCollider(R.ColliderDesc.cuboid(hx,hy,hz).setTranslation(x,y,z).setCollisionGroups(groups('WORLD')))
    labels.set(c.handle,name)
  }
  try{
    box('datum',x,-.25,z,6,.25,6)
    if(mode==='exact')for(const g of source.meshes){
      const c=world.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),new Uint32Array(g.triangles))
        .setCollisionGroups(groups('WORLD')))
      labels.set(c.handle,'block')
    }
    if(mode==='treads')for(const [start,end,h] of [[-.56,-.24,.18],[-.24,.08,.36],[.08,.56,.54]]){
      box('block',x,h*.5,z-(start+end)*.5,.43,h*.5,(end-start)*.5)
    }
    const tick=(s=0)=>host.step(new Map([[p.id,{moveX:0,moveZ:s,yaw}]]))
    for(let i=0;i<45;i++)tick()
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded)
    const frames=[]
    let maxY=0,air=0,stall=0,longestStall=0,blockTicks=0
    const snap=()=>{
      const g=p.motor.result.groundCollider
      return {feet:p.position.toArray(),grounded:p.fall.grounded,support:g?labels.get(g.handle)??null:null}
    }
    for(let i=0;i<220&&Math.abs(goal-p.position.z)>.035;i++){
      const before=p.position.z
      tick(sign*Math.min(1,Math.abs(goal-before)*60/speed))
      const state=snap()
      if(!state.grounded)air++
      stall=Math.abs(state.feet[2]-before)<.002?stall+1:0
      longestStall=Math.max(longestStall,stall)
      blockTicks+=Number(state.grounded&&state.support==='block')
      maxY=Math.max(maxY,state.feet[1])
      if(save&&(i%3===0||stall===30))frames.push(state)
      if(stall>=30)break
    }
    for(let i=0;i<24;i++)tick()
    const end=snap()
    return {mode,offset,reverse,speed,air,longestStall,blockTicks,maxY,end,...(save?{frames}:{})}
  }finally{host.dispose()}
}
const cases=modeNames.flatMap(mode=>[-.25,-.125,0,.125,.25].flatMap(off=>[bench(off,mode),bench(off,mode,true)]))
const traces=modeNames.map(mode=>bench(0,mode,false,true))
assert.deepEqual(traces,modeNames.map(mode=>bench(0,mode,false,true)))
const fast=[-.25,0,.25].map(off=>bench(off,'exact',false,off===0,4.3))
assert([...cases,...fast].every(c=>c.end.grounded&&c.air===0&&c.longestStall===0))
for(const c of [...cases,...fast]){
  const top=c.mode!=='nothing'&&!c.reverse
  assert.equal(c.end.support,top?'block':'datum')
  assert(Math.abs(c.end.feet[1]-(top?.56:.02))<.002,c)
  if(top)assert(c.end.feet[2]>z-.42&&c.end.feet[2]<z-.29,c)
}
const receipt={scope:'Stock walking input around original mounting block at its archive pad. No horse, loan or mounting.',
  engine:'0.1.44',assetSha:source.donor,origin:source.origin,geometrySha256:createHash('sha256').update(raw).digest('hex'),cases,traces,fast}
writeFileSync(join(folder,'walk.json'),JSON.stringify(receipt,null,2)+'\n')
for(const c of cases)console.log(c.mode,c.offset,c.reverse,c.blockTicks,c.air,c.longestStall,c.maxY,c.end)

console.log('full-speed controls:',fast.map(({frames,...c})=>c))

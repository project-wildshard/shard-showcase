import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'

const [dir,out]=process.argv.slice(2)
const proofs={
 'layout.js':'5d019a020361c47187ec889f2bc947f82cd9f98a',
 'placement.js':'6a067ec22a8e07f1d99a9d495d23063d2863ab10',
 'lab.js':'51a3b4bef1f2d4891172164d10893d98d450a3b9',
}
for(const [file,expected] of Object.entries(proofs)){
 const b=readFileSync(join(dir,file))
 assert.equal(createHash('sha1').update(`blob ${b.length}\0`).update(b).digest('hex'),expected,file)
}
const imp=name=>import(pathToFileURL(resolve(dir,name)))
const {ZONES,ARCHES}=await imp('layout.js')
const {place}=await imp('placement.js')
const entry=ARCHES.find(a=>a.band===3)
const {packs,cover}=place()
const dayPacks=packs.filter(p=>p.band===3).map(({x,z,lv,size})=>({x,z,lv,size}))
const rows=cover.filter(c=>c.band===3&&c.kind==='pillars')
assert.equal(rows.length,27)
const round=n=>+n.toFixed(6)
const sq=(x,z,bx,bz)=>Math.hypot(Math.max(0,Math.abs(x)-bx),Math.max(0,Math.abs(z)-bz))
const checks=rows.map(({x,z,ry},i)=>{
 const c=Math.cos(ry),s=Math.sin(ry)
 const local=dayPacks.map(p=>[(p.x-x)*c-(p.z-z)*s,(p.x-x)*s+(p.z-z)*c])
 const full=Math.min(...local.map(([a,b])=>sq(a,b,4.8,.8)))
 const feet=Math.min(...local.flatMap(([a,b])=>[-4,4].map(o=>sq(a-o,b,.8,.8))))
 return {ordinal:i+1,x,z,ry,footprintToPack:round(full),groundPostToPack:round(feet),installedInFixture:full>=8}
})
assert.equal(checks.filter(a=>a.installedInFixture).length,19)
writeFileSync(out,JSON.stringify({
 archive:'Raynos/project-wildshard-singleplayer@ce1cf050b3:art/showcase-template/round-5-blockout',
 proofs,entry,zone:ZONES.find(z=>z.id==='B3'),dayPacks,rows:checks,
 model:{name:'e3-suspended-pillar-screen.glb',sha256:'b97aac0a7b80e50f2c2d066e51e89cbf32c1ccbed65b83cfd776c9b03c65f69e'},
 colliders:[
  {part:'westPost',center:[-4,3.5,0],half:[.8,3.5,.8]},
  {part:'eastPost',center:[4,3.5,0],half:[.8,3.5,.8]},
  {part:'screen',center:[0,4.2,0],half:[3.8,2,.16]},
  {part:'beam',center:[0,6.7,0],half:[4.8,.3,.4]},
 ],
},null,2)+'\n')

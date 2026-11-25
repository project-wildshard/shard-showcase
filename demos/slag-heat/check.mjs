import assert from 'node:assert/strict'
import {mkdirSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {join,resolve} from 'node:path'
import {ageToHeat} from './slag.mjs'
const req=createRequire(process.env.WSC_NODE_PROJECT?join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url)
const {chromium}=req('playwright')
const [, , url, output]=process.argv
assert(url&&output,'Pass a local preview URL and output directory')
mkdirSync(output,{recursive:true})
assert.throws(()=>ageToHeat(Infinity))
assert.equal(ageToHeat(-.01),null)
assert.equal(ageToHeat(0),1)
assert.equal(ageToHeat(5.99),0)
assert.equal(ageToHeat(6),null)
for(let n=1;n<600;n++)assert(ageToHeat(n/100)<=ageToHeat((n-1)/100))
const browser=await chromium.launch({executablePath:process.env.CHROMIUM||undefined,
  args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']})
const issues=[]
try {
  const shots=(view,w,h)=>browser.newPage({viewport:{width:w,height:h},deviceScaleFactor:1})
    .then(async page=>{
      page.on('pageerror',e=>issues.push(e.message))
      page.on('console',m=>{if(m.type()==='error')issues.push(m.text())})
      await page.goto(url+(view==='portrait'?'?portrait':''))
      await page.waitForFunction(()=>Boolean(window.slagPreview),{},{timeout:8000})
      return page
    })
  const d=await shots('detail',1180,744)
  const call=(page,t,view='detail',k=1,isolated=false)=>page.evaluate(
    ([t,view,k,isolated])=>window.slagPreview.snapshot(t,view,k,isolated),[t,view,k,isolated])
  const isolated = await call(d,.45,'detail',12,true)
  assert.equal(isolated.instances,12)
  assert.equal(isolated.calls,1)
  assert.equal(isolated.triangles,703*12)
  const future=await call(d,-.01,'detail',1,true)
  assert.deepEqual(future,{instances:0,calls:0,triangles:0,heat:[]})
  const expired=await call(d,6,'detail',12,true)
  assert.deepEqual(expired,future)
  for(const [name,t] of [['impact',0],['mid',3.8],['cool',5.9],['gone',6]]) {
    await call(d,t)
    await d.screenshot({path:join(output,`detail-${name}.png`)})
  }
  const phone=await shots('portrait',402,874)
  for(const [name,t] of [['impact',0],['cool',5.9],['gone',6]]) {
    await call(phone,t,'portrait')
    await phone.screenshot({path:join(output,`portrait-${name}.png`)})
  }
  assert.deepEqual(issues,[])
  writeFileSync(join(output,'proof.json'),JSON.stringify({durationSeconds:6,population:isolated.instances,
    isolatedDraws:isolated.calls,isolatedTriangles:isolated.triangles,beforeBirth:future,atExpiry:expired,
    renderer:'Headless Chromium / WebGL2 (software rasterizer)',portrait:[402,874],
    samples:[0,.38,2.1,3.8,5.22,5.9,6].map(t=>[t,ageToHeat(t)])},null,2)+'\n')
}finally{await browser.close()}

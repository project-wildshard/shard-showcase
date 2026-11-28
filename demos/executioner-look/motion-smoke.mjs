import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const [url='http://127.0.0.1:5252/demos/executioner-look/',out='/tmp/executioner-motion']=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const dest=new URL(url);dest.searchParams.set('mesh','./guard-study.glb');dest.searchParams.set('motion','guard');
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const rows=[];
try{
 for(const [name,w,h,touch] of [['desktop',1280,720,false],['portrait',402,874,true]]){
  const p=await browser.newPage({viewport:{width:w,height:h},hasTouch:touch,isMobile:touch,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await p.goto(dest.href);
  await p.waitForFunction(()=>['ready','error'].includes(document.querySelector('#stage').dataset.state));
  const read=()=>p.locator('#stage').evaluate(e=>Object.assign({},e.dataset));
  const first=await read();assert.equal(first.state,'ready',await p.locator('#status').textContent());assert.equal(first.motion,'guard-study');
  assert.equal(+first.skinnedMeshes,7);assert(+first.probeVertices>8);assert.equal(+first.clothTravel,0);
  const side=p.getByRole('button',{name:'Cloth side',exact:true});if(touch)await side.tap();else await side.click();
  assert.equal((await read()).view,'left');
  await p.screenshot({path:`${out}/${name}-rest.png`});
  const play=p.getByRole('button',{name:'Play guard study'});if(touch)await play.tap();else await play.click();
  await p.waitForFunction(()=>+document.querySelector('#stage').dataset.motionProgress===1);
  const done=await read();assert(+done.clothTravel>.05&&+done.clothTravel<.80);
  await p.screenshot({path:`${out}/${name}-guard.png`});
  const range=p.getByRole('slider',{name:'Guard pose progression'});await range.press('Home');
  await p.waitForFunction(()=>+document.querySelector('#stage').dataset.motionProgress===0);
  const reset=await read();assert.equal(+reset.clothTravel,0);
  assert.deepEqual(errors,[]);
  rows.push({viewport:[w,h],trustedTouch:touch,skinnedMeshes:+done.skinnedMeshes,weightedVerticesSampled:+done.probeVertices,
   triangles:+done.triangles,animationSeconds:+done.motionSeconds,maxClothTravelM:+done.clothTravel,reset:true});
  await p.close();
 }
 console.log(JSON.stringify({diagnosticOnly:true,actualWeightedGltf:true,rows},null,2));
}finally{await browser.close();}

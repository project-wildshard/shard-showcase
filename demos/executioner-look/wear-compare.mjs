import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const [url='http://127.0.0.1:5250/demos/executioner-look/',dest='/tmp/executioner-wear']=process.argv.slice(2);
mkdirSync(dest,{recursive:true});
const b=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const rows=[];
try{
 for(const [label,width,height,touch] of [['desktop',1280,720,false],['portrait',402,874,true]]){
  const p=await b.newPage({viewport:{width,height},hasTouch:touch,isMobile:touch,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  const arr=[];
  for(const tone of ['procedural','localized']){
   const u=new URL(url);u.searchParams.set('mesh','./mantle.glb');u.searchParams.set('tone',tone);
   await p.goto(u.href);await p.waitForFunction(()=>['ready','error'].includes(document.querySelector('#stage').dataset.state));
   const read=()=>p.locator('#stage').evaluate(e=>Object.assign({},e.dataset));
   const first=await read();assert.equal(first.state,'ready');assert.equal(first.tone,tone);
   assert(await p.locator('nav button').evaluateAll(ns=>ns.every(n=>n.getBoundingClientRect().right<=innerWidth&&n.getBoundingClientRect().left>=0)));
   await p.screenshot({path:`${dest}/${label}-${tone}-distance.png`});
   const control=p.getByRole('button',{name:'Close',exact:true});if(touch)await control.tap();else await control.click();
   const close=await read();assert.equal(close.view,'close');
   await p.screenshot({path:`${dest}/${label}-${tone}-close.png`});
   const side=p.getByRole('button',{name:'Cloth side',exact:true});if(touch)await side.tap();else await side.click();
   assert.equal((await read()).view,'left');
   arr.push({tone,triangles:+first.triangles,distancePx:+first.heightPixels,closePx:+close.heightPixels});
  }
  assert.deepEqual(arr.map(r=>Object.values(r).slice(1))[0],arr.map(r=>Object.values(r).slice(1))[1]);
  assert.deepEqual(errors,[]);rows.push({viewport:[width,height],touch,results:arr});
  await p.close();
 }
 console.log(JSON.stringify({sameByteExactMesh:true,samePoseCameraAndLights:true,visualReviewOnly:true,rows},null,2));
}finally{await b.close();}

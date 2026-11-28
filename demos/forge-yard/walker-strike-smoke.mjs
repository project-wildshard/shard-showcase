import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
import {WEAPONS} from './arena.mjs';
import {RELEASE_POSE,SIGNATURE_STRIKES,walkerStrike} from './walker-strike.mjs';
const [url='http://127.0.0.1:5187/demos/forge-yard/',out='/tmp/walker-strikes']=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
try{
 const p=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.addInitScript(()=>{
  const raf=requestAnimationFrame.bind(window);window.swingProof=null;
  window.requestAnimationFrame=apply=>raf(t=>{
   apply(t);
   const y=document.querySelector('#yard'),record=window.swingProof,d=y?.dataset;
   if(!record||d?.equipped!==record.id||!d.heroStrikePhase)return;
   const capture=()=>y.querySelector('canvas').toDataURL();
   if(record.photo&&!record.wind&&+d.heroStrikePhase>.16&&+d.heroStrikePhase<.39)record.wind=capture();
   if(!record.release&&+d.fxImpact>record.start){
    record.release={pose:d.heroClip,phase:+d.heroStrikePhase,time:+d.heroStrikeTime,release:+d.heroStrikeRelease,
     grip:d.gripLocal,hp:+document.querySelector('#enemy-hp').textContent,image:record.photo?capture():null};
   }
  });
 });
 const wait=(fn,arg)=>p.waitForFunction(fn,arg,{timeout:16000});
 await p.goto(url);await wait(()=>document.querySelector('#yard').dataset.state==='ready');
 const y=p.locator('#yard'),stick=await p.locator('#stick').boundingBox(),cdp=await p.context().newCDPSession(p);
 const touch=dy=>cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:stick.x+stick.width/2,y:stick.y+stick.height/2+dy*31}]});
 const stop=()=>cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 const report=[];
 for(const w of WEAPONS){
  await p.locator('#reset').tap();
  await p.locator('#weapon').selectOption(w.id);
  await wait(id=>document.querySelector('#yard').dataset.equipped===id,w.id);
  await touch(-1);await wait(()=>{const d=document.querySelector('#yard').dataset;return Math.hypot(d.playerX-d.enemyX,d.playerZ-d.enemyZ)<1.74;});await stop();
  const hp=Number(await p.locator('#enemy-hp').textContent()),serial=Number(await y.getAttribute('data-fx-impact'));
  await p.evaluate(o=>{window.swingProof=o;},{id:w.id,start:serial,photo:!!SIGNATURE_STRIKES[w.id]});
  await p.locator('#attack').tap();
  await wait(()=>window.swingProof?.release);
  const o=await p.evaluate(()=>window.swingProof);const {image,...result}=o.release;
  assert.equal(result.pose,walkerStrike(w),w.id);
  assert.equal(result.phase,+RELEASE_POSE.toFixed(5),w.id);
  assert.equal(result.time,result.release,w.id);
  assert.equal(hp-result.hp,w.power,w.id);
  const grip=result.grip.split(',').map(Number);assert(grip.length===3&&grip.every(Number.isFinite));
  if(o.photo){
   assert(o.wind?.length>12000&&image?.length>12000,w.id+' captures');
   for(const [stage,data] of [['wind',o.wind],['release',image]])
    writeFileSync(out+'/'+w.id+'-'+stage+'.png',Buffer.from(data.split(',')[1],'base64'));
  }
  report.push({id:w.id,weapon:w.name,clip:result.pose,authoredPhase:result.phase,actualReleaseMs:Math.round(result.release*1000),
   oldUniformPeakMs:Math.round(w.cycle*RELEASE_POSE*1000),damage:hp-result.hp});
  await wait(()=>!document.querySelector('#yard').dataset.heroStrikePhase);
 }
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({trustedTouch:true,viewport:[402,874],report,errors},null,2));
}finally{await browser.close();}

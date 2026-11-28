import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
const url=process.argv[2]??'http://127.0.0.1:5187/demos/forge-yard/';
const out=process.argv[3]??'/tmp/ram-counter';mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
try{
 const p=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.addInitScript(()=>{
  const raf=requestAnimationFrame.bind(window);window.counterFrames={};
  window.requestAnimationFrame=fn=>raf(t=>{
   fn(t);
   const a=document.querySelector('#yard'),d=a?.dataset;
   const record=k=>{if(!window.counterFrames[k])window.counterFrames[k]={image:a.querySelector('canvas').toDataURL(),cue:document.querySelector('#notice').textContent};};
   if(d?.counterOpen==='1')record('open');
   if(d?.counterHit&&+d.fxAgeMs>=70&&+d.fxParticles)record('hit');
  });
 });
 const wait=(fn,arg)=>p.waitForFunction(fn,arg,{timeout:14000});
 await p.goto(url);await wait(()=>document.querySelector('#yard').dataset.state==='ready');
 await p.locator('#rival').selectOption('3');await wait(()=>document.querySelector('#yard').dataset.enemy==='WSC-ENM-004');
 await p.locator('#weapon').selectOption('021');await wait(()=>document.querySelector('#yard').dataset.equipped==='021');
 const s=await p.locator('#stick').boundingBox(),cdp=await p.context().newCDPSession(p);
 const touch=(dx,dy)=>cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:s.x+s.width/2+dx*31,y:s.y+s.height/2+dy*31}]});
 const stop=()=>cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 await touch(0,-1);await wait(()=>document.querySelector('#yard').dataset.pose==='Windup');await stop();
 await touch(1,0);await wait(()=>+document.querySelector('#yard').dataset.playerX>1.63);await stop();
 await wait(()=>document.querySelector('#yard').dataset.counterOpen==='1');
 const before=+await p.locator('#enemy-hp').textContent();
 await p.locator('#attack').tap();
 await wait(()=>document.querySelector('#yard').dataset.counterHit==='27');
 await wait(()=>window.counterFrames.hit);
 const state=await p.locator('#yard').evaluate(o=>({opening:o.dataset.counterOpen,player:+document.querySelector('#hero-hp').textContent,rival:+document.querySelector('#enemy-hp').textContent}));
 assert.equal(state.player,120);assert.equal(state.rival,before-27);assert.equal(state.opening,'0');
 for(const key of ['open','hit']){
  const f=await p.evaluate(k=>window.counterFrames[k],key);
  assert.match(f.cue,key==='open'?/ARMOR OPEN/:/COUNTER/);assert(f.image.length>14000);
  writeFileSync(out+'/'+key+'.png',Buffer.from(f.image.split(',')[1],'base64'));
 }
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({viewport:[402,874],trustedTouch:true,weapon:'Beacon Lance',ordinaryDamage:20,counterDamage:27,health:state.player,openingConsumed:true,errors},null,2));
}finally{await browser.close();}

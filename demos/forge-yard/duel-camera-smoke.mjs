import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const url=process.argv[2]??'http://127.0.0.1:5187/demos/forge-yard/';
const out=process.argv[3]??'/tmp/duel-camera';mkdirSync(out,{recursive:true});
const baseline=process.argv[4];
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const report=[];
try{
 for(const [name,width,height] of [...(baseline?[['before',402,874]]:[]),['portrait',402,874],['wide',960,680]]){
  const p=await browser.newPage({viewport:{width,height},hasTouch:true,isMobile:true,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  if(name==='before')await p.route('**/dist/yard.js',r=>r.fulfill({path:baseline,contentType:'text/javascript'}));
  const wait=(fn,arg)=>p.waitForFunction(fn,arg,{timeout:16000});
  await p.addInitScript(()=>{
   const orig=requestAnimationFrame.bind(window);
   window.holdFraming=false;
   window.bounds=[0,0,0];
   window.requestAnimationFrame=fn=>orig(t=>{
    fn(t);
    const d=document.querySelector('#yard')?.dataset;
    if(!window.holdFraming||!d?.playerViewX||!d.enemyViewX)return;
    const b=window.bounds;
    b[0]=Math.max(b[0],Math.abs(+d.playerViewX),Math.abs(+d.enemyViewX));
    b[1]=Math.max(b[1],Math.abs(+d.playerViewY),Math.abs(+d.enemyViewY));b[2]++;
   });
  });
  await p.goto(url);await wait(()=>document.querySelector('#yard').dataset.state==='ready');
  const stick=await p.locator('#stick').boundingBox(),c=await p.context().newCDPSession(p);
  const start=(x,y)=>c.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:stick.x+stick.width/2+x*31,y:stick.y+stick.height/2+y*31}]});
  const end=()=>c.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  const distance=d=>{const e=document.querySelector('#yard').dataset;return Math.hypot(+e.playerX-+e.enemyX,+e.playerZ-+e.enemyZ)<d;};
  const state=()=>p.locator('#yard').evaluate(o=>{const d=o.dataset;return {cameraDistance:+d.cameraDistance||null,x:+d.playerX,z:+d.playerZ,ex:+d.enemyX,ez:+d.enemyZ,pose:d.pose};});
  await p.evaluate(()=>{window.holdFraming=true;});
  await start(0,-1);await wait(distance,2.68);await end();
  await p.waitForTimeout(270);const approach=await state();
  await p.screenshot({path:out+'/'+name+'-approach.png'});
  await start(0,-1);await wait(distance,1.83);await end();
  let hp=+await p.locator('#enemy-hp').textContent();
  await p.locator('#attack').tap();await wait(h=>+document.querySelector('#enemy-hp').textContent<h,hp);
  await p.locator('#rival').selectOption('3');await wait(()=>document.querySelector('#yard').dataset.enemy==='WSC-ENM-004');
  await start(0,-1);await wait(distance,5.90);await end();
  await wait(()=>document.querySelector('#yard').dataset.pose==='Windup');
  await p.screenshot({path:out+'/'+name+'-ram-tell.png'});
  await p.locator('#dodge').tap();await wait(()=>document.querySelector('#yard').dataset.heroClip==='Dodge');
  await wait(()=>['Attack','Recover'].includes(document.querySelector('#yard').dataset.pose));
  const bounds=await p.evaluate(()=>window.bounds);
  assert(bounds[2]>15);if(name!=='before'){assert(bounds[0]<=.86);assert(bounds[1]<=.70);assert(approach.cameraDistance>=6.35&&approach.cameraDistance<11,JSON.stringify(approach));}
  assert.deepEqual(errors,[]);
  report.push({name,viewport:[width,height],approach,maxAbsNdc:bounds.slice(0,2),sampledFrames:bounds[2],sentryHit:true,ramTellAndDodge:true,errors});
  await p.close();
 }
 console.log(JSON.stringify({trustedTouch:true,report},null,2));
}finally{await browser.close();}

import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
const url=process.argv[2]??'http://127.0.0.1:5187/demos/forge-yard/';
const out=process.argv[3]??'/tmp/ram-armor';mkdirSync(out,{recursive:true});
const prior=process.argv[4];
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
const report=[];
try{
 for(const variant of [...(prior?['before']:[]),'after']){
  const p=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  if(variant==='before')await p.route('**/ram.glb',r=>r.fulfill({path:prior,contentType:'model/gltf-binary'}));
  const wait=(fn,arg)=>p.waitForFunction(fn,arg,{timeout:16000});
  await p.addInitScript(()=>{
   const raf=requestAnimationFrame.bind(window);
   window.requestAnimationFrame=run=>raf(t=>{
    run(t);
    const yard=document.querySelector('#yard');
    if(!window.windupFrame&&yard?.dataset.enemy==='WSC-ENM-004'&&yard.dataset.pose==='Windup'){
     window.windupCue=document.querySelector('#notice').textContent;
     window.windupFrame=yard.querySelector('canvas').toDataURL();
    }
   });
  });
  await p.goto(url);await wait(()=>document.querySelector('#yard').dataset.state==='ready');
  await p.locator('#rival').selectOption('3');await wait(()=>document.querySelector('#yard').dataset.enemy==='WSC-ENM-004');
  const s=await p.locator('#stick').boundingBox(),cdp=await p.context().newCDPSession(p);
  const touch=(dx,dy)=>cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:s.x+s.width/2+dx*31,y:s.y+s.height/2+dy*31}]});
  const stop=()=>cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  const pose=name=>wait(n=>document.querySelector('#yard').dataset.pose===n,name);
  await touch(0,-1);await pose('Windup');await stop();
  await touch(1,0);
  await wait(()=>+document.querySelector('#yard').dataset.playerX>1.75);
  await stop();await pose('Recover');
  const [cue,frame]=await p.evaluate(()=>[window.windupCue,window.windupFrame]);
  assert.match(cue,/CHARGE/);assert(frame.length>14000);
  writeFileSync(out+'/'+variant+'-ram-windup.png',Buffer.from(frame.split(',')[1],'base64'));
  const hp=+await p.locator('#hero-hp').textContent();
  assert.equal(hp,120,'sidestep off the locked lane should avoid the charge');
  assert.deepEqual(errors,[]);
  report.push({variant,cue,healthAfterSidestep:hp,errors});
  await p.close();
 }
 console.log(JSON.stringify({portrait:[402,874],trustedTouch:true,report},null,2));
}finally{await browser.close();}

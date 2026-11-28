import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
const [url='http://127.0.0.1:5243/demos/forge-yard/',out='/tmp/snare-smoke']=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const trials=[];
try{
 for(const mode of ['stay','step-out']){
  const p=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.addInitScript(()=>{
   const raf=requestAnimationFrame.bind(window);window.snare={};
   window.requestAnimationFrame=run=>raf(t=>{
    run(t);
    const y=document.querySelector('#yard'),d=y?.dataset,phase=d?.snarePhase;
    if(!phase||window.snare[phase])return;
    window.snare[phase]={hp:+document.querySelector('#hero-hp').textContent,pose:d.pose,radius:+d.snareRadius,
     distance:+Math.hypot(d.playerX-d.snareX,d.playerZ-d.snareZ).toFixed(3),
     image:y.querySelector('canvas').toDataURL()};
   });
  });
  const wait=fn=>p.waitForFunction(fn,{},{timeout:25000});
  await p.goto(url);
  await wait(()=>document.querySelector('#yard').dataset.state==='ready');
  await p.locator('#rival').selectOption({label:'Breakwater Snare'});
  const b=await p.locator('#stick').boundingBox(),cdp=await p.context().newCDPSession(p);
  await wait(()=>window.snare.windup);
  if(mode==='step-out'){
   await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:b.x+b.width/2+32,y:b.y+b.height/2}]});
   await wait(()=>+document.querySelector('#yard').dataset.playerX>=1.24);
   await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  }
  await wait(()=>window.snare.release);
  const frames=await p.evaluate(()=>window.snare);
  assert.equal(frames.release.hp,mode==='stay'?104:120);
  assert.equal(frames.release.radius,.93);
  assert.equal(frames.release.distance<.93,mode==='stay');
  assert.equal(frames.release.pose,'Attack');
  assert.deepEqual(errors,[]);
  for(const [k,f] of Object.entries(frames)){
   assert(f.image.length>14000);
   writeFileSync(out+'/'+mode+'-'+k+'.png',Buffer.from(f.image.split(',')[1],'base64'));
   delete f.image;
  }
  trials.push({mode,frames,errors});await p.close();
 }
 console.log(JSON.stringify({viewport:[402,874],trustedTouch:true,trials},null,2));
}finally{await browser.close();}

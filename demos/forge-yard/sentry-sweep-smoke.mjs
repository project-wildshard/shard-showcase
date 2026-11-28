import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';

const [url='http://127.0.0.1:5187/demos/forge-yard/',out='/tmp/sentry-sweep',prior]=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
const trials=[];
try{
 for(const mode of [...(prior?['before']:[]),'inside','outside']){
  const p=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  if(mode==='before')await p.route('**/dist/yard.js',r=>r.fulfill({path:prior,contentType:'text/javascript'}));
  await p.addInitScript(()=>{
   const raf=requestAnimationFrame.bind(window);
   window.requestAnimationFrame=run=>raf(t=>{
    run(t);
    const y=document.querySelector('#yard'),a=y?.dataset;
    if(!a)return;
    const gap=()=>Math.hypot(Number(a.playerX)-Number(a.enemyX),Number(a.playerZ)-Number(a.enemyZ));
    const phase=a.sweepPhase,remaining=Number(a.sweepRemaining);
    const capture=name=>{
     window.sweepFrames??={};
     window.sweepFrames[name]??=y.querySelector('canvas').toDataURL();
    };
    if(a.pose==='Windup'&&(phase==='windup'?remaining<.63&&remaining>.48:!phase&&gap()>1.63))capture('warning');
    if(phase==='release'&&!window.firstRelease){window.firstRelease={gap:gap(),radius:Number(a.sweepRadius)};capture('release');}
   });
  });
  await p.goto(url);
  const wait=(fn,arg)=>p.waitForFunction(fn,arg,{timeout:17000});
  await wait(()=>document.querySelector('#yard').dataset.state==='ready');
  const stick=await p.locator('#stick').boundingBox(),cdp=await p.context().newCDPSession(p);
  const touch=dy=>cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:stick.x+stick.width/2,y:stick.y+stick.height/2+dy*31}]});
  const stop=()=>cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await touch(-1);
  await wait(()=>document.querySelector('#yard').dataset.pose==='Windup');await stop();
  await touch(1);
  await wait(target=>{
   const a=document.querySelector('#yard').dataset;
   return Math.hypot(Number(a.playerX)-Number(a.enemyX),Number(a.playerZ)-Number(a.enemyZ))>=target;
  },mode==='outside'?2.15:1.68);
  await stop();
  await wait(()=>document.querySelector('#yard').dataset.pose==='Recover');
  const [result,frames]=await p.evaluate(()=>[window.firstRelease,window.sweepFrames]);
  const hp=Number(await p.locator('#hero-hp').textContent());
  assert.equal(hp,mode==='outside'?120:102);
  if(mode!=='before'){
   assert.equal(result.radius,2.07);
   assert.equal(result.gap>result.radius,mode==='outside');
  }
  assert.deepEqual(errors,[]);
  assert(frames?.warning?.length>14000);
  for(const [name,frame] of Object.entries(frames))
   writeFileSync(out+'/'+mode+'-'+name+'.png',Buffer.from(frame.split(',')[1],'base64'));
  trials.push({mode,gapAtRelease:result?.gap??null,displayedRadius:result?.radius??null,healthAfterSweep:hp,pageErrors:errors});
  await p.close();
 }
 console.log(JSON.stringify({viewport:[402,874],trustedTouch:true,trials},null,2));
}finally{await browser.close();}

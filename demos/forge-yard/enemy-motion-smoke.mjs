import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
const out=process.argv[3]??'/tmp/enemy-motion';mkdirSync(out,{recursive:true});
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
try{
 const page=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>{
  const raf=requestAnimationFrame.bind(window);
  let prior='',frames=0;
  window.poses=[];window.motionFrames={};
  window.requestAnimationFrame=run=>raf(now=>{
   run(now);
   const yard=document.querySelector('#yard'),d=yard?.dataset;
   if(!d?.pose)return;
   if(d.pose!==prior){
    frames=0;prior=d.pose;
    window.poses.push({pose:d.pose,cue:d.variantCue,variant:d.variant});
   }
   if(['Turn','Attack','Special'].includes(prior)&&++frames===5&&!window.motionFrames[d.variant+prior]){
    window.motionFrames[d.variant+prior]=yard.querySelector('canvas').toDataURL();
   }
  });
 });
 const wait=(fn,arg)=>page.waitForFunction(fn,arg,{timeout:13000});
 await page.goto(process.argv[2]??'http://127.0.0.1:5187/demos/forge-yard/');
 await wait(()=>document.querySelector('#yard').dataset.state==='ready');
 await page.locator('#variant').selectOption('echo');
 await wait(()=>document.querySelector('#yard').dataset.variant==='echo');
 const box=await page.locator('#stick').boundingBox(),x=box.x+box.width/2,y=box.y+box.height/2;
 const cdp=await page.context().newCDPSession(page);
 const stick=(dx,dy)=>cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:x+dx*31,y:y+dy*31}]});
 const stop=()=>cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 await stick(0,-1);
 await wait(()=>{const d=document.querySelector('#yard').dataset;return Math.hypot(+d.playerX-+d.enemyX,+d.playerZ-+d.enemyZ)<1.51;});
 await stop();
 await wait(()=>window.motionFrames.echoSpecial);
 const echo=await page.evaluate(()=>window.poses.filter(x=>x.variant==='echo'));
 assert(echo.findIndex(x=>x.pose==='Attack')>=0);
 assert(echo.some((x,i)=>x.pose==='Special'&&x.cue==='echo'&&echo[i-1]?.pose==='Windup'));
 await page.locator('#variant').selectOption('');
 await wait(()=>document.querySelector('#yard').dataset.variant==='');
 await stick(0,-1);
 await wait(()=>{const d=document.querySelector('#yard').dataset;return Math.hypot(+d.playerX-+d.enemyX,+d.playerZ-+d.enemyZ)<1.51;});
 await stop();await wait(()=>document.querySelector('#yard').dataset.pose==='Recover');
 await stick(1,0);
 await wait(()=>window.motionFrames.Turn);
 await stop();
 const normal=await page.evaluate(()=>window.poses.filter(x=>x.variant===''));
 assert(normal.some(x=>x.pose==='Turn'));assert(!normal.some(x=>x.pose==='Special'));
 for(const id of ['echoAttack','echoSpecial','Turn']){
  const url=await page.evaluate(id=>window.motionFrames[id],id);
  assert(url.length>14000);writeFileSync(out+'/'+id+'.png',Buffer.from(url.split(',')[1],'base64'));
 }
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({trustedTouch:true,viewport:[402,874],enemy:'WSC-ENM-001',echo,normal,errors},null,2));
}finally{await browser.close();}

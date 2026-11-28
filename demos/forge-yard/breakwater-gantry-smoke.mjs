import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
const [url='http://127.0.0.1:5240/demos/forge-yard/',out='/tmp/gantry-smoke',prior]=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const captures=[];
try{
 for(const mode of [...(prior?['before']:[]),'after','foundry']){
  const p=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  if(mode==='before')await p.route('**/dist/yard.js',r=>r.fulfill({path:prior,contentType:'text/javascript'}));
  const wait=(fn,arg)=>p.waitForFunction(fn,arg,{timeout:32000});
  await p.goto(url+(mode==='foundry'?'':'?arena=breakwater'));
  await wait(()=>document.querySelector('#yard').dataset.state==='ready');
  const read=()=>p.locator('#yard').evaluate(y=>Object.fromEntries(Object.entries(y.dataset).filter(([k])=>/^(gantry|cargo|playerView|enemyView|scene)/.test(k))));
  if(mode==='after'){
   await wait(()=>{const d=document.querySelector('#yard').dataset;return +d.gantryDrop<.48&&+d.gantryX>-8.38;});
   const a=await read();
   assert(+a.gantryTriangles<2500);assert(Math.abs(+a.cargoViewX)<1&&Math.abs(+a.cargoViewY)<.84,JSON.stringify(a));
   // Grab the first composition before moving the actual touch stick.
   await p.screenshot({path:out+'/after-haul.png'});
   const b=await p.locator('#stick').boundingBox(),cdp=await p.context().newCDPSession(p);
   const before=await p.locator('#yard').getAttribute('data-player-z');
   await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:b.x+b.width/2,y:b.y+b.height/2-31}]});
   await wait(z=>+document.querySelector('#yard').dataset.playerZ<+z-1.5,before);
   await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
   await wait(x=>+document.querySelector('#yard').dataset.gantryX>+x+1.5,a.gantryX);
   const bPose=await read();
   for(const who of ['player','enemy'])assert(Math.abs(+bPose[who+'ViewX'])<1&&Math.abs(+bPose[who+'ViewY'])<1);
   await p.screenshot({path:out+'/after-moved.png'});
   captures.push({mode,first:a,second:bPose,touchForwardMeters:+(before-await p.locator('#yard').getAttribute('data-player-z')).toFixed(2),errors});
  }else{
   await wait(()=>document.querySelector('#yard').dataset.cameraDistance);
   const fields=await read();assert(!fields.gantryX);captures.push({mode,fields,errors});
   if(mode==='before')await p.screenshot({path:out+'/before.png'});
  }
  assert.deepEqual(errors,[]);await p.close();
 }
 console.log(JSON.stringify({viewport:[402,874],captures},null,2));
}finally{await browser.close();}

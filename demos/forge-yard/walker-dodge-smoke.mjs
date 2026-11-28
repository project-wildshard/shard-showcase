import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
const [url='http://127.0.0.1:5244/demos/forge-yard/',out='/tmp/walker-dodge',js,glb]=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const results=[];
try{
 for(const mode of [...(js&&glb?['before']:[]),'after']){
  const p=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  if(mode==='before'){
   await p.route('**/dist/yard.js',r=>r.fulfill({path:js,contentType:'text/javascript'}));
   await p.route('**/forge-walker/walker.glb',r=>r.fulfill({path:glb,contentType:'model/gltf-binary'}));
  }
  await p.addInitScript(()=>{
   const raf=requestAnimationFrame.bind(window);window.dodge={frames:{}};
   requestAnimationFrame=run=>raf(t=>{
    run(t);
    const y=document.querySelector('#yard'),d=y?.dataset;
    if(!d||!window.dodge.start)return;
    const z=+d.playerZ,meters=window.dodge.start-z;
    if(d.heroClip==='Dodge'){
     window.dodge.started=true;
     for(const [name,m] of [['load',.48],['tuck',1.28],['plant',1.76]]){
      if(meters+1e-6<m||window.dodge.frames[name])continue;
      window.dodge.frames[name]={meters:+meters.toFixed(3),phase:d.dodgePhase==null?null:+d.dodgePhase,image:y.querySelector('canvas').toDataURL()};
     }
    }else if(window.dodge.started&&!window.dodge.end)window.dodge.end={meters:+meters.toFixed(3),clip:d.heroClip};
   });
  });
  await p.goto(url);
  const wait=fn=>p.waitForFunction(fn,null,{timeout:19000});
  await wait(()=>document.querySelector('#yard').dataset.state==='ready'&&+document.querySelector('#yard').dataset.playerZ>5.5);
  await p.evaluate(()=>window.dodge.start=+document.querySelector('#yard').dataset.playerZ);
  await p.locator('#dodge').tap();
  await wait(()=>window.dodge.end);
  const r=await p.evaluate(()=>window.dodge);
  assert.equal(r.end.meters,2.4);
  assert.equal(r.end.clip,'Idle');
  for(const [name,f] of Object.entries(r.frames)){
   assert(f.image.length>14000);
   if(mode==='after')assert(Math.abs(f.phase-Math.min(1,f.meters/(9.6*.245)))<.004);
   writeFileSync(out+'/'+mode+'-'+name+'.png',Buffer.from(f.image.split(',')[1],'base64'));
   delete f.image;
  }
  assert.equal(Object.keys(r.frames).length,3);assert.deepEqual(errors,[]);
  results.push({mode,...r,errors});await p.close();
 }
 console.log(JSON.stringify({viewport:[402,874],trustedTouch:true,results},null,2));
}finally{await browser.close();}

import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const [url='http://127.0.0.1:5245/demos/forge-yard/',out='/tmp/foundry-wall',prior]=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const results=[];
try{
 for(const mode of [...(prior?['before']:[]),'after','coast']){
  const p=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  if(mode==='before')await p.route('**/dist/yard.js',r=>r.fulfill({path:prior,contentType:'text/javascript'}));
  const wait=(fn,arg)=>p.waitForFunction(fn,arg,{timeout:23000});
  await p.goto(url+(mode==='coast'?'?arena=breakwater':''));
  await wait(()=>document.querySelector('#yard').dataset.state==='ready');
  const yard=p.locator('#yard'),b=await p.locator('#stick').boundingBox(),cdp=await p.context().newCDPSession(p);
  // First touch advances toward the far wall until both rigs enter the narrower camera.
  const move=()=>cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:b.x+b.width/2,y:b.y+b.height/2-32}]});
  const stop=()=>cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  let damage=null;
  if(mode!=='coast'){
   await move();
   await wait(()=>+document.querySelector('#yard').dataset.playerZ<3.77);
   await stop();
   await p.screenshot({path:out+'/'+mode+'-portrait.png'});
   if(mode==='after'){
    await move();
    await wait(()=>{const d=document.querySelector('#yard').dataset;return Math.hypot(d.playerX-d.enemyX,d.playerZ-d.enemyZ)<1.8;});
    await stop();
    const h=+await p.locator('#enemy-hp').textContent();
    await p.locator('#attack').tap();
    await wait(before=>+document.querySelector('#enemy-hp').textContent<before,h);
    damage=h-(+await p.locator('#enemy-hp').textContent());
    assert.equal(damage,19);
   }
  }
  const d=await yard.evaluate(y=>Object.fromEntries(Object.entries(y.dataset).filter(([k])=>/^(wallModules|scene|playerView|enemyView)/.test(k))));
  assert.equal(d.wallModules,mode==='after'?'3':undefined);assert.equal(d.sceneCover,'4');
  assert.deepEqual(errors,[]);
  results.push({mode,...d,damage,errors});await p.close();
 }
 console.log(JSON.stringify({viewport:[402,874],trustedTouch:true,results},null,2));
}finally{await browser.close();}

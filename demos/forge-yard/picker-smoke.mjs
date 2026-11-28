import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const url=process.argv[2]??'http://127.0.0.1:5191/demos/forge-yard/';
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const b=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
try{
 const page=await b.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
 let keels=0;const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/dock-terminal/keel.glb',async r=>++keels===1?
  r.fulfill({status:503,body:'Temporary failure injected by the test'}):r.continue());
 await page.goto(url);const d=page.locator('#yard'),rival=page.locator('#rival');
 await page.waitForFunction(()=>document.querySelector('#yard').dataset.state==='ready');
 assert.equal(await rival.locator('option').count(),20);
 await page.locator('#variant').selectOption('echo');
 await rival.selectOption('19');
 await page.waitForFunction(()=>document.querySelector('#notice').textContent.includes('Select it or tap Next to retry'));
 assert.equal(await d.getAttribute('data-enemy'),'WSC-ENM-001-echo');
 assert.equal(await rival.inputValue(),'0');
 await rival.selectOption('19');
 await page.waitForFunction(()=>document.querySelector('#yard').dataset.enemy==='WSC-ENM-020-echo');
 assert.equal(await rival.inputValue(),'19');
 assert(Number(await d.getAttribute('data-variant-parts'))>0);
 await page.locator('#reset').tap();assert.equal(await rival.inputValue(),'19');
 await page.locator('#next').tap();
 await page.waitForFunction(()=>document.querySelector('#yard').dataset.enemy==='WSC-ENM-001-echo');
 assert.equal(await rival.inputValue(),'0');
 assert.equal(keels,2);assert.deepEqual(errors,[]);
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 console.log(JSON.stringify({viewport:[402,874],rivalOptions:20,directChoice:'WSC-ENM-020-echo',firstRequestStatus:503,rollbackAndRetry:true,
   variantRetained:true,keelRequests:keels,nextWraps:true,errors},null,2));
}finally{await b.close();}

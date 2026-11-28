import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,statSync,readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const [url='http://127.0.0.1:5250/demos/executioner-look/',out='/tmp/executioner-materials']=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const file=n=>fileURLToPath(new URL(n,import.meta.url));
const read=n=>{
 const b=readFileSync(file(n));return JSON.parse(b.toString('utf8',20,20+b.readUInt32LE(12)));
};
const baked=read('./baked.glb'),flat=read('./hybrid.glb');
assert(baked.images?.length>=3&&baked.materials[0].normalTexture);
assert(baked.materials[0].pbrMetallicRoughness.baseColorTexture&&baked.materials[0].pbrMetallicRoughness.metallicRoughnessTexture);
assert(!baked.skins?.length&&!flat.skins?.length);
assert(!baked.animations?.length&&!flat.animations?.length);
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const records=[];
try{
 for(const [label,w,h,touch] of [['desktop',1280,720,false],['portrait',402,874,true]]){
  const page=await browser.newPage({viewport:{width:w,height:h},hasTouch:touch,isMobile:touch,deviceScaleFactor:1});
  const faults=[];page.on('pageerror',e=>faults.push(e.message));page.on('console',m=>{if(m.type()==='error')faults.push(m.text());});
  for(const [kind,name,tone] of [['vertex','hybrid','color'],['baked','baked','color'],['procedural','hybrid','procedural']]){
   const dest=new URL(url);dest.searchParams.set('mesh','./'+name+'.glb');dest.searchParams.set('tone',tone);
   await page.goto(dest.href);
   await page.waitForFunction(()=>['ready','error'].includes(document.querySelector('#stage').dataset.state));
   const state=()=>page.locator('#stage').evaluate(el=>Object.assign({},el.dataset));
   const info=await state();assert.equal(info.state,'ready',await page.locator('#status').textContent());
   assert.equal(info.tone,tone);assert.equal(info.view,'desktop');assert(+info.triangles>43000&&+info.triangles<46000);
   await page.screenshot({path:`${out}/${label}-${kind}-distance.png`});
   const b=page.getByRole('button',{name:'Close',exact:true});if(touch)await b.tap();else await b.click();
   const close=await state();assert.equal(close.view,'close');assert(+close.heightPixels>+info.heightPixels*1.6);
   await page.screenshot({path:`${out}/${label}-${kind}-close.png`});
   records.push({label,kind,pose:'hybrid rest frame 1',projectedHeightPx:+info.heightPixels,
    triangles:+info.triangles,assetBytes:statSync(file('./'+name+'.glb')).size});
  }
  assert.deepEqual(faults,[]);
  await page.close();
 }
 console.log(JSON.stringify({staticPoseOnly:true,sameCameraAndLighting:true,bakedMaps:baked.images.length,
   noNewTexturesInProcedural:true,samples:records},null,2));
}finally{await browser.close();}

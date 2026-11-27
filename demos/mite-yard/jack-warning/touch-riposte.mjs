import assert from 'node:assert/strict';

// CDP inputs flow through native Chromium hit testing and pointer capture.
// The test pauses simulation every four ticks to pick a thumb direction;
// it never writes player movement, sprint, position, or combat state.
export async function touchRiposte(page,ctx){
 const cdp=await ctx.newCDPSession(page);
 const send=(type,...touchPoints)=>cdp.send('Input.dispatchTouchEvent',{type,touchPoints});
 const point=(id,x,y)=>({id,x,y,radiusX:4,radiusY:4,force:.5});
 const stick=point(1,82,740);
 let moving=false,tapping=false;
 try{
  for(let steps=0;steps<40;steps++){
   await page.waitForFunction(()=>['touch-step','end','miss','timeout','player-hit'].includes(window.coverFixture?.phase),null,{timeout:90000,polling:35});
   const {phase,command,wish,aim}=await page.evaluate(({x,y})=>{
    const f=window.coverFixture;
    let aim=null;
    if(f.command==='move'&&document.elementFromPoint(x,y)?.tagName!=='CANVAS')
     throw Error('Stick start is obscured');
    if(f.command==='attack'){
     const b=document.querySelector('button[data-act="attack"]'),r=b?.getBoundingClientRect();
     if(!r||r.width<10)throw Error('No sword button');
     aim=[r.x+r.width/2,r.y+r.height/2];
     if(document.elementFromPoint(...aim)?.closest('button')!==b)throw Error('Sword button is obscured');
    }
    return {phase:f.phase,command:f.command,wish:f.wish,aim};
   },stick);
   if(phase!=='touch-step')return;
   if(command==='move'){
    if(!moving){await send('touchStart',stick);moving=true;}
    await send('touchMove',point(stick.id,stick.x+wish[0]*57.75,stick.y+wish[1]*57.75));
   }else if(command==='attack'){
    if(moving){await send('touchEnd');moving=false;}
    await send('touchStart',point(2,...aim));tapping=true;
   }else if(command==='release'){
    assert(tapping);
    await send('touchEnd');tapping=false;
   }else throw Error('Unknown touch command');
   await page.evaluate(()=>{coverFixture.phase=null;__golden.thaw();});
  }
  throw Error('Too many touch steps');
 }finally{
  if(moving||tapping)await send('touchCancel');
  await cdp.detach();
 }
}

import {join} from 'node:path';

export const touchMarks=[1,18,19,20,21,36,37,41,42,53];

// Chromium dispatch goes through hit testing, pointer capture and Fable's
// DOM handlers. The fixture advances on fixed ticks between gesture events.
export async function touchCounter(page,ctx,control,out) {
  await page.waitForFunction(()=>window.fixture?.mode==='touch-start',null,{timeout:90000,polling:100});
  const cdp=await ctx.newCDPSession(page);
  const controls=await page.evaluate(()=>{
    const b=document.querySelector('button[data-act="attack"]');
    const r=b?.getBoundingClientRect();
    if(!r?.width||r.width<10)throw Error('Attack button unavailable');
    const x=r.x+r.width/2,y=r.y+r.height/2;
    if(document.elementFromPoint(x,y)?.closest('button')!==b)throw Error('Attack button is covered');
    return {x,y,canvas:document.elementFromPoint(319,390)?.tagName};
  });
  const pointer=(id,x,y)=>({id,x,y,radiusX:4,radiusY:4,force:.5});
  const stick=pointer(1,82,740),attack=pointer(2,controls.x,controls.y),screen=pointer(3,319,390);
  const shifted=(p,dx,dy)=>({...p,x:p.x+dx,y:p.y+dy});
  const send=(type,...touchPoints)=>cdp.send('Input.dispatchTouchEvent',{type,touchPoints});
  await send('touchStart',stick,attack);
  const snaps=[];
  for(const n of touchMarks){
    await page.evaluate(()=>{fixture.mode='counter';__golden.thaw()});
    await page.waitForFunction(()=>['framing-frozen','ended'].includes(window.fixture?.mode),null,{timeout:90000,polling:100});
    const row=await page.evaluate(()=>{
      const g=game,a=g.hud.acts.attack,x=fixture;
      return {n:__golden.frame-x.counterFrame,attackHeld:a.ptr!==-1,hudSteer:a.root.classList.contains('steer'),
        canvasLook:!!g.input.lookIds?.size,holdingMove:g.input.holdingMove,hp:[g.state.d.hp,x.mob.hp],action:g.player.action,
        captured:a.ptr!==-1&&a.root.hasPointerCapture(a.ptr)};
    });
    if(row.n!==n)throw Error('Unexpected touch milestone '+JSON.stringify(row));
    snaps.push(row);
    if(n===1&&['hud-tap','canvas-drag'].includes(control))await send('touchEnd');
    if(n===18&&control==='canvas-drag')await send('touchStart',stick,screen);
    if(n===18&&control.startsWith('hud-')&&control!=='hud-tap')await send('touchMove',stick,shifted(attack,13,-8));
    if(n===19&&control==='canvas-drag')await send('touchMove',stick,shifted(screen,16,8));
    if(n===19&&control.startsWith('hud-')&&control!=='hud-tap')await send('touchMove',stick,shifted(attack,19,-11));
    if(n===36&&control==='canvas-drag')await send('touchMove',stick,shifted(screen,11,5));
    if(n===36&&control.startsWith('hud-')&&control!=='hud-tap')await send('touchMove',stick,shifted(attack,14,-8));
    if(n===41&&control!=='hud-tap')await send(control==='hud-cancel'?'touchCancel':'touchEnd');
    if(control==='hud-drag'&&[20,36,42].includes(n))
      await page.screenshot({path:join(out,'touch-'+n+'.jpg'),type:'jpeg',quality:89});
  }
  await cdp.detach();
  return {control,controls,snaps,...await page.evaluate(()=>({lens:fixture.lensTrace,events:fixture.pointerEvents,contact:fixture.contact??null}))};
}

// Fixture consumer of the existing native replay. Not a game host.
const drill='six-dummies'
const tickRate=60
const maxTicks=59999 // Three whole-second digits at most; the display wall is finite.
const targetIds=['sword-1','sword-2','sword-3','spear-1','spear-2','spear-3']
export const empty=()=>({version:1,bestTicks:null,lastTicks:null})
const duration=n=>Number.isSafeInteger(n)&&n>0&&n<=maxTicks

export function restore(raw){
  try{
    const x=JSON.parse(raw)
    if(x.version!==1)return empty()
    const b=x.bestTicks,l=x.lastTicks
    if(b===null&&l===null)return empty()
    if(!duration(b)||!duration(l)||b>l)return empty()
    return {version:1,bestTicks:b,lastTicks:l}
  }catch{return empty()}
}
export function finish(state,run){
  if(run?.drill!==drill||!Number.isSafeInteger(run.started)||run.started<0||!Array.isArray(run.attempts))return state
  let last=run.started
  const hit=new Set()
  for(const a of run.attempts){
    if(a?.gained===0)continue
    if(!a||typeof a!=='object')return state
    if(a.gained!==1||!targetIds.includes(a.name)||hit.has(a.name)||
       !Number.isSafeInteger(a.landingTick)||a.landingTick<=last||
       a.slot!==a.name.split('-')[0])return state
    hit.add(a.name)
    last=a.landingTick
  }
  const elapsed=last-run.started
  if(hit.size!==targetIds.length||!duration(elapsed))return state
  const b=state.bestTicks
  return {version:1,bestTicks:b===null?elapsed:Math.min(b,elapsed),lastTicks:elapsed}
}
export function format(ticks){
  if(!duration(ticks))return '--'
  const cs=Math.round(ticks*100/tickRate)
  return (cs/100).toFixed(2)+' s'
}

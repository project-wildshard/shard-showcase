// Shared simulation and presentation geometry for the local Breakwater tide.
export const SURGE=Object.freeze({
 x:-5.55,halfWidth:.96,near:-8.1,far:8.1,length:2.45,
 period:9.4,warnsAt:3.65,startsAt:4.90,endsAt:6.10,damage:12
});

export function surgeAt(time){
 const {period,warnsAt,startsAt,endsAt,near,far,length}=SURGE;
 const cycle=Math.floor(time/period),t=time-cycle*period;
 if(t<warnsAt||t>=endsAt)return null;
 if(t<startsAt)return {phase:'warn',cycle,remaining:(startsAt-t)/(startsAt-warnsAt)};
 const front=near+(far-near+length)*(t-startsAt)/(endsAt-startsAt);
 return {phase:'wash',cycle,lo:Math.max(near,front-length),hi:Math.min(front,far)};
}

export function surgeTouches(p,section){
 return section?.phase==='wash'&&Math.abs(p.x-SURGE.x)<=SURGE.halfWidth&&p.z>=section.lo&&p.z<=section.hi;
}

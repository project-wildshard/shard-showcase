// Presentation only. Time argument is seconds since the sword tap.
export function makeShoulderEnvelope(){
 let weight=0, yielded=false;
 const ease=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
 return ({age,dt=1/60,engaged,look,third})=>{
  if(look)yielded=true;
  if(!third){yielded=true;weight=0;return {weight,yielded};}
  const target=engaged&&!yielded?ease(age/.15)*(1-ease((age-.24)/.25)):0;
  const delta=Math.min(.08,Math.max(0,dt))*7;
  weight+=Math.max(-delta,Math.min(delta,target-weight));
  return {weight,yielded};
 };
}

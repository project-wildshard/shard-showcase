// This is a supplemental HUD decision, not targeting/camera or damage policy.
// The host must establish that the committed lane can still reach the player.
export function jackWarning({tick,currentTick,windup,threatReachesPlayer,
  nativeArrow,bodyVisible,laneVisible,tested} = {}){
  if(nativeArrow===true)return 'native-edge';
  if(!Number.isSafeInteger(tick)||tick!==currentTick||tick<0||
    windup!==true||threatReachesPlayer!==true||tested!==true||
    bodyVisible!==false||laneVisible!==false)return null;
  return 'hidden-charge';
}

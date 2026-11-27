import assert from 'node:assert/strict';
import test from 'node:test';
import { chargeCameraFeed } from './policy.mjs';
const jack = {pos:[1,2,3], height:1.8};
const normal = Object.freeze({aimTarget:null,aimHeight:0,flee:.8,lookX:.01});
const before = {target:jack,armedTarget:jack,kind:'pallet-charge',startedAt:0,now:.949,
  windingUp:true,stillHeld:true,autoFollow:true,thirdPersonMelee:true,sprint:false,
  manualLookSinceStart:false,cleared:false};
test('retain only the already framed Jack and never modify the original input',()=>{
  assert.deepEqual(chargeCameraFeed(before,normal),{aimTarget:jack.pos,aimHeight:1.8,flee:0,lookX:.01});
});
for (const [name,change] of Object.entries({
  'hard cap':{now:.950}, 'expired':{now:1}, 'clock before start':{now:-.001},
  'invalid clock':{now:NaN}, 'active not winding up':{windingUp:false},
  'move released':{stillHeld:false}, 'explicit look':{manualLookSinceStart:true},
  'clear':{cleared:true}, 'sprint':{sprint:true}, 'camera assist off':{autoFollow:false},
  'other camera stance':{thirdPersonMelee:false}, 'no late acquisition':{armedTarget:null},
  'other move':{kind:'jab'}, 'selection changed':{target:{...jack}}
})) test(name,()=>assert.equal(chargeCameraFeed({...before,...change},normal),normal));

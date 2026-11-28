import {test} from 'node:test';
import assert from 'node:assert/strict';
import {ARENA} from './arena.mjs';
import {GANTRY_Z,GANTRY_PERIOD,gantryPose,createBreakwaterGantry} from './breakwater-gantry.mjs';
import {Scene,Vector3,Box3} from 'three';
test('cargo lifts at the stops, stays loaded while traveling, and loops without a jump',()=>{
 const first=gantryPose(0),last=gantryPose(GANTRY_PERIOD);
 assert.deepEqual(first,last);assert.equal(first.drop,1.36);
 const samples=Array.from({length:1081},(_,i)=>gantryPose(i/60));
 for(const [n,p] of samples.entries()){
  assert(p.x>=-7.4-1e-9&&p.x<=-1.8+1e-9);
  assert(p.drop>=.4-1e-9&&p.drop<=1.36);assert(Math.abs(p.tilt)<=.046);
  if(n)assert(Math.hypot(p.x-samples[n-1].x,p.drop-samples[n-1].drop)<.04);
  if(p.x>-7.39&&p.x<-1.81)assert(Math.abs(p.drop-.4)<1e-9);
 }
});
test('the complete gantry and moving cargo stay outside the duel footprint',()=>{
 const s=new Scene(),g=createBreakwaterGantry(s);
 assert(GANTRY_Z<-ARENA);
 assert(g.batches<=22);assert(g.triangles<2500);
 for(const t of [0,5.4,9.7,15.2,18]){
  g.step(t);s.updateMatrixWorld(true);
  const bounds=new Box3().setFromObject(s,true);
  assert(bounds.max.z< -ARENA-.5);
  assert(bounds.getSize(new Vector3()).y<6.7);
 }
});

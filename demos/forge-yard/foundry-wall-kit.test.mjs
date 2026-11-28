import assert from 'node:assert/strict';
import {test} from 'node:test';
import {ARENA} from './arena.mjs';
import {addFoundryWallKit,FOUNDRY_MODULE_EXTENTS} from './foundry-wall-kit.mjs';

test('the three distinct foundry wall modules remain behind the playable floor',()=>{
 const parts=[];
 const record=(material,pos,forward)=>parts.push({material,pos,forward});
 const result=addFoundryWallKit({
  B:(m,s,p)=>record(m,p,s[2]/2),
  C:(m,r,h,p)=>record(m,p,r),
  X:(m,r,h,p)=>record(m,p,r),
  Z:(m,r,h,p)=>record(m,p,h/2),
  Tori:(m,r,p)=>record(m,p,r*.1),
 });
 assert.equal(result,3);assert.equal(new Set(FOUNDRY_MODULE_EXTENTS.map(x=>x.id)).size,result);
 for(const {x,zMax} of FOUNDRY_MODULE_EXTENTS){
  const fixture=parts.filter(({pos})=>Math.abs(pos[0]-x)<2.28);
  assert(fixture.length>=21);assert(new Set(fixture.map(p=>p.material)).size>=5);
  assert(fixture.every(({pos,forward})=>pos[2]+forward<=zMax+1e-5));
  assert(zMax< -ARENA);
 }
});

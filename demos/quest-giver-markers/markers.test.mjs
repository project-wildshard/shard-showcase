import test from 'node:test';
import assert from 'node:assert/strict';
import { createMarker } from './markers.mjs';
const document={ createElement:()=>({style:{},dataset:{},children:[],attrs:{},
  setAttribute(k,v){this.attrs[k]=v},append(el){this.children.push(el)}
})};
test('two glyphs, three visual treatments, and absence for completed quests',()=>{
  const anchor={headX:140.2,headY:405.4};
  for(const [state,glyph] of [['locked','!'],['available','!'],['turnIn','?']]){
    const mark=createMarker(document,'Yard Boss',state,anchor);
    assert.equal(mark.dataset.state,state);
    assert.deepEqual(mark.children.map(c=>c.textContent),['Yard Boss',glyph]);
    assert.match(mark.attrs['aria-label'],/^Yard Boss: Quest /);
    assert.deepEqual(mark.style,{left:'140.2px',top:'405.4px'});
  }
  assert.equal(createMarker(document,'Yard Boss','done',anchor),null);
  assert.throws(()=>createMarker(document,'Yard Boss','constructor',anchor),TypeError);
  assert.throws(()=>createMarker(document,'Yard Boss','locked',{headX:NaN,headY:0}),TypeError);
});

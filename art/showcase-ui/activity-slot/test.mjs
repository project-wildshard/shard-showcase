import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import assert from 'node:assert/strict';

const root=new URL('./',import.meta.url);
const html=readFileSync(new URL('index.html',root),'utf8');
const code=readFileSync(new URL('app.js',root),'utf8');
assert.equal(html.match(/id="activity"/g)?.length,1);
assert.match(html,/<meta name="viewport" content="width=device-width,initial-scale=1">/);
const modes=['quest','vault','course','tricks'];
function boot(value='') {
  let active;
  function node(mode) {
    return {dataset:mode ? {mode}: {},attributes:{},handlers:{},
      setAttribute(k,v){this.attributes[k]=v},
      addEventListener(k,fn){this.handlers[k]=fn},
      focus(){active=this},
      tap(){this.handlers.click()}
    };
  }
  const controls=modes.map(node);
  const parts=new Map(['.view','#end','#area','#activity-icon','#activity-title','#activity-detail','#mode-caption'].map(k=>[k,node()]));
  const document={querySelector:s=>parts.get(s),querySelectorAll:()=>controls};
  runInNewContext(code,{document,URLSearchParams,location:{search:value}});
  return {parts,controls,active:()=>active};
}
const {parts,controls,active}=boot();
assert.equal(parts.get('.view').dataset.mode,'vault');
for (const n of controls) {
  n.tap();
  assert.equal(parts.get('.view').dataset.mode,n.dataset.mode);
  assert.equal(controls.filter(b=>b.attributes['aria-pressed']==='true').length,1);
  if(n!==controls[0]){
    assert.equal(parts.get('#end').disabled,false);
    assert.notEqual(parts.get('#activity-title').textContent,'Clock In');
    parts.get('#end').tap();
    assert.equal(parts.get('#activity-title').textContent,'Clock In');
    assert.equal(active(),controls[0]);
  }
  assert.equal(parts.get('#end').disabled,true);
}
assert.equal(boot('?state=tricks').parts.get('.view').dataset.mode,'tricks');
assert.equal(boot('?state=../../bogus').parts.get('.view').dataset.mode,'vault');
console.log('One slot, state exclusivity, end-to-quest, keyboard focus, and invalid-state fallback passed.');

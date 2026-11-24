// Static review state QA, not a mobile browser or gameplay test.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";

const dir=new URL("../dist/level-up/",import.meta.url);
const read=n=>readFileSync(new URL(n,dir),"utf8");
function review(search){
  let focus=null;
  function item(target){
    const events={};
    return {dataset:{target},attributes:{},events,
      addEventListener(name,callback){events[name]=callback},
      setAttribute(name,value){this.attributes[name]=value},
      focus(){focus=target}};
  }
  const id=Object.fromEntries(["frame","card","cue","skip","note","location"].map(k=>[k,item()]));
  const tabs=["fight","calm"].map(item);
  runInNewContext(read("app.js"),{document:{getElementById:k=>id[k],querySelectorAll:()=>tabs},
    URLSearchParams,location:{search}});
  return {id,tabs,focused:()=>focus};
}
const start=review("");
assert.equal(start.id.frame.dataset.state,"fight");
assert.equal(start.id.cue.hidden,false);
assert.equal(start.id.card.hidden,true);
assert.equal(start.id.note.textContent,"2.5 SEC CUE");
start.tabs[1].events.click();
assert.equal(start.id.frame.dataset.state,"calm");
assert.equal(start.id.cue.hidden,true);
assert.equal(start.id.card.hidden,false);
assert.equal(start.id.note.textContent,"AFTER 5 SEC CALM");
start.id.skip.events.click();
assert.equal(start.id.frame.dataset.state,"rest");
assert.equal(start.id.card.hidden,true);
assert.equal(start.focused(),"calm");
assert.equal(review("?state=calm").id.card.hidden,false);
assert.match(read("style.css"),/\.burst\{pointer-events:none;/);
assert.match(read("style.css"),/\.meter-wrap b\{width:18%\}/);
assert.match(read("../activity-slot/style.css"),/\.meter-wrap i\{height:4px;/);
assert.match(read("index.html"),/Illustrative control placement; not interactive/);
console.log("Fight and calm state selection, skip/focus, 4 px meter and non-intercepting burst declarations passed.");

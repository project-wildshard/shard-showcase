// Run: node project/check-catalog-studies.mjs
// Load the actual site scripts with a minimal DOM so query, class, study and
// hash routing regressions can be checked without installing browser packages.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";

const dist = new URL("../dist/", import.meta.url);
const read = path => readFileSync(new URL(path, dist), "utf8");
const markup = read("index.html");
const ids = new Map();
const handlers = new Map();
const location = {hash: ""};
class Element {
  constructor(tag) { this.tag=tag;this.children=[];this.events={};this.textContent="";this.value="";this.hidden=false }
  append(...xs) { this.children.push(...xs) }
  replaceChildren(...xs) { this.children=this.tag==="node rows" ? xs.flatMap(x=>x.children) : xs }
  addEventListener(type,cb) { this.events[type]=cb }
  setAttribute(key,val) { this[key]=val }
  matches(tag) { return this.tag===tag }
  querySelector(tag) { return this.children.find(c=>c.tag===tag) }
  scrollIntoView() {}
  focus() { this.focused=true }
  closest() { return {id:this.tag==="details"?"assets":(this.panel??"assets")} }
}
for(const id of [...markup.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]))ids.set(id,new Element("node "+id));
for(const id of ["nov23-d7-launch-wall","nov23-round5-field-atlas","nov23-activity-slot","nov23-hover-secondary-kit"])ids.get(id).panel="blender";
const get=id=>ids.get(id)??ids.get("rows").children.find(x=>x.id===id);
const select=get("previews");
select.value="all";
select.options=["all","linked","unlinked"].map(value=>Object.assign(new Element("option"),{value,textContent:value}));
const document={getElementById:get,createElement:t=>new Element(t),createDocumentFragment:()=>new Element("fragment")};
const ctx={document,location,history:{pushState:(_,__,hash)=>{location.hash=hash}},addEventListener:(type,cb)=>handlers.set(type,cb),
  ConceptAngles:{available:()=>false,mountRails(){},close(){}}};
const data=runInNewContext(read("data.js")+"\nDATA",ctx);
runInNewContext(read("app.js"),{...ctx,DATA:data});
const rows=()=>get("rows").children;
const pick=(id,value,evt="change")=>{get(id).value=value;get(id).events[evt]({type:evt})};
const assertRows=n=>assert.equal(rows().length,n);
assertRows(data.assets.length);
const hasStudy=a=>Boolean(a.model_preview);
const salvage=data.assets.filter(a=>a.related_study?.href==="#nov24-salvage-parts");
assert.equal(salvage.length,6);
assert.equal(salvage.filter(hasStudy).length,2);
for (const a of salvage) {
  const row=get("asset-"+a.id);
  const link=row.children.flatMap(x=>x.children).find(c=>c.href===a.related_study.href);
  assert.equal(link.textContent,a.related_study.label);
}
assert.ok(ids.has("nov24-salvage-parts"));

const linked=data.assets.filter(hasStudy);
assert.equal(select.options[1].textContent,`linked (${linked.length})`);
pick("previews","linked");assertRows(linked.length);
pick("previews","unlinked");assertRows(data.assets.length-linked.length);
pick("types","PROP");
assertRows(data.assets.filter(a=>a.class==="PROP"&&!hasStudy(a)).length);
pick("query","totally-absent-asset","input");assertRows(0);
location.hash="#asset-WSC-SCENE-009";handlers.get("hashchange")();
assertRows(1);
const forced=get("asset-WSC-SCENE-009");
assert.equal(forced.open,true);
assert.equal(get("hits").textContent,"0 matching entries · plus linked entry outside filters");
assert.equal(forced.children.flatMap(x=>x.children).find(c=>c.href==="#nov23-round5-field-atlas").textContent,"View study");
location.hash="#catalog";handlers.get("popstate")();
assertRows(0);
assert.equal(get("hits").textContent,"0 matching entries");
location.hash="#nov23-d7-launch-wall";handlers.get("popstate")();
assert.equal(get("blender").hidden,false);
location.hash="#asset-WSC-SCENE-009";handlers.get("popstate")();
assert.equal(get("assets").hidden,false);
assert.equal(get("asset-WSC-SCENE-009").open,true);
assert.equal(get("query").value,"totally-absent-asset");
assert.equal(select.value,"unlinked");
assert.ok(linked.every(a=>ids.has(a.model_preview.slice(1))));
console.log(`${data.assets.length} entries, ${linked.length} study links, ${data.assets.length-linked.length} unlinked; filters, forced row, and hash routing passed.`);

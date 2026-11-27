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
for(const id of ["nov23-d7-launch-wall","nov23-round5-field-atlas","nov23-activity-slot","nov23-hover-secondary-kit","nov24-squeeze-cave-gold","nov24-w3b-ranged-inventory","nov25-e4-welder-cone"])ids.get(id).panel="blender";
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

const cores=data.assets.filter(a=>a.related_study?.href==="#nov25-pack-upgrade-cores");
assert.deepEqual(Array.from(cores,a=>a.id).sort(), ["WSC-ACTOR-007","WSC-ACTOR-008","WSC-ACTOR-009"]);
assert.ok(ids.has("nov25-pack-upgrade-cores"));
for (const a of cores) {
  assert.equal(a.status,"provisional-inventory");
  assert.equal(a.model_preview,undefined);
  assert.ok(get("asset-"+a.id).children.flatMap(x=>x.children).some(c=>
    c.href===a.related_study.href && c.textContent===a.related_study.label));
}


const rook=data.assets.find(a=>a.id==="WSC-SCENE-002");
assert.equal(rook.model_preview,"#nov23-tinker-rook-counter");
assert.equal(rook.related_study?.href,"#nov25-w2b-rook-forge");
assert.ok(ids.has(rook.related_study.href.slice(1)));
assert.ok(get("asset-"+rook.id).children.flatMap(x=>x.children).some(c=>
  c.href===rook.related_study.href && c.textContent===rook.related_study.label));

const grapplePerch=data.assets.find(a=>a.id==="WSC-KIT-004");
assert.equal(grapplePerch.model_preview,"#nov23-grapple-hoop");
assert.equal(grapplePerch.related_study?.href,"#nov25-w7a-grapple-perch");
assert.ok(ids.has(grapplePerch.related_study.href.slice(1)));
assert.ok(get("asset-"+grapplePerch.id).children.flatMap(x=>x.children).some(c=>
  c.href===grapplePerch.related_study.href && c.textContent===grapplePerch.related_study.label));

const zipCable=data.assets.find(a=>a.id==="WSC-PROP-033");
assert.equal(zipCable.model_preview,"#west-route-details");
assert.equal(zipCable.related_study?.href,"#nov25-w11a-zip-sway");
assert.ok(ids.has(zipCable.related_study.href.slice(1)));
assert.ok(get("asset-"+zipCable.id).children.flatMap(x=>x.children).some(c=>
  c.href===zipCable.related_study.href && c.textContent===zipCable.related_study.label));

const roofVista=data.assets.find(a=>a.id==="WSC-MODULE-001");
assert.equal(roofVista.model_preview,"#west-venue-kits");
assert.equal(roofVista.related_study?.href,"#nov25-w9b-roof-vistas");
assert.ok(ids.has(roofVista.related_study.href.slice(1)));
assert.ok(get("asset-"+roofVista.id).children.flatMap(x=>x.children).some(c=>
  c.href===roofVista.related_study.href && c.textContent===roofVista.related_study.label));

const sword=data.assets.find(a=>a.id==="WSC-GEAR-001");
assert.equal(sword.model_preview,"#nov24-west-inventory-pair");
assert.equal(sword.status,"model-study-available");
assert.equal(sword.related_study?.href,"#nov25-e8e-sword-finishes");
assert.ok(ids.has(sword.related_study.href.slice(1)));
assert.ok(get("asset-"+sword.id).children.flatMap(x=>x.children).some(c=>
  c.href===sword.related_study.href && c.textContent===sword.related_study.label));

const titan=data.assets.find(a=>a.id==="WSC-SCENE-008");
assert.equal(titan.model_preview,"#nov23-titan-bowl");
assert.equal(titan.status,"scene-study-available");
assert.equal(titan.related_study?.href,"#nov25-e12g-titan-retry-alcove");
assert.ok(ids.has(titan.related_study.href.slice(1)));
assert.ok(get("asset-"+titan.id).children.flatMap(x=>x.children).some(c=>
  c.href===titan.related_study.href && c.textContent===titan.related_study.label));

const cave=data.assets.find(a=>a.id==="WSC-PROP-011");
assert.equal(cave.model_preview,"#nov23-rock-squeeze-cave");
assert.equal(cave.related_study?.href,"#nov24-squeeze-cave-gold");
assert.ok(ids.has(cave.related_study.href.slice(1)));
assert.ok(get("asset-"+cave.id).children.flatMap(x=>x.children).some(c=>
  c.href===cave.related_study.href && c.textContent===cave.related_study.label));

const donors=data.assets.filter(a=>a.model_file);
assert.deepEqual(Array.from(donors, a=>a.id).sort(),[
  "WSC-ARCH-008","WSC-ARCH-009","WSC-ARCH-010","WSC-GEAR-003","WSC-GEAR-004","WSC-PROP-020","WSC-PROP-021","WSC-PROP-024"
]);
for (const a of donors) {
  const {href,bytes,triangles,dimensions_m}=a.model_file;
  assert.ok(/^https:\/\/github\.com\/project-wildshard\/shard-showcase\/blob\/[a-f0-9]{40}\/public\/assets\/wildshard-art\/[a-z0-9-]+\.glb$/.test(href));
  assert.ok(href.includes(a.id.toLowerCase()));
  assert.ok(bytes>0 && triangles>0 && dimensions_m.length===3 && dimensions_m.every(x=>x>0));
  assert.ok(markup.includes(href));
  assert.ok(hasStudy(a) && ["provisional-inventory","visual-candidate"].includes(a.status));
  const row=get("asset-"+a.id);
  const link=row.children.flatMap(x=>x.children).find(c=>c.href===href);
  assert.equal(link.textContent,"Open GLB on GitHub (repo access required)");
  assert.ok(row.children.some(x=>x.textContent.includes("Blender reimport verified")));
}

for (const [id, bytes, triangles] of [["WSC-GEAR-003",49888,864],["WSC-GEAR-004",52596,924]]) {
  const a=data.assets.find(row=>row.id===id);
  assert.equal(a.model_preview,"#nov24-w3b-ranged-inventory");
  assert.equal(a.model_file.bytes,bytes);
  assert.equal(a.model_file.triangles,triangles);
  assert.ok(a.concept && a.model_file.bytes<=Number(a.proposed_download_budget_bytes));
}

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
location.hash="#nov24-squeeze-cave-gold";handlers.get("popstate")();
assert.equal(get("blender").hidden,false);
location.hash="#asset-WSC-SCENE-009";handlers.get("popstate")();
assert.equal(get("assets").hidden,false);
assert.equal(get("asset-WSC-SCENE-009").open,true);
assert.equal(get("query").value,"totally-absent-asset");
assert.equal(select.value,"unlinked");
assert.ok(linked.every(a=>ids.has(a.model_preview.slice(1))));
console.log(`${data.assets.length} entries, ${linked.length} study links, ${data.assets.length-linked.length} unlinked; filters, forced row, and hash routing passed.`);
for (const id of ["WSC-ACTOR-015", "WSC-ACTOR-017"]) {
  const row = data.assets.find(a => a.id === id);
  assert.equal(row.related_study.href, "#nov25-w1b-quest-markers");
  assert.ok(row.model_preview.startsWith("#nov23-w1a-"));
}
assert.ok(ids.has("nov25-w1b-quest-markers"));
assert.ok(ids.has("nov25-e5a-riveter-slam-vfx"));
for (const id of ["WSC-ACTOR-005", "WSC-ACTOR-013"])
  assert.ok(!data.assets.find(row => row.id === id).model_preview);
assert.ok(ids.has("nov25-w4a-native-grate"));
assert.ok(ids.has("nov24-w4a-plate-gate"));
assert.ok(ids.has("nov25-w11a-gate-lanterns"));
assert.ok(ids.has("nov25-w0b-north-west-gates"));
assert.ok(ids.has("nov25-e1d-scrip-opening"));
assert.ok(ids.has("nov24-east-payout-chest"));
assert.ok(ids.has("nov25-e11d-foreman-rewards"));
assert.ok(!data.assets.find(row=>row.id==="WSC-ACTOR-009").model_preview);
assert.ok(ids.has("nov25-e3-pillar-screen"));
assert.ok(!data.assets.find(row=>row.id==="WSC-ACTOR-003").model_preview);
assert.ok(ids.has("nov25-w6b-native-conveyors"));
assert.equal(data.assets.find(row=>row.id==="WSC-PROP-037").related_study.href,"#nov24-w6b-conveyor-direction");
assert.ok(ids.has("nov25-e8b-big-pallet-pit"));
assert.ok(!data.assets.find(row=>row.id==="WSC-ACTOR-007").model_preview);
assert.ok(ids.has("nov25-w12-range-gate-walk"));
assert.ok(ids.has("west-range-landscape-wip"));
assert.ok(ids.has("nov25-e7a-mite-rarity"));
assert.equal(data.assets.find(row=>row.id==="WSC-ACTOR-001").model_preview,"#nov22-mite-rig");
assert.ok(ids.has("nov25-w5a-native-kickers"));
assert.ok(ids.has("nov23-d7-launch-wall"));
assert.ok(ids.has("west-hover-park-wip"));
assert.ok(ids.has("nov25-e8d-night-reliefs"));
assert.ok(ids.has("trophy-plaza-review"));
assert.ok(ids.has("nov25-e4-slag-heat"));
assert.ok(ids.has("nov24-e4-ground-slag"));
assert.ok(ids.has("nov25-w8b-rock-three-pitches"));
assert.ok(ids.has("nov24-w8b-scramble-deck-a"));
assert.ok(ids.has("west-climb-rock-wip"));
assert.ok(ids.has("nov25-w3a-native-six-targets"));
assert.ok(ids.has("nov26-w3a-range-entry"));
for (const name of ["gate-to-yard","gate-eye"]) {
  const path = `media/nov26-w3a-${name}.webp`;
  assert.ok(markup.includes(`src="${path}"`));
  assert.ok(readFileSync(new URL(path, dist)).byteLength > 1000);
}

assert.ok(ids.has("nov24-west-melee-targets"));
assert.ok(ids.has("nov25-w12-range-gate-walk"));
assert.ok(ids.has("nov25-e6-arc-charge"));
assert.ok(ids.has("nov25-e6-duel-cover"));
assert.ok(!data.assets.find(row=>row.id==="WSC-ACTOR-006").model_preview);

const seesaw=data.assets.find(a=>a.id==="WSC-PLAN-003");
assert.equal(seesaw.model_preview,"#nov23-seesaw-fit");
assert.equal(seesaw.status,"static-study-available");
assert.equal(seesaw.related_study?.href,"#nov26-w4b-seesaw-launch");
assert.ok(ids.has(seesaw.related_study.href.slice(1)));

const ropeWalkway=data.assets.find(a=>a.id==="WSC-PROP-048");
assert.equal(ropeWalkway.model_preview,"#lookout-reuse-models");
assert.equal(ropeWalkway.related_study?.href,"#nov26-w6c-climb-terminals");
assert.ok(ids.has(ropeWalkway.related_study.href.slice(1)));

const rangeTimer=data.assets.find(a=>a.id==="WSC-PROP-027");
assert.equal(rangeTimer.model_preview,"#course-gantry-and-trophy");
assert.equal(rangeTimer.related_study?.href,"#nov26-w3a-range-record-face");
assert.ok(ids.has(rangeTimer.related_study.href.slice(1)));
assert.ok(ids.has("nov24-w11a-record-light"));
pick("query","","input");
pick("previews","all");
pick("types","KIT");
const movers = data.assets.find(a => a.id === "WSC-KIT-002");
assert.equal(movers.model_preview, "#nov23-station6-landings");
assert.equal(movers.related_study.href, "#nov27-w6c-station6-round-trips");
assert.ok(ids.has("nov26-w6a-spinner-lift-handoff"));
assert.ok(markup.includes('href="#nov26-w6a-spinner-lift-handoff">Spinner to cage handoff'));
assert.ok(ids.has(movers.related_study.href.slice(1)));
assert.ok(get("asset-"+movers.id).children.flatMap(x=>x.children).some(c=>c.href===movers.related_study.href));
const stormKit = data.assets.find(a => a.id === "WSC-KIT-007");
assert.equal(stormKit.model_preview, "#nov23-e9-storm-beacon");
assert.equal(stormKit.related_study.href, "#nov26-e9-beacon-ground-control");
assert.ok(ids.has(stormKit.related_study.href.slice(1)));
assert.ok(get("asset-"+stormKit.id).children.flatMap(x=>x.children).some(c=>c.href===stormKit.related_study.href));
for(const [id,original,type] of [
  ['WSC-KIT-005','#nov23-west-riding-course','KIT'],
  ['WSC-PROP-080','#w10b-riding-jump','PROP'],
]){
  pick("types",type);
  const a=data.assets.find(x=>x.id===id);
  assert.equal(a.model_preview,original);
  assert.equal(a.related_study.href,'#nov26-w10b-four-rails');
  assert.ok(ids.has(a.related_study.href.slice(1)));
  assert.ok(get('asset-'+id).children.flatMap(x=>x.children).some(c=>c.href===a.related_study.href));
}
assert.ok(ids.has("nov26-e2-charge-stop"));
assert.ok(markup.includes('href="#nov26-e2-charge-stop"'));
assert.equal(data.assets.find(a=>a.id==="WSC-ACTOR-002").model_preview,"#nov22-pallet-jack");
assert.ok(ids.has("nov26-east-threshold-direction"));
assert.ok(markup.includes('href="#nov26-east-threshold-direction"'));
for (const side of ["yard", "return"]) {
  assert.ok(markup.includes(`href="media/w0a-east-direction-${side}.glb"`));
  assert.ok(markup.includes(`src="media/nov26-east-threshold-${side}.webp"`));
}
assert.ok(ids.has("nov26-w4b-player-lever"));
assert.ok(markup.includes('href="#nov26-w4b-player-lever"'));
for (const state of ["lever", "release", "settled"])
  assert.ok(markup.includes(`src="media/nov26-w4b-player-${state}.webp"`));
assert.ok(ids.has("nov26-e1-first-cover"));
assert.ok(markup.includes('href="#nov26-e1-first-cover"'));
assert.ok(markup.includes('href="media/e1-first-cover-cradle.glb"'));
assert.ok(ids.has("nov26-w9-oval-cache-screen"));
assert.ok(markup.includes('href="#nov26-w9-oval-cache-screen"'));
assert.ok(markup.includes('href="media/w9-oval-cache-screen.glb"'));
assert.ok(ids.has("nov26-e5b-gate-crossing"));
assert.ok(markup.includes('href="#nov26-e5b-gate-crossing"'));
for (const f of ["hold","release"]) assert.ok(markup.includes(`src="media/nov26-e5b-cross-${f}.webp"`));

assert.ok(ids.has("nov26-vault-bridge-boarding"));
for (const name of ["wide","eye"]) {
  const path = `media/nov26-vault-bridge-lift-${name}.webp`;
  assert.ok(markup.includes(`src="${path}"`));
  assert.ok(readFileSync(new URL(path, dist)).byteLength > 1000);
}

assert.ok(ids.has("nov26-avenue-service-cover"));
for(const name of ["nov26-avenue-cover-context.webp","nov26-avenue-cover-detail.webp","w0b-avenue-service-cover.glb"]) {
  assert.ok(markup.includes(`media/${name}`));
  assert.ok(readFileSync(new URL(`media/${name}`,dist)).byteLength>1000);
}

assert.ok(ids.has("nov26-vault-moving-lift"));
for(const name of ["nov26-vault-lift-boarding.webp","nov26-vault-lift-top.webp"]){
  assert.ok(markup.includes(`media/${name}`));
  assert.ok(readFileSync(new URL(`media/${name}`,dist)).byteLength>1000);
}

assert.ok(ids.has("nov26-paddock-block-walk"));
assert.equal(data.assets.find(a=>a.id==="WSC-PLAN-008").related_study.href,"#nov26-paddock-block-walk");
for (const name of ["walk","treads"]) {
  const path = `media/nov26-paddock-block-${name}.webp`;
  assert.ok(markup.includes(`src="${path}"`));
  assert.ok(readFileSync(new URL(path,dist)).byteLength > 1000);
}

assert.ok(ids.has("nov26-e6-screen-far"));
for(const name of ["nov26-e6-screen-near.webp","nov26-e6-screen-far.webp","e6-sight-screen-far.glb"]){
  assert.ok(markup.includes(`media/${name}`));
  assert.ok(readFileSync(new URL(`media/${name}`,dist)).byteLength>1000);
}

assert.ok(ids.has("nov26-w4b-skittle-reset"));
for (const id of ["WSC-PLAN-004","WSC-PLAN-005"]) {
  const asset=data.assets.find(a=>a.id===id);
  assert.equal(asset.model_preview,"#nov23-west-physics-props");
  assert.equal(asset.related_study.href,"#nov26-w4b-skittle-reset");
}
for (const state of ["result","reset","replay"]) {
  const path=`media/nov26-w4b-score-${state}.webp`;
  assert.ok(markup.includes(`src="${path}"`));
  assert.ok(readFileSync(new URL(path,dist)).byteLength>1000);
}

assert.ok(ids.has("nov26-e12h-dormant-stack"));
const titanCutsceneParts=data.assets.find(a=>a.id==="WSC-KIT-010");
assert.equal(titanCutsceneParts.related_study.href,"#nov26-e12h-dormant-stack");
assert.equal(titanCutsceneParts.model_preview,undefined);
location.hash="#asset-WSC-KIT-010";handlers.get("hashchange")();
assert.ok(get("asset-WSC-KIT-010").children.flatMap(x=>x.children).some(c=>c.href===titanCutsceneParts.related_study.href));
for (const name of ["nov26-titan-haul-stack-opening.webp","nov26-titan-haul-stack-footing.webp","e12h-dormant-haul-stack.glb"]) {
  const path=`media/${name}`;
  assert.ok(markup.includes(path));
  assert.ok(readFileSync(new URL(path,dist)).byteLength>1000);
}

assert.ok(ids.has("nov26-hover-ease-off"));
assert.equal(data.assets.find(a=>a.id==="WSC-KIT-003").related_study.href,"#nov26-hover-ease-off");
for(const name of ["nov26-hover-ease-off-rider.webp","nov26-hover-ease-off-deck.webp","w5a-high-receiver-ease-off.glb"]){
  assert.ok(markup.includes(`media/${name}`));
  assert.ok(readFileSync(new URL(`media/${name}`,dist)).byteLength>1000);
}

assert.ok(ids.has("nov26-e10c-square-crate"));
assert.equal(data.assets.find(a=>a.id==="WSC-PROP-064").related_study.href,"#nov26-e10c-square-crate");
for (const state of ["free","fixed"]) {
  const path=`media/nov26-vault-full-push-${state}.webp`;
  assert.ok(markup.includes(path));
  assert.ok(readFileSync(new URL(path,dist)).byteLength>1000);
}

assert.ok(ids.has("nov26-w6a-spinner-lift-handoff"));
for (const file of ["nov26-spinner-lift-gap.webp","nov26-spinner-lift-lip.webp","w6a-spinner-lift-lip.glb"]) {
  assert.ok(markup.includes(`media/${file}`));
  assert.ok(readFileSync(new URL(`media/${file}`,dist)).byteLength>1000);
}

assert.ok(ids.has("nov26-e8d-wall-fit"));
assert.equal(data.assets.find(a=>a.id==="WSC-MODULE-017").related_study.href,"#nov26-e8d-wall-fit");
for (const state of ["locked","earned"]) {
  const path=`media/nov26-trophy-wall-${state}.webp`;
  assert.ok(markup.includes(path));
  const bytes=readFileSync(new URL(path,dist));
  assert.ok(bytes.byteLength>1000);
  assert.equal(bytes.subarray(8,12).toString(),"WEBP");
}

assert.ok(ids.has("nov26-w6a-station5-ride"));
assert.match(markup, /id="nov26-w6a-spinner-lift-handoff"><p><a href="#nov26-w6a-station5-ride"/);
for (const state of ["low-beam","raised-beam"]) {
  const path=`media/nov26-station5-${state}.webp`;
  assert.ok(markup.includes(path));
  const bytes=readFileSync(new URL(path,dist));
  assert.ok(bytes.byteLength>1000);
  assert.equal(bytes.subarray(8,12).toString(),"WEBP");
}

assert.ok(ids.has("nov26-e5b-keycard-entry"));
assert.equal(data.assets.find(a=>a.id==="WSC-PROP-065").related_study.href,"#nov26-e5b-keycard-entry");
for (const file of ["nov26-keycard-shed-entry.webp","nov26-keycard-shed-card.webp","e5b-keycard-shed-open.glb"]) {
  assert.ok(markup.includes(`media/${file}`));
  const bytes=readFileSync(new URL(`media/${file}`,dist));
  assert.ok(bytes.byteLength>1000);
  if (file.endsWith(".glb")) assert.equal(bytes.subarray(0,4).toString(),"glTF");
  else assert.equal(bytes.subarray(8,12).toString(),"WEBP");
}

assert.ok(ids.has("nov26-w9a-native-squeeze"));
assert.match(markup,/id="nov23-rock-squeeze-cave"><p><a href="#nov26-w9a-native-squeeze"/);
for (const state of ["stock","candidate"]) {
  const path=`media/nov26-w9a-squeeze-${state}.webp`;
  assert.ok(markup.includes(path));
  const bytes=readFileSync(new URL(path,dist));
  assert.ok(bytes.byteLength>1000);
  assert.equal(bytes.subarray(8,12).toString(),"WEBP");
}

const halfCover=data.assets.find(a=>a.id==="WSC-PROP-066");
assert.equal(halfCover.related_study?.href,"#nov27-e1c-half-cover");
assert.ok(ids.has(halfCover.related_study.href.slice(1)));
assert.ok(markup.includes('href="media/e1-half-cover.glb"'));
assert.ok(markup.includes('href="#nov26-e1-first-cover">Earlier roadside crate stacks'));

const rockCache=data.assets.find(a=>a.id==="WSC-PROP-049");
assert.equal(rockCache.model_preview,"#nov23-cache-opening");
assert.equal(rockCache.related_study?.href,"#nov27-w9-rock-cache");
assert.ok(ids.has("nov27-w9-rock-cache"));
assert.ok(markup.includes('href="#nov27-w9-rock-cache"'));
assert.ok(markup.includes('href="media/w9-rock-cache-outcrop.glb"'));
for (const name of ["discover","open"]) {
  const imagePath=`media/nov27-w9-rock-cache-${name}.webp`;
  assert.ok(markup.includes(`src="${imagePath}"`));
  assert.equal(readFileSync(new URL(imagePath,dist)).subarray(8,12).toString(),"WEBP");
}

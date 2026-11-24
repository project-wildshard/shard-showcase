const frame=document.getElementById('frame');
const tabs=[...document.querySelectorAll('[data-target]')];
const card=document.getElementById('card');
const chip=document.getElementById('cue');
const skip=document.getElementById('skip');

function show(state){
  frame.dataset.state=state;
  card.hidden=state!=='calm';
  chip.hidden=state!=='fight';
  document.getElementById('location').textContent=state==='fight'?'EAST · CONTAINER YARD':'EAST · GATE VISTA';
  document.getElementById('note').textContent=
    state==='fight'?'2.5 SEC CUE':state==='calm'?'AFTER 5 SEC CALM':'CARD SKIPPED';
  tabs.forEach(btn=>btn.setAttribute('aria-pressed',String(btn.dataset.target===state)));
}

tabs.forEach(btn=>btn.addEventListener('click',()=>show(btn.dataset.target)));
skip.addEventListener('click',()=>{
  show('rest');
  tabs[1].focus();
});
show(new URLSearchParams(location.search).get('state')==='calm'?'calm':'fight');

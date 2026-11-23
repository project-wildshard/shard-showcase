'use strict';
const states = Object.freeze({
  quest: {area:'EAST YARD', icon:'quest', title:'Clock In', detail:'TRACKED QUEST', status:'Tracked quest'},
  vault: {area:'TRAINING VAULT', icon:'vault', title:'Training Vault', detail:'ROOM 2 / 4 · 3 LEFT', status:'Vault active'},
  course: {area:'RIDING OVAL', icon:'clock', title:'00:42.9', detail:'RIDING LAP · PB 41.3', status:'Course active'},
  tricks: {area:'HOVER PARK', icon:'trick', title:'Trick score', detail:'1,320 PTS · PB 1,500', status:'Trick run active'},
});
const view = document.querySelector('.view');
const select = [...document.querySelectorAll('.switcher [data-mode]')];
const end = document.querySelector('#end');
function switchTo(next) {
  const mode = Object.hasOwn(states,next) ? next : 'vault';
  const state = states[mode];
  view.dataset.mode = mode;
  document.querySelector('#area').textContent = state.area;
  document.querySelector('#activity-icon').setAttribute('href','#s-'+state.icon);
  document.querySelector('#activity-title').textContent = state.title;
  document.querySelector('#activity-detail').textContent = state.detail;
  document.querySelector('#mode-caption').textContent = state.status;
  for (const b of select) b.setAttribute('aria-pressed',String(b.dataset.mode===mode));
  end.disabled = mode==='quest';
  if (!end.disabled) end.textContent = 'End activity';
  else end.textContent = 'Quest restored';
}
for (const b of select) b.addEventListener('click',() => switchTo(b.dataset.mode));
end.addEventListener('click',() => {
  switchTo('quest');
  select[0].focus();
});
switchTo(new URLSearchParams(location.search).get('state') || 'vault');

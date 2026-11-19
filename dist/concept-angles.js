/* Crop the existing board at the audited box. All four angles share one WebP. */
const ConceptAngles = (() => {
 const labels = ['Front', 'Back', 'Left', 'Right'];
 const rails = [
  ['flat', 'Flat rail'],
  ['down', 'Descending rail'],
  ['kink', 'Kinked rail'],
 ].map(([key, name]) => ({
  id: 'WSC-PLAN-009/'+key, name, concept: 'media/WSC-PLAN-009-'+key+'-illustrative.webp',
 }));
 function create(tag, parent, className, text) {
  const n = document.createElement(tag);
  if (className) n.className = className;
  if (text) n.textContent = text;
  parent?.append(n);
  return n;
 }
 function button(parent, className, text) {
  const b = create('button', parent, className, text);
  b.type = 'button';
  return b;
 }
 function available(asset) {
  return Boolean(asset.concept && CONCEPT_ANGLE_DATA[asset.id]);
 }
 function crop(parent, asset, angle, lazy) {
  const [[w,h], ...boxes] = CONCEPT_ANGLE_DATA[asset.id];
  const [x,y,x2,y2] = boxes[angle];
  const dw = x2-x, dh = y2-y;
  const frame = create('span', parent, 'angle-crop');
  frame.style.setProperty('--crop-ratio', dw/dh);
  const img = create('img', frame);
  img.alt = lazy ? '' : `${asset.name}, ${labels[angle].toLowerCase()} concept view`;
  img.style.width = 100*w/dw+'%';
  img.style.height = 100*h/dh+'%';
  img.style.left = -100*x/dw+'%';
  img.style.top = -100*y/dh+'%';
  img.loading = lazy ? 'lazy' : 'eager';
  img.decoding = 'async';
  img.src = asset.concept;
  return frame;
 }
 function render(parent, asset) {
  const grid = create('ul', parent, 'angle-grid');
  grid.setAttribute('aria-label', asset.name+' concept angles');
  labels.forEach((label, i) => {
   const li = create('li', grid);
   const b = button(li, 'angle-tile');
   b.setAttribute('aria-label', `Inspect ${asset.name}: ${label}`);
   b.setAttribute('aria-haspopup', 'dialog');
   crop(b, asset, i, true);
   create('span', b, 'angle-caption', label);
   b.addEventListener('click', () => open(asset, i, b));
  });
 }
 function boardLink(parent, asset) {
  const a = create('a', parent, 'angle-board-link', 'Open full board');
  a.href = asset.concept;
  return a;
 }
 let dlg, title, stage, full, picker, closer, current, active, opener;
 function setup() {
  dlg = create('dialog', document.body, 'angle-dialog');
  dlg.setAttribute('aria-labelledby', 'angle-dialog-title');
  const top = create('div', dlg, 'angle-dialog-top');
  title = create('h2', top);
  title.id = 'angle-dialog-title';
  closer = button(top, 'angle-close', 'Close');
  closer.autofocus = true;
  closer.addEventListener('click', () => dlg.close());
  picker = create('div', dlg, 'angle-picker');
  picker.setAttribute('role', 'group');
  picker.setAttribute('aria-label', 'Select concept angle');
  labels.forEach((label, i) => button(picker, 'angle-select', label)
   .addEventListener('click', () => select(i)));
  stage = create('div', dlg, 'angle-stage');
  full = create('a', dlg, 'angle-board-link', 'Open full board');
  dlg.addEventListener('keydown', e => {
   if (e.altKey || e.metaKey || e.ctrlKey || e.shiftKey) return;
   const delta = {ArrowLeft:-1, ArrowRight:1}[e.key];
   if (!delta) return;
   e.preventDefault();
   const next = (active+delta+labels.length)%labels.length;
   select(next);
   picker.children[next].focus();
  });
  dlg.addEventListener('close', () => {
   if (opener?.isConnected && !opener.closest('[hidden]')) opener.focus({preventScroll:true});
  });
 }
 function select(index) {
  active = index;
  picker.querySelectorAll('button').forEach((b,i) => b.setAttribute('aria-pressed', i === active ? 'true' : 'false'));
  stage.replaceChildren();
  crop(stage, current, active, false);
 }
 function open(asset, index, buttonEl) {
  if (!dlg) setup();
  current = asset;
  opener = buttonEl;
  title.textContent = asset.name+' · '+asset.id.replace('/', ' / ');
  full.href = asset.concept;
  select(index);
  if (!dlg.open) dlg.showModal();
 }
 function rowButton(parent, asset) {
  const b = button(parent, 'angle-entry-button', 'Inspect four angles');
  b.setAttribute('aria-haspopup', 'dialog');
  b.addEventListener('click', () => open(asset, 0, b));
 }
 function mountRails() {
  for (const asset of rails) {
   const figures = document.querySelectorAll('#rail-studies figure');
   const figure = [...figures].find(f => f.querySelector(`a[href="${asset.concept}"]`));
   if (!figure || !available(asset)) continue;
   figure.querySelector('a').remove();
   const views = create('div', null, 'angle-rail-views');
   render(views, asset);
   boardLink(views, asset);
   figure.prepend(views);
  }
 }
 return {available, render, boardLink, rowButton, mountRails, close: () => { if (dlg?.open) dlg.close(); }};
})();

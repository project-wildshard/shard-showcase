// UI-12 display only. Callers supply an explicit state and a projected crown.
// Independent of quest flags, engine internals, or minimap integration.
const markers = Object.freeze({
  locked: ['!', 'Quest locked'],
  available: ['!', 'Quest available'],
  turnIn: ['?', 'Quest ready to turn in'],
  done: null,
});
export function createMarker(doc, label, state, {headX, headY}) {
  if (!Object.hasOwn(markers, state)) throw new TypeError('Unknown quest marker state');
  if (!Number.isFinite(headX) || !Number.isFinite(headY)) throw new TypeError('Invalid projection');
  if (!markers[state]) return null;
  const [glyph, hint] = markers[state];
  const root = doc.createElement('div');
  root.className = 'quest-giver-marker';
  root.dataset.state = state;
  root.style.left = headX + 'px';
  root.style.top = headY + 'px';
  root.setAttribute('role','img');
  root.setAttribute('aria-label', label + ': ' + hint);
  for (const [cls, value] of [['name',label], ['symbol',glyph]]) {
    const child = doc.createElement('span');
    child.className = cls; child.textContent = value;
    root.append(child);
  }
  return root;
}

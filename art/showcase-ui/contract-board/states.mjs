export const demoRows = Object.freeze([
  { id: 'scrap-patrol', name: 'Scrap Patrol', level: 1, need: 20,
    goal: 'Down 20 Crate Mites', band: 'COUNT  /  BAND 01',
    scrip: 20, firstTitle: 'Pest Control' },
  { id: 'big-pallet', name: 'Big Pallet', level: 6, band: 'ELITE  /  BAND 02' },
  { id: 'vault-warden', name: 'The Vault Warden', level: 12, band: 'ELITE  /  TRAINING VAULT' },
]);

// Display fixtures only. There is no action reducer, reward grant, or game state.
export const previews = Object.freeze({
  progress: { label: 'In progress', level: 1, count: 8, completed: 0, titles: 0, firstClaimed: false, caption: 'A fresh contract at eight of twenty.' },
  first: { label: 'First claim', level: 1, count: 20, completed: 0, titles: 0, firstClaimed: false, caption: 'Ready for the first claim: 20 Scrip, a wall trophy, and Pest Control.' },
  repeat: { label: 'Repeat claim', level: 1, count: 20, completed: 1, titles: 1, firstClaimed: true, caption: 'Repeat ready: 20 Scrip only. The title remains earned.' },
});
export function describe(row, state) {
  if (state.level < row.level) return { locked: true, status: 'LOCKED', text: 'Opens at LV '+row.level };
  if (row.id !== 'scrap-patrol') return { locked: false, status: 'PREVIEW', text: 'Not authored in this preview' };
  const done = state.count === row.need;
  return {
    locked: false,
    status: done ? (state.firstClaimed ? 'REPEAT READY' : 'FIRST CLAIM READY') : 'IN PROGRESS',
    count: state.count,
    text: row.goal,
    rewards: state.firstClaimed ? [row.scrip+' Scrip'] : [row.scrip+' Scrip','Wall trophy',row.firstTitle],
    firstClaimed: state.firstClaimed,
  };
}

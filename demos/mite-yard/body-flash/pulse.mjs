// Render-only readout on confirmed third-person sword contact. No damage,
// animation, light, screen overlay, or gameplay clock writes.
export const PEAK = .22, END = .075;
export function confirmSwordPulse(event, previous = null) {
  if (event?.weapon !== 'sword' || event?.source !== 'melee' ||
      !Number.isFinite(event.damageDealt) || event.damageDealt <= 0 ||
      !Number.isFinite(event.at) || event.hitId == null) return previous;
  if (previous && (previous.hitId === event.hitId || event.at < previous.at)) return previous;
  return Object.freeze({at:event.at,hitId:event.hitId});
}
export function pulseWeight(pulse, now, flashSetting=1) {
  if (!pulse || !Number.isFinite(now) || !Number.isFinite(flashSetting)) return 0;
  const t=now-pulse.at;
  if (t<0 || t>=END-1e-9) return 0;
  const fade=1-t/END;
  return PEAK*fade*fade*Math.max(0,Math.min(1,flashSetting));
}

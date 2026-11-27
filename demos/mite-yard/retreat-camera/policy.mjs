// Candidate camera-feed filter for one selected Jack's charge tell.
// No targeting, aim, movement, gameplay clocks, or camera writes.
export const RETREAT_HOLD_CAP = .950;

export function holdChargeFraming(state) {
  const {target, armedTarget, kind, startedAt, now, windingUp, stillHeld,
    autoFollow, thirdPersonMelee, sprint, manualLookSinceStart, cleared,
  } = state;
  return !!target && target === armedTarget && kind === 'pallet-charge' &&
    windingUp && stillHeld && autoFollow && thirdPersonMelee && !sprint &&
    !manualLookSinceStart && !cleared && Number.isFinite(startedAt) &&
    Number.isFinite(now) && now >= startedAt && now - startedAt < RETREAT_HOLD_CAP;
}

export function chargeCameraFeed(state, normalFeed) {
  return holdChargeFraming(state)
    ? { ...normalFeed, aimTarget:state.target.pos, aimHeight:state.target.height, flee:0 }
    : normalFeed;
}

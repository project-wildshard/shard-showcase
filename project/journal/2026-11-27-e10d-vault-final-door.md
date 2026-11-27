# E10c/E10d · The last turn into Lockdown

WSC-KIT-008 / WSC-SCENE-006. Close the gap between the prior moving-lift
proof and the existing Lockdown art instead of adding another prop. The
unchanged last-door anchor is at x204, z−64. Place the chamber at
[207.5, −40.5, −43.6] and turn toward increasing world Z. The Room 4
art fits inside D41; its Z bounds start 2.965 m beyond the existing Room
3 art bounds. This is a placement proposal, not an installed Vault.

- Exact Room 3 landing, three center Room 4 plates plus perimeter floor,
  two open bulkheads, and a compact editable steel deck/guard recipe.
- The unchanged open mesh at floor height blocked the path before each
  ring. Lowering it 0.99 m, as in the prior Room 2 test, buried the sill.
- Ten clear legs (five offsets each way) stayed grounded with zero stalls.
  Five sealed approaches stayed grounded before the door and five with
  the throat floor omitted fell. No jump or fallback plane.
- The deck and wall locations can be rebuilt from the recipe without
  preserving the temporary collision JSON, renders, or duplicate GLBs.
  Larger Vault fit, edge cases outside the sampled lane, live hazards and
  phone performance still need separate integration.

[Rebuild](../../demos/native-vault-final-door/README.md) ·
[Test receipt](../layouts/e10c-e10d-vault-final-door-proof.json).

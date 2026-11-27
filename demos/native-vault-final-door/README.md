# Vault Room 3 → Lockdown

The proposed connector turns 90° between the authored Room 3 upper
landing and the existing Room 4 art. It keeps the end of Room 3 in place,
reuses MODULE-021 as each static open doorway, and fits the full Room 4
art within D41. Setting both open modules 0.99 m below the floor lowers
the otherwise blocking round sill, matching the previous Room 2 study.
The assembled bend is about 18.6 m from start to endpoint along the two legs.

```sh
T=/tmp/vault-handoff
B=demos/native-vault-final-door/build.py
WSC_HANDOFF_VALIDATE_ONLY=1 blender -b -t 6 --factory-startup --python-exit-code 1 --python "$B" -- "$T"
WSC_NODE_PROJECT=/path/to/pinned/node/project node --experimental-transform-types demos/native-vault-final-door/sample.mjs "$T"
blender -b -t 8 --factory-startup --python-exit-code 1 --python "$B" -- "$T"
```

Engine 0.1.44 + its Rapier Node package runs the stock 0.38 m player
capsule, without a fallback plane or jump. The five offsets ±0.48 m in
both directions stay grounded and never stall. Reusing the original
sealed door stops all five approaches; removing the throat deck makes
all five fall. The fixture uses exact central plate and
door triangles only for reference; it is not a phone collision budget.

The Room 4 bench opening is opt-in; its canonical sealed art and
exports stay unchanged. No door animation, triggers, encounter, full
chamber traversal, other room fit, native install, or phone test.
See the [receipt](../../project/layouts/e10c-e10d-vault-final-door-proof.json).

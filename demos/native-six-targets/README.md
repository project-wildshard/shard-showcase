# W3a Six Targets: native walk-and-strike rehearsal

The pinned Engine 0.1.44 capsule travels through the actual Range Gate
scenery and six reimported fixture meshes. It walks 64.79 m without an
airborne tick. The chosen route skirts ornamental vegetation at the outer
stands and uses the west aisle between the two rows. Inputs are simulated
stick/yaw and ordinary swing commands; no teleport, height plane, flag
injection or direct contact callback.

The sword row follows Round 5 X −30/−24/−18 at Z 86. The spear row uses the
same X values at Z 104. Only the angled **approach points** are inferred.
The reimported stands face the approach; each fixture foot seats on its
existing ground. The two bracketed rehearsal item rows are separate from
production inventory. Proven on the installed native loadout, timed melee,
and `world/targets` dispatcher, with one flag per correctly reached
fixture. The intended six swings landed in a repeatable order by 22.1 s
including recovery; this is a scripted test, not a target PB. An independent
run rejects four controls: an aimed miss, wrong weapon, duplicate hit,
and a spear line outside the clear bore. Sight rays through the exported
ring centers were also checked independently in Blender, not inferred from
the engine flags. These contact rows do not add an occlusion law.

```sh
T=/tmp/six-targets
D=demos/native-six-targets
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/west-range-scenery/build.py -- --output "$T/donor"
B="$T/donor/range-landscape-editable.blend"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/geometry.py" -- "$T/geometry.json"
node --experimental-transform-types "$D/sample.mjs" "$T/geometry.json" "$T/run.json"
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/geometry.py" -- "$T/geometry.json" "$T/run.json"
```

Use a Node project containing pinned Engine 0.1.44, Format 0.43.0 and the
engine's Rapier dependencies; set `WSC_NODE_PROJECT` if it is outside
the repo. The last command checks line of sight and renders the trace.
Trail lines and checks are annotations, not game UI. Large rebuilds stay
in scratch. No game-world host/install, equipment loan, player animation,
scoring board, persistence, native client, phone review or public game
deployment is part of this rehearsal.

## Range Gate entry extension

The optional `--entry` mode starts outside the original gate at Three
(−36±0.65, 0, 54). It follows the already measured gate center route to
z=79.90, turns into the melee yard, and uses the same native capsule,
fixtures and loadout for the six strikes. The course timer here is a
measurement from the common yard entry point to the final native hit,
not a saved personal best. No collider or visual was added to the real
gate or yard. The temporary closed-gate control tests whether the trace
can incorrectly score while stopped at the gate.

```sh
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/geometry.py" -- --entry "$T/entry-geometry.json"
node --experimental-transform-types "$D/sample.mjs" "$T/entry-geometry.json" "$T/entry-run.json" --entry
blender -b "$B" -t 6 --python-exit-code 1 --python "$D/geometry.py" -- --entry "$T/entry-geometry.json" "$T/entry-run.json"
```

Use the same flags in extraction and rendering. The gate-to-yard image
shows measured trace lines over the unchanged scenery. The entrance
view is a staged eye-height render, not a client screenshot. This
extension is not an equipment loan or drill/records host.

Three offsets finished all six with zero airborne ticks and zero
commanded stalls. The center path covered 96.81 m; final impact was
1,761 ticks from first movement (29.35 s), and all three timed 1,309
ticks from the common yard point to impact (21.82 s). The wall control
stopped at z=61.420 m with no target flags. Original yard-only output
matches the previous receipt; two independent entry traces also match.

`summarize-entry.mjs ENTRY_RUN SCENERY_PARITY SIGHT_JSON RECEIPT`
regenerates `project/layouts/w3a-native-range-entry-proof.json`.

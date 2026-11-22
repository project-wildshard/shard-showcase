# Native Crate Mite calibration

The separate first-person demo proves the fight in a Three.js test yard. This
recipe instead stages the pinned native SDK template and substitutes one
awake Mite for its first blob. It reuses the template's iron sword and stock
player view. It does not copy the template, its asset tree, or the generated
product into Git.

From the repository root with its pinned dependencies installed:

```sh
scratch="$PWD/tmp/mite-native"
mkdir -p "$scratch/home"
node demos/native-mite/prepare.mjs "$scratch/mite-calibration"
HOME="$scratch/home" node_modules/.bin/wildshard build "$scratch/mite-calibration" "$scratch/product/mite-calibration" --folder-only
HOME="$scratch/home" node_modules/.bin/wildshard validate "$scratch/product/mite-calibration"
```

Alternatively use `WSC_NODE_PROJECT=/absolute/path/to/installed-project` with
the same exact SDK 0.4.12 and format 0.43.0. Stage beneath that project's
dependency root when its dependencies are separate from this checkout.

The recipe runs the native skin byte-admission validator, checks all seven
mapped materials (including the cyan eye), publishes content-addressed skin
and GLB bytes into the scratch template, and configures native walk, bite,
hit and die state mappings. The native temperament explicitly binds the bite and overclock abilities;
their unique actor tag avoids inheriting stock template strikes. Separate
turn, sleep and wake clips are available in the rig but not registered as
unsupported native animation states.

After building, run the pinned engine's headless check:

```sh
HOME="$scratch/home" node --experimental-transform-types \
  demos/native-mite/check-native-pursuit.mjs "$scratch/product/mite-calibration"
```

The run must observe walking into range, both named strikes winding up and
landing, and actual player damage. It does not prove native sword hits,
browser graphics, client animation selection, or iPhone performance. This
isolated calibration product is not a game release.

To verify the declared iron sword through the engine's data-cell input path:

```sh
HOME="$scratch/home" node --experimental-transform-types \
  demos/native-mite/check-native-sword.mjs "$scratch/product/mite-calibration"
```

The check places the player at a controlled sword distance, confirms the
actual held slot, and issues three ordinary wire attack presses. It verifies
28 damage on the first strike, death attribution, kill credit, and the
native clip selector for the two Mite abilities and death. Unlike this
server-side check, witnessing the first-person swing needs a native client.

For the 138-triangle tier, pass `--far` after a different empty
`mite-calibration` output directory and build and validate it separately.
Engine 0.1.44 uses format 0.37.1 and has no phone selection for authored
creature skins. These are two products, not an automatic distance switch.

To exercise the actual client asset loader independently of the game renderer:

```sh
node demos/native-mite/stage-client-check.mjs "$scratch/client-check" \
  "$scratch/product/mite-calibration" "$scratch/far-product/mite-calibration"
node_modules/.bin/vite build "$scratch/client-check" --base ./
node_modules/.bin/vite preview "$scratch/client-check"
```

The page must report 386 and 138 triangles, each with seven joints and
eleven sampled clips. This isolated loader check does not start a native
World or validate rendering, touch controls, or iPhone performance.

To compare a stationary player with a delayed sidestep in the native
server simulation:

```sh
HOME="$scratch/home" node --experimental-transform-types \
  demos/native-mite/check-native-dodge.mjs "$scratch/product/mite-calibration"
```

For each attack, the check repeats the same approach from a fresh world,
holds still for 15 ticks after the windup starts, then either stays in
place or moves perpendicular to the recorded lane. It verifies matching
start states, both phase edges, a hit in the control, and unchanged
health through recovery in the sidestep. The reported active durations
are observed server phases, not nominal strike fields. No browser, phone
or live native shard is exercised by this check.

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
HOME="$scratch/home" node_modules/.bin/wildshard build "$scratch/mite-calibration" "$scratch/product/mite-calibration"
HOME="$scratch/home" node_modules/.bin/wildshard validate "$scratch/product/mite-calibration"
```

Alternatively use `WSC_NODE_PROJECT=/absolute/path/to/installed-project` with
the same exact SDK 0.4.12 and format 0.43.0. Stage beneath that project's
dependency root when its dependencies are separate from this checkout.

The recipe runs the native skin byte-admission validator, checks all seven
mapped materials (including the cyan eye), publishes content-addressed skin
and GLB bytes into the scratch template, and configures native walk, bite,
hit and die state mappings. The pinned pursue row selects only one strike;
the overclock clip is mapped but this particular spawn does not select it.
Separate turn, sleep and wake clips remain available in the source rig, but
are not declared as unsupported native animation states. This is not a release
or device benchmark.

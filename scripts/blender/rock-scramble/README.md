# W8b: The Rock’s south scramble

Three fitted planes on the south route, two cedar rest ledges, and a sill
into the original 16 m crown. The North Chimney ladder, cave mouths, rope
bridge, lookout position, and separate Deck A climb are unchanged.

From the art branch, use Blender 4.3.2. Work outside the checkout:

```sh
out=/absolute/scratch/rock
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/west-climb-rock/build.py -- --output "$out/donor"
blender -b -t 6 --factory-startup --python-exit-code 1 \
  --python scripts/blender/rock-scramble/build.py -- \
  "$out/donor/climb-rock-editable.blend" "$out/route" --render
```

The first command validates the tracked donor including previous mesh
signatures. The second removes only the seven original proxy blocks from
its in-memory copy (56 vertices / 42 faces), builds and exports seven
placement-ready nodes, and reimports the GLB to check the deck heights.
Drop `--render` for a geometry-only run. The original blend and base
builder are never changed. If placing the route over an existing scene,
remove those proxy steps before compositing; do not delete the combined
north chimney mesh. No .blend copies, baked scene exports, or test renders
are needed to continue authoring.

Placement follows the archived Round 5 `buildRock` south approach around
X −216, Z 72, not the Deck A practice wall. The summit and lookout
use the original 16 m height and coordinates. The W8b plan supplied the
three-pitch topology; the intermediate landings and angled surfaces are
new art placement, not original measured climb mechanics. `receipt.json`
records coordinates as Three XYZ, including the clearances of the sampled
geometry. The staged faces are not engine traverse rows. No climb mode,
mantle, falling, collision, or shipped shard change is implemented here.

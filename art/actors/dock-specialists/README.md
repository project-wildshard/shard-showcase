# Four original dock specialists

Hook Crane swings a magnetic leader, Kiln Warden moves its shield independently, Breakwater Snare bends its hull and cutters, and Spark Buoy flexes its cage and fins. The single editable Blender lineup and Python builder retain all four rigid armatures. Each export has nine clips with distinct attack and special tracks plus ground, weak and attack sockets. No Fable work or follower variants are included.

Rebuild with `blender -b --factory-startup --python-exit-code 1 --python scripts/blender/dock-specialists/build.py -- /tmp/dock-specialists`. Verify with `python scripts/blender/dock-enemies/verify.py art/actors/dock-specialists specialists`.
